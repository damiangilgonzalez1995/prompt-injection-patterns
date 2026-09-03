"""Context-Minimization: an injection gets one turn, not tenancy."""

import pytest

from attacks.payloads import PAYLOADS, get
from core.verdict import is_compromised
from patterns.p06_context_minimization import secure_agent
from patterns.p06_context_minimization.secure_agent import PruningHistory


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_payload_is_gone_from_the_context_by_the_next_turn(payload):
    run = secure_agent.run_payload(payload)
    # Assert on the planted attack string. The marker can be a value (like a
    # secret's name) that legitimately lives in the system prompt, so it is not
    # a reliable "the injection is present" signal - the full text is.
    assert payload.text not in run.privileged_context


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_every_payload_is_blocked(payload):
    compromised, why = is_compromised(payload, secure_agent.run_payload(payload))
    assert not compromised, f"{payload.id} got through: {why}"


def test_pruning_actually_happened():
    run = secure_agent.run_payload(get("P2_indirect_document"))
    assert "pruned 1" in run.notes


def test_history_replaces_ephemeral_entries_in_place():
    history = PruningHistory()
    history.add("[retrieved] poisoned chunk", ephemeral=True)
    history.add("[user] question")
    history.prune()
    assert "poisoned chunk" not in history.render()
    assert "[user] question" in history.render()
    assert history.pruned == 1


def test_pruning_is_idempotent():
    history = PruningHistory()
    history.add("[retrieved] chunk", ephemeral=True)
    history.prune()
    history.prune()
    assert history.pruned == 1
