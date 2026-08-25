"""Item image HTTP controller (BIZ-26)."""

from flask import request, send_file

from app.schemas.item_image_schemas import create_item_image_schema
from app.services.item_image_service import ItemImageService
from app.utils.responses import success_response


def list_item_images(item_id: str):
    return success_response(data=ItemImageService.list_for_item(item_id))


def create_item_image(item_id: str):
    payload = create_item_image_schema.load(request.get_json() or {})
    data = ItemImageService.create_from_url(
        item_id,
        image_url=payload["image_url"],
        variant_id=payload.get("variant_id"),
        alt_text=payload.get("alt_text"),
        is_primary=payload.get("is_primary", False),
    )
    return success_response(data=data, status_code=201)


def upload_item_image(item_id: str):
    file = request.files.get("file") or request.files.get("image")
    data = ItemImageService.upload(
        item_id,
        file,
        variant_id=request.form.get("variant_id"),
        alt_text=request.form.get("alt_text"),
        is_primary=str(request.form.get("is_primary", "")).lower() in {"1", "true", "yes"},
    )
    return success_response(data=data, status_code=201)


def delete_item_image(item_id: str, image_id: str):
    return success_response(data=ItemImageService.delete(item_id, image_id))


def serve_item_image(filename: str):
    path = ItemImageService.resolve_file_path(filename)
    return send_file(path)
