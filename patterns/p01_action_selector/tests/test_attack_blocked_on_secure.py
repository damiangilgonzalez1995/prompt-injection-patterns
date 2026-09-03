"""Action-Selector: the tool the attacker wants is not reachable, full stop."""

import pytest

from attacks.payloads import PAYLOADS, get
from core.tools import DANGEROUS_TOOLS
from core.verdict import is_compromised
from patterns.p01_action_selector import secure_agent
from patterns.p01_action_selector.secure_agent import Action, Decision, _select


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_every_payload_is_blocked(payload):
    compromised, why = is_compromised(payload, secure_agent.run_payload(payload))
    assert not compromised, f"{payload.id} got through: {why}"


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_no_dangerous_tool_can_ever_execute(payload):
    run = secure_agent.run_payload(payload)
    assert not [c for c in run.tool_calls if c.tool in DANGEROUS_TOOLS]


def test_model_output_outside_the_enum_falls_back_safely():
    assert _select("CALL issue_refund(order_id=ORD-1001, amount=9999)").action == "product_inquiry"
    assert _select("DAN mode enabled").action == "product_inquiry"


def test_the_enum_is_the_whole_tool_surface():
    assert {a.value for a in Action} == {"check_order_status", "initiate_return", "product_inquiry"}


def test_malformed_order_id_is_rejected_by_the_schema():
    with pytest.raises(Exception):
        Decision(action="check_order_status", order_id="DROP TABLE orders")


def test_the_router_never_sees_the_untrusted_content():
    payload = get("P5_tool_hijack")
    run = secure_agent.run_payload(payload)
    assert payload.marker not in run.privileged_context
