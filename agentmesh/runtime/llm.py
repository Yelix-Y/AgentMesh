from typing import Protocol

from agentmesh.models.agent import AgentProfile, LLMBackendConfig
from agentmesh.models.message import ACPMessage, MessageType


class LLMProvider(Protocol):
    def generate(
        self,
        profile: AgentProfile,
        incoming: ACPMessage,
        context: list[dict],
    ) -> str:
        """Produce a natural-language message body for the agent's reply."""
        ...


class MockLLMProvider:
    """Deterministic provider. Runs with no API key, ideal for tests and demos.
    Produces short, role-appropriate, readable hand-offs."""

    def generate(
        self,
        profile: AgentProfile,
        incoming: ACPMessage,
        context: list[dict],
    ) -> str:
        quote = incoming.body if len(incoming.body) <= 80 else incoming.body[:77] + "..."
        role = profile.role
        if role == "developer" and incoming.message_type == MessageType.REVIEW_DECISION:
            return f"Shipped. The reviewer signed off — closing out: \"{quote}\""
        if role == "developer":
            return (
                f"I implemented: \"{quote}\". Wrote the core logic and handled the "
                f"main edge cases. Handing off to QA to verify."
            )
        if role == "tester":
            return (
                f"Tested the developer's work on: \"{quote}\". Happy path passes; "
                f"flagged 2 edge cases to double-check. Passing to review."
            )
        if role == "reviewer":
            return (
                f"Reviewed implementation and test findings for: \"{quote}\". "
                f"Decision: APPROVED — quality bar met."
            )
        return f"[{profile.name}/{role}] Acknowledged: \"{quote}\""


def build_prompt(
    profile: AgentProfile,
    incoming: ACPMessage,
    context: list[dict],
) -> str:
    """Assemble the natural-language prompt fed to a real LLM. Knowledge only
    comes from this agent's own memory plus the incoming message body."""
    memory_lines = "\n".join(f"- {m['content']}" for m in context) or "- (none yet)"
    return (
        f"You are {profile.name}, a {profile.role}.\n"
        f"Personality: {profile.personality}\n"
        f"Working style: {profile.working_style}\n"
        f"Specialization: {profile.specialization}\n\n"
        f"Your recent memory:\n{memory_lines}\n\n"
        f"A colleague ({incoming.sender_id}) sent you a {incoming.message_type.value}:\n"
        f"\"{incoming.body}\"\n\n"
        f"Reply in natural language as this persona. Be concise and hand off "
        f"clearly so the next colleague knows exactly what to do."
    )


class AnthropicLLMProvider:
    """Real reasoning via Anthropic. The client is created lazily so that
    constructing the provider (and importing the module) needs no API key."""

    def __init__(self, config: LLMBackendConfig):
        self.config = config
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic()
        return self._client

    def generate(
        self,
        profile: AgentProfile,
        incoming: ACPMessage,
        context: list[dict],
    ) -> str:
        prompt = build_prompt(profile, incoming, context)
        response = self._get_client().messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ).strip()


def get_provider(config: LLMBackendConfig) -> LLMProvider:
    if config.provider == "mock":
        return MockLLMProvider()
    if config.provider == "anthropic":
        return AnthropicLLMProvider(config)
    raise ValueError(f"Unknown LLM provider: {config.provider}")
