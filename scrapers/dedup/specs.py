from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from scrapers.dedup.fingerprint import (
    acopio_block_keys,
    build_acopio_fingerprint,
    build_event_fingerprint,
    person_block_keys,
)


@dataclass(frozen=True)
class DedupSpec:
    version: str
    auto_merge: bool
    fingerprint_fn: Callable[[Any], str] | None = None
    blocking_fn: Callable[[Any], list[str]] | None = None
    score_fn: Callable[[Any, Any], float] | None = None


EVENT_SPEC = DedupSpec(
    version="evt.v1",
    auto_merge=True,
    fingerprint_fn=build_event_fingerprint,
)
ACOPIO_SPEC = DedupSpec(
    version="acopio.v1",
    auto_merge=True,
    fingerprint_fn=build_acopio_fingerprint,
    blocking_fn=acopio_block_keys,
)
PERSON_SPEC = DedupSpec(
    version="person.v3",
    auto_merge=False,
    fingerprint_fn=None,
    blocking_fn=person_block_keys,
    score_fn=None,
)

SPECS = {
    "Event": EVENT_SPEC,
    "AcopioCenter": ACOPIO_SPEC,
    "Person": PERSON_SPEC,
}
