"""Category request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateCategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(load_default=None, allow_none=True)
    parent_id = fields.String(load_default=None, allow_none=True)


class UpdateCategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    description = fields.String(load_default=None, allow_none=True)
    parent_id = fields.String(load_default=None, allow_none=True)


class StatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    is_active = fields.Boolean(required=True)


create_category_schema = CreateCategorySchema()
update_category_schema = UpdateCategorySchema()
status_schema = StatusSchema()