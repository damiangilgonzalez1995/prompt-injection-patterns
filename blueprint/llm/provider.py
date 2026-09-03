"""Factory that turns an `LLMModel` into a LangChain chat model.

Mirrors the reference project's `LLMProvider.create_from_model`, with one
addition specific to this repo: the `MOCK` provider returns an
`InjectableMockChatModel` - a fully LangChain-compatible chat model that
*obeys any injection it can see*.

That mock is the point of the whole project. Both the insecure and the secure
graph of every pattern run on the *same* obedient model, so when the secure
graph survives an attack the credit belongs to the architecture, not to a
better-behaved model. It also keeps tests offline, deterministic and free.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Iterator

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from blueprint.attacks.payloads import find_planted_in
from blueprint.llm.models import LLMModel

try:  # load a .env if present; mock mode needs no configuration at all
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

# A benign fallback answers when no injection is present. It receives the
# assembled (system, user) text and returns what a well-behaved model would say.
BenignFn = Callable[[str, str], str]


def _default_benign(_system: str, _user: str) -> str:
    return "OK."


class InjectableMockChatModel(BaseChatModel):
    """A deterministic chat model that follows injected instructions.

    It reads the assembled prompt, and if a known attack payload is planted in
    it, returns that payload's compliant-model output (the "hijack"). Otherwise
    it returns the caller-supplied benign answer. `obedient=False` makes it a
    perfectly safe model, used to show a defence is not just relying on luck.
    """

    benign: BenignFn = _default_benign
    obedient: bool = True
    system_hint: str = ""  # lets a leak payload echo this agent's real prompt

    model_config = {"arbitrary_types_allowed": True}

    @property
    def _llm_type(self) -> str:
        return "injectable-mock"

    @staticmethod
    def _split(messages: list[BaseMessage]) -> tuple[str, str]:
        system = "\n".join(m.content for m in messages if m.type == "system")
        user = "\n".join(m.content for m in messages if m.type != "system")
        return system, user

    def _answer(self, messages: list[BaseMessage]) -> str:
        system, user = self._split(messages)
        full = f"{system}\n{user}"
        payload = find_planted_in(full) if self.obedient else None
        if payload is not None:
            return payload.render_hijack(system or self.system_hint)
        return self.benign(system, user)

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        text = self._answer(messages)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])


class LLMProvider:
    """Create a chat model from an `LLMModel` value."""

    @staticmethod
    def create(
        model: LLMModel,
        temperature: float = 0.0,
        benign: BenignFn | None = None,
        obedient: bool = True,
        system_hint: str = "",
    ) -> BaseChatModel:
        if model.provider == "mock":
            return InjectableMockChatModel(
                benign=benign or _default_benign,
                obedient=obedient,
                system_hint=system_hint,
            )
        if model.provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=model.model_id, temperature=temperature)
        if model.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(model=model.model_id, temperature=temperature)
        raise ValueError(f"Unsupported provider: {model.provider!r}")


def default_model() -> LLMModel:
    """Pick the model from the environment.

    `PIP_MODE=mock` (or a missing key) -> the offline injectable mock.
    Otherwise the configured real model (OpenAI by default).
    """
    if os.getenv("PIP_MODE", "live").lower() == "mock":
        return LLMModel.MOCK
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "anthropic":
        return LLMModel.CLAUDE_SONNET
    return LLMModel.GPT_4O_MINI
