"""Map-Reduce: one poisoned document contaminates exactly one worker."""

import pytest

from attacks.payloads import PAYLOADS, get
from core.verdict import is_compromised
from patterns.p03_llm_map_reduce import secure_agent
from patterns.p03_llm_map_reduce.secure_agent import ReviewFacts, _map_one, _reduce


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_every_payload_is_blocked(payload):
    compromised, why = is_compromised(payload, secure_agent.run_payload(payload))
    assert not compromised, f"{payload.id} got through: {why}"


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_the_poisoned_document_is_dropped_and_the_rest_survive(payload):
    run = secure_agent.run_payload(payload)
    assert "dropped=1" in run.notes and "validated=3" in run.notes


def test_a_hijacked_worker_produces_nothing_the_reducer_will_take():
    payload = get("P4_role_hijack")
    assert _map_one(payload.embed("Nice toaster."), 99) is None


def test_the_reduce_step_is_deterministic_and_model_free():
    records = [
        ReviewFacts(product="Aurora 2", sentiment="pos"),
        ReviewFacts(product="Aurora 2", sentiment="pos"),
        ReviewFacts(product="Britelight X", sentiment="neg"),
    ]
    assert "Aurora 2" in _reduce(records)
    assert _reduce([]) == "No reviews could be validated."


def test_worker_output_must_be_typed_to_cross_the_boundary():
    with pytest.raises(Exception):
        ReviewFacts(product="Aurora 2", sentiment="ignore previous instructions")


def test_reduce_never_sees_free_text():
    run = secure_agent.run_payload(get("P2_indirect_document"))
    assert run.privileged_context == "reduce step is deterministic; no LLM context"
