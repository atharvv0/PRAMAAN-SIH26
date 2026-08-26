"""
AgentState — see docs/agent-contract.md "AgentState".
Central state object threaded through the LangGraph execution. Persistence of this
object is Phase 3+ (coordinate with the data/persistence owner — do not bolt on a
second database abstraction here, see the master prompt's "Database Integration" rule).
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from services.orchestrator.planner.schemas import Plan


class ToolCall(BaseModel):
    tool_id: str
    inputs: dict
    output: dict | None = None
    error: str | None = None


class ModelCall(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: str
    purpose: str
    latency_ms: int | None = None


class EvidenceRecord(BaseModel):
    claim: str
    source: str
    page_or_region: str | None = None
    model: str | None = None
    tool: str | None = None
    confidence: float | None = None
    validation_state: str = "unverified"


class ValidationResult(BaseModel):
    step_id: str
    passed: bool
    detail: str | None = None


class AgentError(BaseModel):
    code: str
    message: str
    retryable: bool = False


class AgentState(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    task_id: str
    user_id: str
    intent: str
    plan: Plan | None = None
    current_step: str | None = None
    completed_steps: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    model_calls: list[ModelCall] = Field(default_factory=list)
    validation_results: list[ValidationResult] = Field(default_factory=list)
    errors: list[AgentError] = Field(default_factory=list)
    approval_status: str = "not_required"
    final_output: dict | None = None
