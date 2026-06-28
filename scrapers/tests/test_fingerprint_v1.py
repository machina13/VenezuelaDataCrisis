from types import SimpleNamespace

from scrapers.dedup.fingerprint import build_acopio_fingerprint, build_event_fingerprint


def test_event_fingerprint_ignores_volatile_fields() -> None:
    first = SimpleNamespace(
        event_type="earthquake",
        date_iso="2026-06-28T10:15:00Z",
        description="Reporte inicial",
        status="active",
        magnitude=5.0,
    )
    second = SimpleNamespace(
        event_type="earthquake",
        date_iso="2026-06-28T10:45:00Z",
        description="Reporte corregido",
        status="closed",
        magnitude=6.2,
    )

    assert build_event_fingerprint(first) == build_event_fingerprint(second)


def test_event_fingerprint_changes_by_hour() -> None:
    first = SimpleNamespace(event_type="earthquake", date_iso="2026-06-28T10:59:00Z")
    second = SimpleNamespace(event_type="earthquake", date_iso="2026-06-28T11:00:00Z")

    assert build_event_fingerprint(first) != build_event_fingerprint(second)


def test_acopio_fingerprint_ignores_volatile_fields() -> None:
    first = SimpleNamespace(
        event_id="evt-1",
        name="Centro de Acopio Central",
        location_text="Maracaibo, Zulia",
        needs=["agua"],
        active=True,
        status="open",
        contacto="+58 000",
    )
    second = SimpleNamespace(
        event_id="evt-1",
        name="Centro de Acopio Central",
        location_text="Maracaibo, Zulia",
        needs=["comida"],
        active=False,
        status="closed",
        contacto="+58 111",
    )

    assert build_acopio_fingerprint(first) == build_acopio_fingerprint(second)
