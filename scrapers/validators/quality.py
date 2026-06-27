from __future__ import annotations

from typing import Any

from scrapers.models import AcopioCenter, Event, Person
from scrapers.sanitizers.pii_detector import detect_pii

_TIER_BONUS = {
    "A": 0.20,
    "B": 0.15,
    "C": 0.10,
    "D": 0.05,
}


def assert_sanitized(text: str) -> bool:
    return len(detect_pii(text)) == 0


def confidence_from_tier(tier: str) -> float:
    return {
        "A": 0.90,
        "B": 0.75,
        "C": 0.60,
        "D": 0.35,
        "E": 0.15,
    }.get((tier or "").upper(), 0.10)


def confidence_score(entity: Person | AcopioCenter | Event) -> float:
    """Return a 0.0-1.0 confidence score from completeness + source tier.

    Person formula:
    full_name +0.25, cedula_hmac +0.25, last_known_location +0.20,
    explicitly supplied status +0.10, trust_tier A/B/C/D +0.20/+0.15/+0.10/+0.05.
    Example: a Person with full_name, cedula_hmac, location, explicit status
    and tier A scores 1.000.

    AcopioCenter formula:
    name +0.25, location_text +0.25, coordinates +0.20, needs +0.10,
    trust_tier A/B/C/D +0.20/+0.15/+0.10/+0.05.

    Event formula:
    event_type +0.20, description +0.25, location_text +0.20,
    date_iso +0.15, trust_tier A/B/C/D +0.20/+0.15/+0.10/+0.05.
    """
    if isinstance(entity, Person):
        score = 0.0
        score += 0.25 if _has_value(entity, "full_name") else 0.0
        score += 0.25 if _has_value(entity, "cedula_hmac") else 0.0
        score += 0.20 if _has_value(entity, "last_known_location") else 0.0
        score += 0.10 if _field_was_supplied(entity, "status") and _has_value(entity, "status") else 0.0
        score += _tier_bonus(entity)
        return _cap(score)

    if isinstance(entity, AcopioCenter):
        score = 0.0
        score += 0.25 if _has_value(entity, "name") else 0.0
        score += 0.25 if _has_value(entity, "location_text") else 0.0
        score += 0.20 if _has_value(entity, "coordinates") else 0.0
        score += 0.10 if _has_value(entity, "needs") else 0.0
        score += _tier_bonus(entity)
        return _cap(score)

    if isinstance(entity, Event):
        score = 0.0
        score += 0.20 if _has_value(entity, "event_type") else 0.0
        score += 0.25 if _has_value(entity, "description") else 0.0
        score += 0.20 if _has_value(entity, "location_text") else 0.0
        score += 0.15 if _has_value(entity, "date_iso") else 0.0
        score += _tier_bonus(entity)
        return _cap(score)

    raise TypeError("confidence_score only accepts Person, AcopioCenter, or Event")


def _has_value(entity: Any, field_name: str) -> bool:
    value = getattr(entity, field_name, None)
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (dict, list, set, tuple)):
        return bool(value)
    return True


def _field_was_supplied(entity: Any, field_name: str) -> bool:
    return field_name in getattr(entity, "model_fields_set", set())


def _tier_bonus(entity: Any) -> float:
    tier = str(getattr(entity, "trust_tier", "D") or "D").upper()
    return _TIER_BONUS.get(tier, _TIER_BONUS["D"])


def _cap(score: float) -> float:
    return round(min(max(score, 0.0), 1.0), 3)
