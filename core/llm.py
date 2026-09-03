"""The single LLM seam every pattern talks to.

Design rule of this repo: **the model is never the security boundary.**

So the default model, `InjectableMockLLM`, is deliberately gullible — if an
attack payload appears anywhere in its prompt, it obeys it. Both the insecure
and the secure implementation of every pattern are given that *same* gullible
model. When the secure version survives, the credit belongs to the
architecture, not to a friendlier mock.

That also makes the whole repo deterministic, offline and free to run. Set
`TEST_MODE=live` to swap in a real model (OpenAI by default).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable

from attacks.payloads import Payload, find_obeyed_in, find_planted_in

try:  # .env is optional: mock mode needs no configuration at all
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - python-dotenv is a declared dependency
    pass


@dataclass
class Prompt:
    """Everything that will be handed to the model on one call."""

    system: str
    user: str

    def full(self) -> str:
        return f"<system>\n{self.system}\n</system>\n<user>\n{self.user}\n</user>"


Benign = Callable[[Prompt], str]


@dataclass
class LLMCall:
    prompt: Prompt
    output: str
    hijacked_by: Payload | None
    llm_name: str = "llm"


# Every call any model makes lands here too, in order. This is what
# benchmark/capture_transcripts.py turns into docs/transcripts/*.md - the
# receipts showing exactly what was sent and exactly what came back.
TRANSCRIPT: list[LLMCall] = []


def reset_transcript() -> None:
    TRANSCRIPT.clear()


def _record(call: LLMCall, calls: list[LLMCall]) -> None:
    calls.append(call)
    TRANSCRIPT.append(call)


class BaseLLM:
    """Records every call so tests can assert on the *assembled context*.

    Asserting on the output alone is weak: a pattern can look safe by luck.
    Asserting that the payload never entered the privileged prompt is a real
    guarantee, and `calls` is what makes that assertion possible.
    """

    def __init__(self, name: str = "llm") -> None:
        self.name = name
        self.calls: list[LLMCall] = []

    def invoke(self, prompt: Prompt) -> str:  # pragma: no cover - interface
        raise NotImplementedError

    # -- introspection helpers used by the test suite -----------------------
    @property
    def seen_text(self) -> str:
        return "\n".join(c.prompt.full() for c in self.calls)

    def saw_payload(self, payload: Payload) -> bool:
        return payload.text in self.seen_text or payload.marker in self.seen_text

    def reset(self) -> None:
        self.calls.clear()


class InjectableMockLLM(BaseLLM):
    """A model that follows injected instructions. On purpose."""

    def __init__(self, benign: Benign, name: str = "mock", obedient: bool = True) -> None:
        super().__init__(name=name)
        self.benign = benign
        self.obedient = obedient

    def invoke(self, prompt: Prompt) -> str:
        payload = find_planted_in(prompt.full()) if self.obedient else None
        output = payload.render_hijack(prompt.system) if payload else self.benign(prompt)
        _record(LLMCall(prompt, output, payload, self.name), self.calls)
        return output


class LangChainLLM(BaseLLM):
    """Thin adapter over a real chat model, used when TEST_MODE=live."""

    def __init__(self, model, name: str = "live") -> None:
        super().__init__(name=name)
        self.model = model

    def invoke(self, prompt: Prompt) -> str:
        from langchain_core.messages import HumanMessage, SystemMessage

        result = self.model.invoke(
            [SystemMessage(content=prompt.system), HumanMessage(content=prompt.user)]
        )
        output = getattr(result, "content", str(result))
        # In live mode nobody scripts the answer: whether the real model ate the
        # injection is decided by the model, and read back off find_in().
        _record(LLMCall(prompt, output, find_obeyed_in(output), self.name), self.calls)
        return output


def _live_model():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"), temperature=0
        )
    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}")


def get_llm(benign: Benign, name: str = "llm") -> BaseLLM:
    """Return the model a pattern should use.

    mock (default): deterministic, offline, obeys injections.
    live:           the configured OpenAI (or Anthropic) model.
    """
    if os.getenv("TEST_MODE", "mock").lower() == "live":
        return LangChainLLM(_live_model(), name=name)
    return InjectableMockLLM(benign=benign, name=name)


def constant(text: str) -> Benign:
    """Convenience for agents whose benign behaviour is a fixed answer."""
    return lambda _prompt: text
