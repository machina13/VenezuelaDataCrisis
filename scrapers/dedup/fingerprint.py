from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime
from typing import Any

FINGERPRINT_VERSION = "v1"


def build_fingerprint(
    event_id: str,
    claim_type: str,
    location_text: str | None,
    description: str,
) -> str:
    return _hash_normalized_parts(
        normalize_for_match(event_id),
        normalize_for_match(claim_type),
        normalize_for_match(location_text or ""),
        normalize_for_match(description)[:300],
    )


def build_event_fingerprint(event: Any) -> str:
    """Build a stable content fingerprint for Event deduplication."""
    return _hash_normalized_parts(
        normalize_for_match(_field(event, "event_type")),
        normalize_for_match(_event_hour(event)),
    )


def build_acopio_fingerprint(center: Any) -> str:
    """Build a stable content fingerprint for AcopioCenter deduplication."""
    return _hash_parts(
        _event_id(center, default=""),
        _field(center, "name"),
        _field(center, "location_text"),
    )


def build_entity_fingerprint(entity: Any) -> str:
    """Dispatch fingerprint generation for supported typed entities."""
    entity_name = type(entity).__name__
    if entity_name == "Event":
        return build_event_fingerprint(entity)
    if entity_name == "AcopioCenter":
        return build_acopio_fingerprint(entity)
    raise TypeError("build_entity_fingerprint only accepts Event or AcopioCenter")


def _hash_parts(*parts: str) -> str:
    return _hash_normalized_parts(*(normalize_for_match(part) for part in parts))


def _hash_normalized_parts(*parts: str) -> str:
    normalized = "|".join(parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def person_block_keys(person: Any) -> list[str]:
    """Return conservative candidate keys for Person review.

    Person records never auto-merge. These keys only group likely candidates
    for later human review and deliberately ignore volatile status fields.
    """
    event_id = _event_id(person)
    keys: list[str] = []
    cedula_hmac = _field(person, "cedula_hmac")
    if cedula_hmac:
        keys.append(f"ced:{event_id}:{cedula_hmac}")

    full_name = _field(person, "full_name")
    if not full_name:
        return keys

    tokens = normalize_for_match(full_name).split()
    if not tokens:
        return keys

    location = _location_key(person)
    keys.append(f"name_loc:{event_id}:{_phonetic_hash(full_name)}:{location}")

    first = tokens[0]
    last = tokens[-1]
    keys.append(f"name:{event_id}:{_phonetic_hash(first)}:{_phonetic_hash(last)}")
    return keys


def acopio_block_keys(center: Any) -> list[str]:
    """Return blocking keys for AcopioCenter records without volatile fields."""
    event_id = _event_id(center)
    name = _field(center, "name")
    location = _location_key(center)
    if not name and not location:
        return [f"acopio:{event_id}"]
    return [f"acopio:{event_id}:{_phonetic_hash(name)}:{location}"]


def _field(obj: Any, field: str) -> str:
    value = getattr(obj, field, None)
    if value is None:
        return ""
    return str(value)


def _event_id(obj: Any, default: str = "unknown_event") -> str:
    return _field(obj, "event_id") or default


def _location_key(obj: Any) -> str:
    for field in ("estado", "last_known_location", "location_text"):
        value = _field(obj, field)
        if value:
            return normalize_for_match(value)
    return "unknown_location"


def _event_hour(event: Any) -> str:
    value = _field(event, "occurred_at") or _field(event, "date_iso")
    if not value:
        return ""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value[:13]
    return parsed.replace(minute=0, second=0, microsecond=0).isoformat()


def _phonetic_hash(value: str) -> str:
    key = _spanish_phonetic_key(value)
    if not key:
        return ""
    return hashlib.sha256(("spa:" + key).encode("utf-8")).hexdigest()[:16]


def _spanish_phonetic_key(value: str) -> str:
    text = normalize_for_match(value)
    text = text.replace("ñ", "ni")
    text = "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    replacements = (
        ("ll", "y"),
        ("ch", "x"),
        ("rr", "r"),
        ("h", ""),
        ("b", "v"),
        ("z", "s"),
        ("c", "s"),
        ("g", "j"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    compact = re.sub(r"[^a-z0-9]+", "", text)
    result: list[str] = []
    previous = ""
    for char in compact:
        if char != previous:
            result.append(char)
        previous = char
    return "".join(result)


def normalize_for_match(text: str | None) -> str:
    if not text:
        return ""
    value = unicodedata.normalize("NFKC", text).lower()
    value = "".join(
        char for char in unicodedata.normalize("NFD", value)
        if unicodedata.category(char) != "Mn"
    )
    value = re.sub(r"[^a-z0-9áéíóúñü\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()
