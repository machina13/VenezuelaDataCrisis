from scrapers.adapters import RawContent
from scrapers.models import AcopioCenter, Event, Person
from scrapers.parsers import ParserProtocol
from scrapers.parsers.base import ParsedEntity


class DummyParser:
    def parse(self, raw: RawContent) -> list[ParsedEntity]:
        if isinstance(raw, bytes):
            raw = raw.decode()
        if isinstance(raw, dict):
            raw = str(raw.get("description", "synthetic event"))
        return [
            Person(full_name="Ana Perez", fuente="synthetic_source"),
            AcopioCenter(name="Centro Demo", location_text="Caracas", fuente="synthetic_source"),
            Event(event_type="demo", description=str(raw), fuente="synthetic_source"),
        ]


def test_parser_protocol_accepts_matching_parse_signature() -> None:
    parser: ParserProtocol = DummyParser()

    parsed = parser.parse("synthetic event")

    assert [type(entity) for entity in parsed] == [Person, AcopioCenter, Event]
    assert isinstance(parsed[2], Event)
    assert parsed[2].description == "synthetic event"
