"""Suggested transport modes for tour packages."""

from __future__ import annotations

BUS = "bus"
CAR = "car"
TRAIN = "train"
FLIGHT = "flight"
VAN = "van"
TEMPO = "tempo"
CRUISE = "cruise"
BOAT = "boat"
BIKE = "bike"
OTHER = "other"

SUGGESTED_TRANSPORT_TYPES: tuple[str, ...] = (
    BUS,
    CAR,
    TRAIN,
    FLIGHT,
    VAN,
    TEMPO,
    CRUISE,
    BOAT,
    BIKE,
)

TRANSPORT_TYPE_LABELS: dict[str, str] = {
    BUS: "Bus",
    CAR: "Car",
    TRAIN: "Train",
    FLIGHT: "Flight",
    VAN: "Van",
    TEMPO: "Tempo Traveller",
    CRUISE: "Cruise",
    BOAT: "Boat",
    BIKE: "Bike / Scooter",
}


def transport_type_label(value: str | None) -> str | None:
    if not value:
        return None
    key = str(value).strip().lower()
    return TRANSPORT_TYPE_LABELS.get(key, str(value).strip())


def normalize_transport_type(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > 60:
        raise ValueError("transport_type must be at most 60 characters")
    lowered = text.lower()
    if lowered in TRANSPORT_TYPE_LABELS:
        return lowered
    return text
