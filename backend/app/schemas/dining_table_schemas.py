"""Dining table request schemas (BIZ-12)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.tables import ALLOWED_TABLE_STATUSES


class CreateDiningTableSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(required=True, validate=validate.Length(min=1, max=32))
    section = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    capacity = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1, max=999))


class UpdateDiningTableSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(load_default=None, validate=validate.Length(min=1, max=32))
    section = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    capacity = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1, max=999))


class DiningTableStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(required=True, validate=validate.OneOf(sorted(ALLOWED_TABLE_STATUSES)))


class MergeDiningTablesSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    primary_table_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    secondary_table_ids = fields.List(
        fields.String(validate=validate.Length(min=1, max=36)),
        required=True,
        validate=validate.Length(min=1, max=20),
    )


class UnmergeDiningTablesSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    primary_table_id = fields.String(required=True, validate=validate.Length(min=1, max=36))


create_dining_table_schema = CreateDiningTableSchema()
update_dining_table_schema = UpdateDiningTableSchema()
dining_table_status_schema = DiningTableStatusSchema()
merge_dining_tables_schema = MergeDiningTablesSchema()
unmerge_dining_tables_schema = UnmergeDiningTablesSchema()
