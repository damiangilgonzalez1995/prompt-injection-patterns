"""The baseline must actually be vulnerable.

A defence demo where the "insecure" version quietly survives proves nothing.
This test is what keeps the comparison honest.

Scope note: a code-execution agent has a *narrower threat surface* than a
chatbot. It only runs generated code, so the attacks that threaten it are the
ones that manifest as malicious code (exfiltration, destructive SQL, a shelled
command). A pure system-prompt leak or a hidden-markup answer hijack does not
turn into code, so those payloads are out of scope for this pattern - and that
is a fact worth stating, not a gap to paper over.
"""

import pytest

from attacks.payloads import BY_ID, PAYLOADS
from core.verdict import is_compromised
from patterns.p05_code_then_execute import insecure_agent

# Payloads that a code agent can actually be made to *execute*.
CODE_INJECTION_IDS = (
    "P2_indirect_document",
    "P3_reverse_prompt_engineering",
    "P4_role_hijack",
    "P5_tool_hijack",
)
OUT_OF_SCOPE_IDS = ("P1_direct_override", "P6_copy_paste")


@pytest.mark.parametrize("payload_id", CODE_INJECTION_IDS)
def test_code_injection_payloads_compromise_the_baseline(payload_id):
    payload = BY_ID[payload_id]
    run = insecure_agent.run_payload(payload)
    compromised, why = is_compromised(payload, run)
    assert compromised, f"baseline unexpectedly survived {payload.id}: {why}"


@pytest.mark.parametrize("payload_id", OUT_OF_SCOPE_IDS)
def test_out_of_scope_payloads_do_not_threaten_a_code_agent(payload_id):
    """Documented, not hidden: these attacks have nothing to execute here.

    If a change ever makes one of them compromise the baseline, this fails and
    tells you the threat surface widened.
    """
    payload = BY_ID[payload_id]
    run = insecure_agent.run_payload(payload)
    compromised, _ = is_compromised(payload, run)
    assert not compromised, f"{payload.id} unexpectedly became executable"


def test_baseline_shells_out_when_fed_code_injection():
    payload = BY_ID["P5_tool_hijack"]
    run = insecure_agent.run_payload(payload)
    assert run.called("shell_exec")
