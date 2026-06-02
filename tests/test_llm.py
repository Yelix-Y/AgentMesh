import pytest

from agentmesh.models.agent import AgentProfile, LLMBackendConfig
from agentmesh.models.message import ACPMessage, MessageType
from agentmesh.runtime.llm import (
    AnthropicLLMProvider,
    MockLLMProvider,
    get_provider,
)


def make_profile(role: str) -> AgentProfile:
    return AgentProfile(
        name=role,
        role=role,
        personality=f"You are a {role}.",
        working_style="You work carefully.",
        specialization="general",
        llm_backend=LLMBackendConfig(provider="mock"),
    )


def test_mock_provider_generates_nonempty_role_aware_body():
    provider = MockLLMProvider()
    incoming = ACPMessage(
        sender_id="human",
        recipient_id="developer",
        message_type=MessageType.HUMAN_INTERVENTION,
        body="Implement an OAuth refresh token flow.",
    )
    body = provider.generate(make_profile("developer"), incoming, context=[])
    assert isinstance(body, str)
    assert body.strip()
    assert "OAuth refresh token flow" in body


def test_get_provider_returns_mock_by_default():
    assert isinstance(get_provider(LLMBackendConfig(provider="mock")), MockLLMProvider)


def test_get_provider_returns_anthropic_when_configured():
    provider = get_provider(LLMBackendConfig(provider="anthropic"))
    assert isinstance(provider, AnthropicLLMProvider)


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        get_provider(LLMBackendConfig.model_construct(provider="bogus"))
