from types import SimpleNamespace

from scrapers.dedup.fingerprint import person_block_keys


def test_person_with_cedula_hmac_generates_cedula_key() -> None:
    person = SimpleNamespace(
        event_id="evt-1",
        cedula_hmac="abc123",
        full_name="Maria Perez",
        last_known_location="Zulia",
    )

    assert "ced:evt-1:abc123" in person_block_keys(person)


def test_person_without_cedula_hmac_does_not_generate_cedula_key() -> None:
    person = SimpleNamespace(
        event_id="evt-1",
        cedula_hmac=None,
        full_name="Maria Perez",
        last_known_location="Zulia",
    )

    assert all(not key.startswith("ced:") for key in person_block_keys(person))


def test_status_does_not_change_person_block_keys() -> None:
    base = SimpleNamespace(
        event_id="evt-1",
        cedula_hmac=None,
        full_name="Maria Perez",
        last_known_location="Zulia",
        status="missing",
    )
    changed = SimpleNamespace(
        event_id="evt-1",
        cedula_hmac=None,
        full_name="Maria Perez",
        last_known_location="Zulia",
        status="found",
    )

    assert person_block_keys(base) == person_block_keys(changed)


def test_similar_names_produce_stable_phonetic_keys() -> None:
    first = SimpleNamespace(event_id="evt-1", full_name="Jose Perez", estado="Lara")
    second = SimpleNamespace(event_id="evt-1", full_name="José Pérez", estado="Lara")

    assert person_block_keys(first) == person_block_keys(second)


def test_event_id_changes_person_block_keys() -> None:
    first = SimpleNamespace(event_id="evt-1", full_name="Maria Perez", estado="Zulia")
    second = SimpleNamespace(event_id="evt-2", full_name="Maria Perez", estado="Zulia")

    assert person_block_keys(first) != person_block_keys(second)
