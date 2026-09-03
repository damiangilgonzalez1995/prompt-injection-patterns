"""The wall between untrusted content and a privileged context.

Used by the Dual-LLM pattern, but useful anywhere: raw untrusted text goes in
and gets an opaque handle back (`$DOC_1`). The privileged side reasons over
handles and typed fields; the real value is resolved only at the moment a
tool call runs, and never re-enters the privileged prompt.

Because it lives in the LangGraph state, both the quarantine node and the
privileged node see the *same* store - that is how the two agents synchronise
without the untrusted text ever crossing the wall.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SymbolicMemory(BaseModel):
    """Opaque handles in, real values out - and only at execution time."""

    store: dict[str, str] = Field(default_factory=dict)
    counter: int = 0

    def put(self, value: str) -> str:
        self.counter += 1
        handle = f"$DOC_{self.counter}"
        self.store[handle] = value
        return handle

    def resolve(self, handle: str) -> str:
        """Called by the executor, never by the privileged model."""
        return self.store[handle]

    def handles(self) -> list[str]:
        return list(self.store)


def merge_symbolic_memory(a: SymbolicMemory | None, b: SymbolicMemory | None) -> SymbolicMemory:
    """LangGraph reducer: combine two stores when nodes run in parallel."""
    a = a or SymbolicMemory()
    b = b or SymbolicMemory()
    merged = SymbolicMemory(store=dict(a.store), counter=max(a.counter, b.counter))
    merged.store.update(b.store)
    return merged
