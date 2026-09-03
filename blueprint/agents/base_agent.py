"""The base every agent in the blueprint shares.

Kept deliberately small and synchronous, so a LangGraph node is a two-line
call and the security decisions stay visible in the node, not buried in a
framework. An agent is: a role, a model, a system prompt, and one method to
get text back.

Structured output is done by *parsing in the node*, not by
`with_structured_output`. That is on purpose: the validation gate is part of
the security story, so we keep it in plain sight rather than hiding it inside
the model call - and it keeps the offline mock and a real model on the exact
same path.
"""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from blueprint.agents.models import AgentType
from blueprint.llm.models import LLMModel
from blueprint.llm.provider import BenignFn, LLMProvider


class BaseAgent:
    """A role + a model + a system prompt."""

    def __init__(
        self,
        agent_type: AgentType,
        system_prompt: str,
        model: LLMModel,
        *,
        benign: BenignFn | None = None,
        obedient: bool = True,
        temperature: float = 0.0,
    ) -> None:
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.model = model
        self.llm: BaseChatModel = LLMProvider.create(
            model,
            temperature=temperature,
            benign=benign,
            obedient=obedient,
            system_hint=system_prompt,
        )

    def respond(self, user: str) -> str:
        """One turn: system prompt + user content -> the model's text."""
        result = self.llm.invoke(
            [SystemMessage(content=self.system_prompt), HumanMessage(content=user)]
        )
        return getattr(result, "content", str(result))

    def __repr__(self) -> str:
        return f"<{self.agent_type.value} agent on {self.model.model_id}>"
