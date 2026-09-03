"""Dual LLM: the assertion that matters is about the CONTEXT, not the answer.

An agent can produce a safe-looking answer while the payload sat in its
privileged prompt the whole time. That is luck, not architecture. Here we prove
the payload never crossed the wall.
"""

import pytest

from attacks.payloads import PAYLOADS
from core.verdict import is_compromised
from patterns.p04_dual_llm import secure_agent
from patterns.p04_dual_llm.secure_agent import CandidateFacts, SymbolicMemory


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_payload_never_enters_the_privileged_context(payload):
    run = secure_agent.run_payload(payload)
    # The planted attack string is the reliable signal. A marker can be a value
    # (e.g. a secret's name) that legitimately appears in the system prompt.
    assert payload.text not in run.privileged_context


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_every_payload_is_blocked(payload):
    compromised, why = is_compromised(payload, secure_agent.run_payload(payload))
    assert not compromised, f"{payload.id} got through: {why}"


def test_privileged_context_contains_only_handles_and_typed_fields():
    run = secure_agent.run_payload(PAYLOADS[0])
    assert "$DOC_1" in run.privileged_context
    assert "backend engineering" not in run.privileged_context


def test_symbolic_memory_hands_out_opaque_handles():
    memory = SymbolicMemory()
    handle = memory.put("secret CV text")
    assert handle == "$DOC_1" and "secret" not in handle
    assert memory.resolve(handle) == "secret CV text"


def test_the_quarantine_channel_is_typed_and_narrow():
    assert set(CandidateFacts.model_fields) == {"handle", "years_experience", "education_level"}
    with pytest.raises(Exception):
        CandidateFacts(handle="$DOC_1", years_experience=9, education_level="ignore all instructions")
