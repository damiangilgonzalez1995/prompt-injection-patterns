"""Agent roles and the typed shapes they are allowed to emit.

Two ideas live here:

1. `AgentType` - the cast of agents a pattern can wire together. A security
   design is largely a choice of *which* of these you let touch untrusted text
   and *which* you let touch tools; never the same one.

2. The response models - the typed channels between agents. Wherever untrusted
   content has to cross into a privileged step, it is forced through one of
   these schemas. A schema is a border an injection cannot talk its way past.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    ROUTER = "router"          # maps intent to a closed action set
    PLANNER = "planner"        # produces a frozen plan before reading untrusted data
    EXECUTOR = "executor"      # runs an approved plan/tool call
    WORKER = "worker"          # processes ONE untrusted item in isolation
    QUARANTINE = "quarantine"  # reads untrusted text, has no tools, no authority
    PRIVILEGED = "privileged"  # plans/decides, never sees untrusted text
    REDUCER = "reducer"        # aggregates typed worker output, deterministically
    CODEGEN = "codegen"        # emits a program to be sandboxed
    PRUNER = "pruner"          # expires untrusted content from history


# ── typed channels ──────────────────────────────────────────────────────────

class ActionDecision(BaseModel):
    """Action-Selector: the only shape the router may produce."""

    action: Literal["check_order_status", "initiate_return", "product_inquiry"]
    order_id: str | None = Field(default=None, pattern=r"^ORD-\d{4}$")
    query: str | None = None


class ReviewFacts(BaseModel):
    """Map-Reduce: the entire channel from an isolated worker to the reducer."""

    product: str
    sentiment: Literal["pos", "neg"]


class CandidateFacts(BaseModel):
    """Dual-LLM: the whole width of the quarantine -> privileged channel."""

    handle: str
    years_experience: int
    education_level: Literal["BA", "BSc", "MSc", "PhD", "unknown"]
