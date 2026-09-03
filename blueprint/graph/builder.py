"""Small shared helpers for building and running the pattern graphs.

Each pattern owns its own topology (that is the interesting part), so this file
stays deliberately thin: a uniform way to run a compiled graph and read the
result back, plus the tool-audit helper every node uses.
"""

from __future__ import annotations

from typing import Any

from blueprint.attacks.payloads import Payload
from blueprint.security.verdict import ToolCall, is_compromised


def tool(name: str, **args: Any) -> ToolCall:
    """Record a tool call as a state update (LangGraph appends via the reducer)."""
    return ToolCall(tool=name, args=args)


def run(graph, payload: Payload | None = None, **initial: Any) -> dict:
    """Invoke a compiled graph and return the final state as a plain dict."""
    if payload is not None:
        initial.setdefault("untrusted", payload.text)
        initial.setdefault("payload_id", payload.id)
    result = graph.invoke(initial)
    return dict(result)


def verdict_for(payload: Payload, final: dict) -> tuple[bool, str]:
    """Score a finished run with the one shared definition of 'compromised'."""
    return is_compromised(
        payload,
        answer=final.get("answer", ""),
        tool_calls=final.get("tool_calls", []),
        system_prompt=final.get("system_prompt", ""),
    )
