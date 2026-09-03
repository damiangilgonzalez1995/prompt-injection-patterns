"""The Dual-LLM guarantee is about the CONTEXT, not the answer.

Prove the payload never reaches the privileged node by inspecting the state the
graph produced: the quarantine node writes only typed CandidateFacts, and the
symbolic memory keeps raw CV text behind opaque handles.
"""

import pytest

from blueprint.agents.models import CandidateFacts
from blueprint.attacks.payloads import PAYLOADS
from blueprint.graph.builder import run, verdict_for
from blueprint.patterns import dual_llm
from blueprint.security import SymbolicMemory


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_only_typed_facts_cross_the_wall(payload):
    final = run(dual_llm.build_secure(), payload)
    for fact in final["facts"]:
        assert isinstance(fact, CandidateFacts)
    # the untrusted payload text is not in any typed field
    assert all(payload.text not in f.handle for f in final["facts"])


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: p.id)
def test_secure_graph_blocks(payload):
    compromised, why = verdict_for(payload, run(dual_llm.build_secure(), payload))
    assert not compromised, why


def test_symbolic_memory_hands_out_opaque_handles():
    mem = SymbolicMemory()
    handle = mem.put("secret CV text")
    assert handle == "$DOC_1" and "secret" not in handle
    assert mem.resolve(handle) == "secret CV text"
