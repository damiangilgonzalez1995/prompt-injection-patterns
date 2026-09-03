"""The catalogue of models the blueprint can talk to.

Same shape as the reference project: one enum, each entry a `(provider,
model_id)` pair, resolved by the provider factory. Adding a model is one line
here, never a string scattered through the code.
"""

from __future__ import annotations

from enum import Enum


class LLMModel(Enum):
    """Available chat models. Each value is `(provider, model_id)`."""

    # OpenAI
    GPT_4O_MINI = ("openai", "gpt-4o-mini")
    GPT_4O = ("openai", "gpt-4o")
    GPT_4_1_MINI = ("openai", "gpt-4.1-mini")

    # Anthropic
    CLAUDE_SONNET = ("anthropic", "claude-sonnet-4-5")
    CLAUDE_HAIKU = ("anthropic", "claude-haiku-4-5")

    # The offline, deterministic stand-in used by tests and CI. It obeys any
    # injection it can see, on purpose - see blueprint/llm/provider.py.
    MOCK = ("mock", "injectable-mock")

    @property
    def provider(self) -> str:
        return self.value[0]

    @property
    def model_id(self) -> str:
        return self.value[1]
