from scrapers.dedup.specs import ACOPIO_SPEC, EVENT_SPEC, PERSON_SPEC, SPECS


def test_dedup_spec_versions() -> None:
    assert EVENT_SPEC.version == "evt.v1"
    assert ACOPIO_SPEC.version == "acopio.v1"
    assert PERSON_SPEC.version == "person.v3"


def test_auto_merge_policy() -> None:
    assert EVENT_SPEC.auto_merge is True
    assert ACOPIO_SPEC.auto_merge is True
    assert PERSON_SPEC.auto_merge is False


def test_specs_keys() -> None:
    assert set(SPECS) == {"Event", "AcopioCenter", "Person"}


def test_person_has_no_fingerprint_fn() -> None:
    assert PERSON_SPEC.fingerprint_fn is None
    assert PERSON_SPEC.blocking_fn is not None
