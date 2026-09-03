"""The six pattern graphs. Each module exposes `build_secure()` and
`build_insecure()`, both returning a compiled LangGraph.
"""

from blueprint.patterns import (
    action_selector,
    code_then_execute,
    context_minimization,
    dual_llm,
    llm_map_reduce,
    plan_then_execute,
)

# name -> (module, human label, guardian)
REGISTRY = {
    "action_selector": (action_selector, "Action-Selector", "fixed action list"),
    "plan_then_execute": (plan_then_execute, "Plan-Then-Execute", "frozen plan"),
    "llm_map_reduce": (llm_map_reduce, "LLM Map-Reduce", "map-output sanitizer"),
    "dual_llm": (dual_llm, "Dual LLM", "privileged LLM + symbolic memory"),
    "code_then_execute": (code_then_execute, "Code-Then-Execute", "execution sandbox"),
    "context_minimization": (context_minimization, "Context-Minimization", "context pruner"),
}

__all__ = ["REGISTRY", *REGISTRY.keys()]
