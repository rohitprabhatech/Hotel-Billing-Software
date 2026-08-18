"""Master Admin request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class RejectRegistrationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    reason = fields.String(required=True, validate=validate.Length(min=8, max=2000))


class UpdateTrialSettingsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    trial_enabled = fields.Boolean(required=True)
    trial_days = fields.Integer(required=True, validate=validate.Range(min=1, max=365))
    expiry_warning_days = fields.Integer(
        allow_none=True, load_default=None, validate=validate.Range(min=1, max=30)
    )


class PlanWriteSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(load_default="", validate=validate.Length(max=2000))
    price = fields.Decimal(required=True, as_string=False)
    billing_cycle = fields.String(
        load_default="MONTHLY",
        validate=validate.OneOf(["MONTHLY", "YEARLY"]),
    )
    trial_eligible = fields.Boolean(load_default=True)
    is_public = fields.Boolean(load_default=True)
    is_active = fields.Boolean(load_default=True)
    display_order = fields.Integer(load_default=0, validate=validate.Range(min=0, max=9999))
    features = fields.Raw(load_default=list)


class PlanUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(validate=validate.Length(min=1, max=120))
    description = fields.String(validate=validate.Length(max=2000))
    price = fields.Decimal(as_string=False)
    billing_cycle = fields.String(validate=validate.OneOf(["MONTHLY", "YEARLY"]))
    trial_eligible = fields.Boolean()
    is_public = fields.Boolean()
    is_active = fields.Boolean()
    display_order = fields.Integer(validate=validate.Range(min=0, max=9999))
    features = fields.Raw()


class PlanStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    is_active = fields.Boolean(required=True)


class AssignPlanSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    plan_id = fields.String(required=True, validate=validate.Length(min=36, max=36))
    days = fields.Integer(allow_none=True, load_default=None, validate=validate.Range(min=1, max=365))


class DurationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    days = fields.Integer(required=True, validate=validate.Range(min=1, max=365))


class RenewSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    days = fields.Integer(required=True, validate=validate.Range(min=1, max=365))
    plan_id = fields.String(
        allow_none=True, load_default=None, validate=validate.Length(min=36, max=36)
    )


reject_registration_schema = RejectRegistrationSchema()
update_trial_settings_schema = UpdateTrialSettingsSchema()
plan_write_schema = PlanWriteSchema()
plan_update_schema = PlanUpdateSchema()
plan_status_schema = PlanStatusSchema()
assign_plan_schema = AssignPlanSchema()
duration_schema = DurationSchema()
renew_schema = RenewSchema()
