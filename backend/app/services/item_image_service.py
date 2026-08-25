"""Item product images — URL metadata plus optional local files (BIZ-26)."""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse

from flask import current_app, request, url_for
from werkzeug.datastructures import FileStorage

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_WRITE
from app.extensions import db
from app.models.item_image import ItemImage
from app.repositories.item_image_repository import ItemImageRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.item_variant_repository import ItemVariantRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MAX_IMAGES_PER_ITEM = 8
MAGIC_PREFIXES = (
    (b"\xff\xd8\xff", ".jpg"),
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"GIF87a", ".gif"),
    (b"GIF89a", ".gif"),
    (b"RIFF", ".webp"),
)
SAFE_FILENAME = re.compile(r"^[0-9a-f-]{36}\.(jpg|png|webp|gif)$", re.I)


class ItemImageService:
    MODULE = "product_images"

    @staticmethod
    def _require_module(*, write: bool):
        if write:
            require_permission(PERM_ITEMS_WRITE)
        else:
            require_permission(PERM_ITEMS_READ)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, ItemImageService.MODULE)
        return ctx

    @staticmethod
    def _get_item(tenant_id: str, item_id: str):
        item = ItemRepository.get_by_id_and_tenant(item_id.strip(), tenant_id)
        if item is None:
            raise NotFoundError("Item not found")
        return item

    @staticmethod
    def public_url(image: ItemImage) -> str:
        if image.storage_key:
            try:
                return url_for(
                    "api_v1.item_images.serve_item_image",
                    filename=image.storage_key,
                    _external=True,
                )
            except Exception:
                root = (request.url_root if request else "").rstrip("/")
                return f"{root}/api/v1/item-images/files/{image.storage_key}"
        return image.image_url

    @staticmethod
    def serialize(image: ItemImage) -> dict:
        return {
            "id": image.id,
            "item_id": image.item_id,
            "variant_id": image.variant_id,
            "image_url": ItemImageService.public_url(image),
            "alt_text": image.alt_text,
            "sort_order": image.sort_order,
            "is_primary": image.is_primary,
            "is_local_file": bool(image.storage_key),
            "created_at": image.created_at.isoformat() if image.created_at else None,
        }

    @staticmethod
    def _validate_http_url(value: str) -> str:
        text = (value or "").strip()
        parsed = urlparse(text)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValidationError("image_url must be an http(s) URL")
        if len(text) > 500:
            raise ValidationError("image_url is too long")
        return text

    @staticmethod
    def _maybe_primary(tenant_id: str, item_id: str, is_primary: bool, count: int) -> bool:
        if is_primary or count == 0:
            ItemImageRepository.clear_primary(tenant_id, item_id)
            return True
        return False

    @staticmethod
    def list_for_item(item_id: str):
        ctx = ItemImageService._require_module(write=False)
        item = ItemImageService._get_item(ctx.tenant_id, item_id)
        rows = ItemImageRepository.list_by_item(ctx.tenant_id, item.id)
        return [ItemImageService.serialize(row) for row in rows]

    @staticmethod
    def create_from_url(item_id: str, *, image_url, variant_id=None, alt_text=None, is_primary=False):
        ctx = ItemImageService._require_module(write=True)
        item = ItemImageService._get_item(ctx.tenant_id, item_id)
        url = ItemImageService._validate_http_url(image_url)
        if ItemImageRepository.count_for_item(ctx.tenant_id, item.id) >= MAX_IMAGES_PER_ITEM:
            raise ValidationError(f"Maximum {MAX_IMAGES_PER_ITEM} images per item")
        vid = (variant_id or "").strip() or None
        if vid:
            variant = ItemVariantRepository.get_by_id(ctx.tenant_id, vid)
            if variant is None or variant.item_id != item.id:
                raise ValidationError("variant_id does not belong to this item")
        count = ItemImageRepository.count_for_item(ctx.tenant_id, item.id)
        primary = ItemImageService._maybe_primary(ctx.tenant_id, item.id, bool(is_primary), count)
        image = ItemImage(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            variant_id=vid,
            image_url=url,
            storage_key=None,
            alt_text=(alt_text or "").strip() or None,
            sort_order=ItemImageRepository.next_sort_order(ctx.tenant_id, item.id),
            is_primary=primary,
        )
        ItemImageRepository.add(image)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_ITEM_IMAGE",
            entity_type="ITEM_IMAGE",
            entity_id=image.id,
            new_data={"item_id": item.id, "image_url": url, "is_primary": primary},
        )
        db.session.commit()
        return ItemImageService.serialize(image)

    @staticmethod
    def upload(item_id: str, file: FileStorage | None, *, variant_id=None, alt_text=None, is_primary=False):
        ctx = ItemImageService._require_module(write=True)
        item = ItemImageService._get_item(ctx.tenant_id, item_id)
        if file is None or not file.filename:
            raise ValidationError("Image file is required")
        if ItemImageRepository.count_for_item(ctx.tenant_id, item.id) >= MAX_IMAGES_PER_ITEM:
            raise ValidationError(f"Maximum {MAX_IMAGES_PER_ITEM} images per item")

        payload = file.read()
        max_bytes = int(current_app.config.get("MAX_ITEM_IMAGE_BYTES", 2 * 1024 * 1024))
        if not payload:
            raise ValidationError("Image file is empty")
        if len(payload) > max_bytes:
            raise ValidationError("Image file is too large (max 2 MB)")

        ext = None
        for magic, suffix in MAGIC_PREFIXES:
            if payload.startswith(magic):
                if suffix == ".webp" and (len(payload) < 12 or payload[8:12] != b"WEBP"):
                    continue
                ext = suffix
                break
        if ext is None:
            raise ValidationError("Only JPEG, PNG, WEBP, and GIF images are allowed")

        vid = (variant_id or "").strip() or None
        if vid:
            variant = ItemVariantRepository.get_by_id(ctx.tenant_id, vid)
            if variant is None or variant.item_id != item.id:
                raise ValidationError("variant_id does not belong to this item")

        folder = current_app.config.get("ITEM_IMAGE_UPLOAD_DIR")
        os.makedirs(folder, exist_ok=True)
        storage_key = f"{new_uuid()}{ext}"
        path = os.path.join(folder, storage_key)
        with open(path, "wb") as handle:
            handle.write(payload)

        count = ItemImageRepository.count_for_item(ctx.tenant_id, item.id)
        primary = ItemImageService._maybe_primary(ctx.tenant_id, item.id, bool(is_primary), count)
        placeholder_url = f"/api/v1/item-images/files/{storage_key}"
        image = ItemImage(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            variant_id=vid,
            image_url=placeholder_url,
            storage_key=storage_key,
            alt_text=(alt_text or "").strip() or None,
            sort_order=ItemImageRepository.next_sort_order(ctx.tenant_id, item.id),
            is_primary=primary,
        )
        ItemImageRepository.add(image)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPLOAD_ITEM_IMAGE",
            entity_type="ITEM_IMAGE",
            entity_id=image.id,
            new_data={"item_id": item.id, "storage_key": storage_key, "is_primary": primary},
        )
        db.session.commit()
        return ItemImageService.serialize(image)

    @staticmethod
    def delete(item_id: str, image_id: str):
        ctx = ItemImageService._require_module(write=True)
        item = ItemImageService._get_item(ctx.tenant_id, item_id)
        image = ItemImageRepository.get_by_id(ctx.tenant_id, image_id)
        if image is None or image.item_id != item.id:
            raise NotFoundError("Image not found")
        storage_key = image.storage_key
        was_primary = image.is_primary
        payload = ItemImageService.serialize(image)
        ItemImageRepository.delete(image)
        if was_primary:
            remaining = ItemImageRepository.list_by_item(ctx.tenant_id, item.id)
            if remaining:
                remaining[0].is_primary = True
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_ITEM_IMAGE",
            entity_type="ITEM_IMAGE",
            entity_id=image_id,
            old_data=payload,
        )
        db.session.commit()
        if storage_key:
            path = os.path.join(current_app.config.get("ITEM_IMAGE_UPLOAD_DIR"), storage_key)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        return payload

    @staticmethod
    def resolve_file_path(filename: str) -> str:
        if not filename or not SAFE_FILENAME.match(filename):
            raise NotFoundError("Image not found")
        folder = current_app.config.get("ITEM_IMAGE_UPLOAD_DIR")
        path = os.path.join(folder, filename)
        if not os.path.isfile(path):
            raise NotFoundError("Image not found")
        return path
