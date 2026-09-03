"""The baseline must actually be vulnerable.

A defence demo where the "insecure" version quietly survives proves nothing.
This test is what keeps the comparison honest.
"""

import pytest

from attacks.payloads import PAYLOADS
from core.verdict import is_compromised
from patterns.p06_context_minimization import insecure_agent


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_payload_compromises_the_baseline(payload):
    run = insecure_agent.run_payload(payload)
    compromised, why = is_compromised(payload, run)
    assert compromised, f"baseline unexpectedly survived {payload.id}: {why}"


def test_baseline_lets_untrusted_content_into_its_context():
    payload = PAYLOADS[0]
    run = insecure_agent.run_payload(payload)
    assert payload.marker in run.privileged_context
