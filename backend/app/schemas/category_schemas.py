"""Category request schemas."""

from marshmallow import EXCLUDE, Schema, fields, pre_load, validate


def _normalize_parent_fields(data):
    """Accept parent_id or parent_category_id; empty string becomes null (root)."""
    if not isinstance(data, dict):
        return data
    normalized = dict(data)
    if "parent_id" not in normalized and "parent_category_id" in normalized:
        normalized["parent_id"] = normalized.get("parent_category_id")
    if "parent_id" in normalized and normalized["parent_id"] == "":
        normalized["parent_id"] = None
    return normalized


class CreateCategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(load_default=None, allow_none=True)
    parent_id = fields.String(load_default=None, allow_none=True)

    @pre_load
    def normalize_parent(self, data, **kwargs):
        return _normalize_parent_fields(data)


class UpdateCategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    description = fields.String(load_default=None, allow_none=True)
    parent_id = fields.String(load_default=None, allow_none=True)

    @pre_load
    def normalize_parent(self, data, **kwargs):
        return _normalize_parent_fields(data)


class StatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    is_active = fields.Boolean(required=True)


create_category_schema = CreateCategorySchema()
update_category_schema = UpdateCategorySchema()
status_schema = StatusSchema()