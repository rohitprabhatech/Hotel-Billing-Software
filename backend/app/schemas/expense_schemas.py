"""Expense request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateExpenseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    category = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=80))
    amount = fields.Decimal(required=True, as_string=False)
    expense_date = fields.Date(required=True, format="%Y-%m-%d")
    notes = fields.String(load_default=None, allow_none=True)


class UpdateExpenseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    category = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=80))
    amount = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    expense_date = fields.Date(load_default=None, allow_none=True, format="%Y-%m-%d")
    notes = fields.String(load_default=None, allow_none=True)


create_expense_schema = CreateExpenseSchema()
update_expense_schema = UpdateExpenseSchema()
