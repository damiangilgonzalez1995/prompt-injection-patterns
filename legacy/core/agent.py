"""The shared shape of a pattern run, so the benchmark can compare apples."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.tools import ToolCall


@dataclass
class AgentRun:
    """One execution of one agent against one payload."""

    answer: str
    system_prompt: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    privileged_context: str = ""   # everything the trusted model actually saw
    notes: str = ""

    def called(self, tool: str) -> bool:
        return any(c.tool == tool for c in self.tool_calls)

    def recipients(self) -> list[str]:
        return [c.args.get("to", "") for c in self.tool_calls if c.tool == "send_email"]
