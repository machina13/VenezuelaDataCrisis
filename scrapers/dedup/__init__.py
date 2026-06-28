from scrapers.dedup.deduplicator import (
    deduplicate_by_fingerprint,
    deduplicate_typed_entities,
)
from scrapers.dedup.fingerprint import (
    FINGERPRINT_VERSION,
    acopio_block_keys,
    build_acopio_fingerprint,
    build_entity_fingerprint,
    build_event_fingerprint,
    build_fingerprint,
    person_block_keys,
)
from scrapers.dedup.specs import ACOPIO_SPEC, EVENT_SPEC, PERSON_SPEC, SPECS, DedupSpec

__all__ = [
    "FINGERPRINT_VERSION",
    "DedupSpec",
    "EVENT_SPEC",
    "ACOPIO_SPEC",
    "PERSON_SPEC",
    "SPECS",
    "build_fingerprint",
    "build_event_fingerprint",
    "build_acopio_fingerprint",
    "build_entity_fingerprint",
    "person_block_keys",
    "acopio_block_keys",
    "deduplicate_by_fingerprint",
    "deduplicate_typed_entities",
]
