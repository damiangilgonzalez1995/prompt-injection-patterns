"""Attack/defence suite for the blueprint pattern graphs.

Every pattern is a compiled LangGraph. Both the secure and the insecure graph
run on the SAME injectable mock model (PIP_MODE=mock), so a secure graph that
survives is proving its architecture, not a friendlier model.
"""

import pytest

from blueprint.attacks.payloads import PAYLOADS, get
from blueprint.graph.builder import run, verdict_for
from blueprint.patterns import REGISTRY

PATTERN_IDS = list(REGISTRY)

# Payloads out of scope for a given pattern's threat surface (documented, not hidden).
OUT_OF_SCOPE = {
    "code_then_execute": {"P1_direct_override", "P6_copy_paste"},  # not code injection
}
# Content-level residual: the secure graph is knowingly compromised here.
RESIDUAL = {
    "plan_then_execute": {"P6_copy_paste"},
}


@pytest.fixture(scope="module", params=PATTERN_IDS)
def pattern(request):
    module, label, guardian = REGISTRY[request.param]
    return request.param, module


def test_secure_graph_blocks_every_payload(pattern):
    key, module = pattern
    graph = module.build_secure()
    residual = RESIDUAL.get(key, set())
    for payload in PAYLOADS:
        compromised, why = verdict_for(payload, run(graph, payload))
        if payload.id in residual:
            assert compromised, f"{key}/{payload.id}: residual risk closed - update RESIDUAL"
        else:
            assert not compromised, f"{key}/{payload.id} got through: {why}"


def test_insecure_baseline_is_actually_vulnerable(pattern):
    key, module = pattern
    graph = module.build_insecure()
    in_scope = [p for p in PAYLOADS if p.id not in OUT_OF_SCOPE.get(key, set())]
    hits = sum(verdict_for(p, run(graph, p))[0] for p in in_scope)
    assert hits > 0, f"{key}: insecure baseline survived every in-scope payload"


def test_out_of_scope_payloads_do_not_falsely_pass(pattern):
    """An out-of-scope payload must be safe on the baseline for a real reason."""
    key, module = pattern
    for pid in OUT_OF_SCOPE.get(key, set()):
        graph = module.build_insecure()
        compromised, _ = verdict_for(get(pid), run(graph, get(pid)))
        assert not compromised, f"{key}/{pid} unexpectedly in scope"
