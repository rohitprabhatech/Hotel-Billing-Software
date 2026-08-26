"""Travel agent and commission schemas (BIZ-59)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.models.travel_agent import ALLOWED_COMMISSION_STATUSES


class CreateTravelAgentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(required=True, validate=validate.Length(min=1, max=40))
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    email = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=160))
    commission_percent = fields.Decimal(load_default=0, as_string=False)
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    is_active = fields.Boolean(load_default=True)


class UpdateTravelAgentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=40))
    name = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=120))
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    email = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=160))
    commission_percent = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    is_active = fields.Boolean(load_default=None, allow_none=True)


class CreateCommissionEntrySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    booking_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    agent_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=36))
    commission_percent = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class UpdateCommissionStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True,
        validate=validate.OneOf(sorted(ALLOWED_COMMISSION_STATUSES)),
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


create_travel_agent_schema = CreateTravelAgentSchema()
update_travel_agent_schema = UpdateTravelAgentSchema()
create_commission_entry_schema = CreateCommissionEntrySchema()
update_commission_status_schema = UpdateCommissionStatusSchema()
