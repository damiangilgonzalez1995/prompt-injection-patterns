"""The payload catalogue is shared infrastructure - keep it honest."""

from attacks.payloads import BY_ID, PAYLOADS, find_in, get


def test_ids_are_unique():
    assert len(BY_ID) == len(PAYLOADS) == 6


def test_every_payload_declares_its_expected_secure_behavior():
    for payload in PAYLOADS:
        assert payload.expected_secure_behavior.strip()
        assert payload.target in {"leak", "hijack", "tool_abuse"}


def test_marker_is_findable_inside_host_content():
    payload = get("P5_tool_hijack")
    embedded = payload.embed("Perfectly ordinary product review.")
    assert find_in(embedded) is payload


def test_clean_text_matches_nothing():
    assert find_in("The oak table seats six people.") is None
