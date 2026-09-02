"""Tour package schemas (BIZ-56)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateTourPackageSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(required=True, validate=validate.Length(min=1, max=40))
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=4000))
    destination = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=160))
    transport_type = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=60))
    duration_days = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1, max=3650))
    base_price = fields.Decimal(required=True, as_string=False)
    gst_percentage = fields.Decimal(load_default=0, as_string=False)
    is_active = fields.Boolean(load_default=True)
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class UpdateTourPackageSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=40))
    name = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=4000))
    destination = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=160))
    transport_type = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=60))
    duration_days = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1, max=3650))
    base_price = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    gst_percentage = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    is_active = fields.Boolean(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class BillTourPackageSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    quantity = fields.Decimal(load_default=1, as_string=False)
    payment_method = fields.String(load_default="cash")
    customer_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=36))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    discount = fields.Decimal(load_default=0, as_string=False)
    reference = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))


create_tour_package_schema = CreateTourPackageSchema()
update_tour_package_schema = UpdateTourPackageSchema()
bill_tour_package_schema = BillTourPackageSchema()
