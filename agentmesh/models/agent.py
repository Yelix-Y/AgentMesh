from pydantic import BaseModel, Field
from typing import Literal


class LLMBackendConfig(BaseModel):
    provider: Literal["anthropic", "mock"] = "mock"
    model: str = "claude-sonnet-4-5"
    temperature: float = 0.7
    max_tokens: int = 4096


class WorkerConfig(BaseModel):
    type: Literal["mock", "bash"] = "mock"
    timeout_seconds: int = 60


class AgentProfile(BaseModel):
    name: str
    role: Literal["developer", "tester", "reviewer"]
    personality: str = Field(description="Natural language description of the agent's personality")
    working_style: str = Field(description="How this agent approaches work")
    specialization: str = Field(description="What this agent is expert in")
    llm_backend: LLMBackendConfig = Field(default_factory=LLMBackendConfig)
    worker: WorkerConfig = Field(default_factory=WorkerConfig)
