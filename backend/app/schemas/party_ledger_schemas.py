"""Party ledger request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.payments import PAYMENT_CASH, PAYMENT_ONLINE


class CustomerPaymentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    amount = fields.Decimal(required=True, as_string=False)
    notes = fields.String(load_default=None, allow_none=True)
    collection_method = fields.String(
        load_default=PAYMENT_CASH,
        validate=validate.OneOf([PAYMENT_CASH, PAYMENT_ONLINE]),
    )


customer_payment_schema = CustomerPaymentSchema()
