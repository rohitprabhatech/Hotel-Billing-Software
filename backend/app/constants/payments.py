"""Controlled payment method values for bills."""

PAYMENT_CASH = "cash"
PAYMENT_ONLINE = "online"
PAYMENT_CREDIT = "credit"
ALLOWED_PAYMENT_METHODS = frozenset({PAYMENT_CASH, PAYMENT_ONLINE, PAYMENT_CREDIT})
DEFAULT_PAYMENT_METHOD = PAYMENT_CASH


def normalize_payment_method(value) -> str:
    method = (str(value).strip().lower() if value is not None else "")
    if method not in ALLOWED_PAYMENT_METHODS:
        raise ValueError("Payment method must be cash, online, or credit")
    return method


def payment_method_label(value: str | None) -> str:
    method = (value or DEFAULT_PAYMENT_METHOD).strip().lower()
    if method == PAYMENT_ONLINE:
        return "Online"
    if method == PAYMENT_CREDIT:
        return "Credit"
    return "Cash"
