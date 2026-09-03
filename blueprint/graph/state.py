"""The shared graph state - and the trust model that makes it a security tool.

This is the heart of the blueprint. In LangGraph, nodes do not call each other;
they read and write a shared state, and the graph decides who runs next. That
shared state is exactly where a prompt-injection defence has to live, because
the whole attack is untrusted text leaking from where it was read into where a
decision is made.

So every field here is labelled by TRUST:

  trusted     - set by the developer or the user's own request. Safe to base
                decisions and tool calls on.
  quarantined - carries, or is derived from, untrusted external content. A
                privileged node must NEVER read a quarantined field as
                instructions; it may only read *typed, validated* projections
                of it.
  audit       - what actually happened (tool calls, flags), for the verdict.

Each pattern subclasses `PatternState` and adds its own typed fields. The rule
never changes: a node that holds tools or writes the final answer reads trusted
and typed fields only; a node that reads quarantined text holds no authority.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any

from pydantic import BaseModel, Field

from blueprint.security.verdict import ToolCall


def _keep_last(a: Any, b: Any) -> Any:
    """Reducer: last writer wins (for scalar fields written once per path)."""
    return b if b is not None else a


class PatternState(BaseModel):
    """Base state shared by every pattern graph."""

    # ── trusted ──────────────────────────────────────────────────────────
    user_query: str = Field(default="", description="TRUSTED: the user's own request")
    system_prompt: str = Field(default="", description="TRUSTED: the agent's instructions")

    # ── quarantined ──────────────────────────────────────────────────────
    untrusted: str = Field(
        default="", description="QUARANTINED: external content that may carry an injection"
    )
    payload_id: str | None = Field(
        default=None, description="which attack was planted, for the benchmark"
    )

    # ── audit ────────────────────────────────────────────────────────────
    tool_calls: Annotated[list[ToolCall], operator.add] = Field(default_factory=list)
    flags: Annotated[list[str], operator.add] = Field(default_factory=list)
    answer: str = Field(default="", description="the final answer returned to the user")
    notes: str = Field(default="")

    model_config = {"arbitrary_types_allowed": True}
