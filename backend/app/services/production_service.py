"""Bakery production runs — consume ingredients, increase finished goods (BIZ-40)."""

from datetime import date, timedelta
from decimal import Decimal

from app.constants.permissions import PERM_PRODUCTION_READ, PERM_PRODUCTION_WRITE
from app.extensions import db
from app.models.production_run import ProductionRun, ProductionRunItem
from app.repositories.item_repository import ItemRepository
from app.repositories.production_run_repository import ProductionRunRepository
from app.repositories.recipe_repository import RecipeRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.notification_service import NotificationService
from app.services.stock_movement_service import StockMovementService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import qty
from app.utils.periods import local_now, parse_date
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "production"


class ProductionService:
    @staticmethod
    def _require(*, write: bool = False):
        require_permission(PERM_PRODUCTION_WRITE if write else PERM_PRODUCTION_READ)
        ctx = require_request_context()
        from app.repositories.tenant_repository import TenantRepository

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None or not ModuleService.is_enabled_for_tenant(tenant, MODULE):
            raise ForbiddenError("Production module is not enabled for this business")
        return ctx

    @staticmethod
    def _tenant_tz() -> str:
        ctx = require_request_context()
        return getattr(ctx, "tenant_timezone", None) or "Asia/Kolkata"

    @staticmethod
    def _parse_filter_date(value: str | None) -> date | None:
        if value is None or not str(value).strip():
            return None
        try:
            return parse_date(str(value).strip(), ProductionService._tenant_tz()).date()
        except ValueError as exc:
            raise ValidationError("Dates must be YYYY-MM-DD") from exc

    @staticmethod
    def list_productions(
        *,
        finished_item_id=None,
        from_date=None,
        to_date=None,
        page=1,
        per_page=50,
    ):
        ctx = ProductionService._require(write=False)
        date_from = ProductionService._parse_filter_date(from_date)
        date_to = ProductionService._parse_filter_date(to_date)
        if date_from and date_to and date_from > date_to:
            raise ValidationError("from date cannot be after to date")
        rows, total = ProductionRunRepository.list_by_tenant(
            ctx.tenant_id,
            finished_item_id=finished_item_id,
            from_date=date_from,
            to_date=date_to,
            page=page,
            per_page=per_page,
        )
        return (
            [ProductionService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_production(run_id: str):
        ctx = ProductionService._require(write=False)
        row = ProductionRunRepository.get_by_id_and_tenant(run_id, ctx.tenant_id)
        if row is None:
            raise NotFoundError("Production run not found")
        return ProductionService.serialize(row)

    @staticmethod
    def create_production(
        *,
        recipe_id: str,
        quantity,
        notes: str | None = None,
        run_date=None,
        expiry_date=None,
        batch_code: str | None = None,
    ):
        ctx = ProductionService._require(write=True)
        recipe_key = (recipe_id or "").strip()
        if not recipe_key:
            raise ValidationError("recipe_id is required")
        produced = qty(quantity)
        if produced <= 0:
            raise ValidationError("Quantity must be greater than zero")

        recipe = RecipeRepository.get_by_id_and_tenant(recipe_key, ctx.tenant_id)
        if recipe is None or not recipe.is_active:
            raise ValidationError("Recipe not found or inactive")
        if not recipe.ingredients:
            raise ValidationError("Recipe has no ingredients")

        yield_qty = qty(recipe.yield_quantity)
        if yield_qty <= 0:
            raise ValidationError("Recipe yield must be greater than zero")

        finished = ItemRepository.lock_by_id_and_tenant(recipe.menu_item_id, ctx.tenant_id)
        if finished is None or not finished.is_active:
            raise ValidationError("Finished goods item not found or inactive")
        if finished.stock_quantity is None:
            raise ValidationError(
                "Finished goods item must track stock. Set an opening stock quantity first."
            )

        tracks_batches = bool(getattr(finished, "tracks_batches", False))
        parsed_expiry = None
        if tracks_batches:
            if expiry_date is None:
                raise ValidationError(
                    "expiry_date is required when the finished goods item tracks batches"
                )
            parsed_expiry = expiry_date
            if isinstance(parsed_expiry, str):
                parsed_expiry = parse_date(parsed_expiry, ProductionService._tenant_tz()).date()

        # Scale BOM: produce `produced` units given recipe yield.
        scale = produced / yield_qty
        needed: list[tuple] = []
        for line in recipe.ingredients:
            amount = qty(qty(line.quantity) * scale)
            if amount <= 0:
                continue
            needed.append((line, amount))
        if not needed:
            raise ValidationError("Scaled ingredient quantities are zero")

        transitions: list[tuple] = []
        locked_ingredients = {}
        for line, amount in needed:
            item = ItemRepository.lock_by_id_and_tenant(line.ingredient_item_id, ctx.tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Ingredient not found or inactive: {line.ingredient_name}")
            if item.stock_quantity is None:
                raise ValidationError(
                    f"Ingredient '{item.name}' does not track stock. Enable stock tracking first."
                )
            previous = Decimal(item.stock_quantity)
            new_stock = previous - amount
            if new_stock < 0:
                raise ValidationError(
                    f"Insufficient stock for {item.name}. "
                    f"Available: {float(previous):g}, required: {float(amount):g}."
                )
            locked_ingredients[item.id] = (item, previous, amount, new_stock, line)

        tz = ProductionService._tenant_tz()
        if run_date:
            entry_date = run_date
            if isinstance(entry_date, str):
                entry_date = parse_date(entry_date, tz).date()
        else:
            entry_date = local_now(tz).date()

        run_id = new_uuid()
        _, run_number = ProductionRunRepository.allocate_number(ctx.tenant_id)
        notes_text = (notes or "").strip() or None

        ingredient_rows = []
        for item_id, (item, previous, amount, new_stock, line) in locked_ingredients.items():
            movement = StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                delta=-amount,
                quantity_after=new_stock,
                source="PRODUCTION",
                reason=f"Production {run_number} ingredient",
                reference_type="PRODUCTION",
                reference_id=run_id,
                created_by=ctx.user_id,
            )
            item.stock_quantity = new_stock
            transitions.append((item, previous, new_stock))
            ingredient_rows.append(
                ProductionRunItem(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    production_run_id=run_id,
                    item_id=item.id,
                    item_name=item.name,
                    quantity=amount,
                    uom=line.uom or item.uom,
                    sort_order=line.sort_order or 0,
                    stock_movement_id=movement.id,
                )
            )

        from app.services.batch_service import BatchService, DEFAULT_EXPIRY_WARNING_DAYS

        finished_batch = None
        if tracks_batches:
            code = (batch_code or "").strip() or run_number
            finished_batch, fg_previous, fg_new, fg_movement_id = BatchService.create_batch_uncommitted(
                tenant_id=ctx.tenant_id,
                item=finished,
                quantity=produced,
                expiry_date=parsed_expiry,
                batch_code=code,
                created_by=ctx.user_id,
                reason=f"Production {run_number} finished goods",
                movement_source="PRODUCTION",
                reference_type="PRODUCTION",
                reference_id=run_id,
            )
            transitions.append((finished, fg_previous, fg_new))
            if parsed_expiry <= date.today() + timedelta(days=DEFAULT_EXPIRY_WARNING_DAYS):
                BatchService._notify_expiring(ctx.tenant_id, [finished_batch])
        else:
            fg_previous = Decimal(finished.stock_quantity)
            fg_new = fg_previous + produced
            fg_movement = StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=finished.id,
                delta=produced,
                quantity_after=fg_new,
                source="PRODUCTION",
                reason=f"Production {run_number} finished goods",
                reference_type="PRODUCTION",
                reference_id=run_id,
                created_by=ctx.user_id,
            )
            finished.stock_quantity = fg_new
            fg_movement_id = fg_movement.id
            transitions.append((finished, fg_previous, fg_new))

        run = ProductionRun(
            id=run_id,
            tenant_id=ctx.tenant_id,
            run_number=run_number,
            recipe_id=recipe.id,
            finished_item_id=finished.id,
            finished_item_name=finished.name,
            quantity=produced,
            notes=notes_text,
            run_date=entry_date,
            finished_stock_movement_id=fg_movement_id,
            created_by=ctx.user_id,
        )
        ProductionRunRepository.add(run)
        for row in sorted(ingredient_rows, key=lambda r: r.sort_order):
            ProductionRunRepository.add_item(row)
        run.items = ingredient_rows

        serialized = ProductionService.serialize(run)
        if finished_batch is not None:
            serialized["finished_batch_id"] = finished_batch.id
            serialized["finished_batch_code"] = finished_batch.batch_code
            serialized["expiry_date"] = (
                finished_batch.expiry_date.isoformat() if finished_batch.expiry_date else None
            )
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_PRODUCTION",
            entity_type="PRODUCTION",
            entity_id=run.id,
            new_data=serialized,
        )
        db.session.commit()

        for item, previous, new_stock in transitions:
            NotificationService.notify_stock_transition(
                tenant_id=ctx.tenant_id,
                item=item,
                previous=previous,
                new_stock=new_stock,
            )
        return serialized

    @staticmethod
    def serialize(run: ProductionRun) -> dict:
        return {
            "id": run.id,
            "run_number": run.run_number,
            "recipe_id": run.recipe_id,
            "finished_item_id": run.finished_item_id,
            "finished_item_name": run.finished_item_name,
            "quantity": float(run.quantity),
            "notes": run.notes,
            "run_date": run.run_date.isoformat() if run.run_date else None,
            "finished_stock_movement_id": run.finished_stock_movement_id,
            "created_by": run.created_by,
            "created_by_name": run.creator.name if run.creator else None,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "items": [
                {
                    "id": row.id,
                    "item_id": row.item_id,
                    "item_name": row.item_name,
                    "quantity": float(row.quantity),
                    "uom": row.uom,
                    "sort_order": row.sort_order,
                    "stock_movement_id": row.stock_movement_id,
                }
                for row in (run.items or [])
            ],
        }
