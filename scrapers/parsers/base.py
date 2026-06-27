from __future__ import annotations

from typing import Protocol

from scrapers.adapters import RawContent
from scrapers.models import AcopioCenter, Event, Person


ParsedEntity = Person | AcopioCenter | Event


class ParserProtocol(Protocol):
    def parse(self, raw: RawContent) -> list[ParsedEntity]:
        ...
