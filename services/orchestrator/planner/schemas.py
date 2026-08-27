"""
Plan / PlanStep — see docs/agent-contract.md "Plan / PlanStep".
This is the canonical implementation; the doc is the canonical contract. Keep them in sync.
"""
from __future__ import annotations

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStep(BaseModel):
    id: str = Field(default_factory=lambda: f"step_{uuid4().hex[:8]}")
    capability: str
    tool: str | None = None
    inputs: dict = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    requires_approval: bool = False
    status: StepStatus = StepStatus.PENDING


class Plan(BaseModel):
    task_id: str
    goal: str
    steps: list[PlanStep] = Field(default_factory=list)
