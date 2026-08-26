"""
Error classes — see docs/agent-contract.md "Error Classes".

Every error carries: code (machine-readable), message (user-readable), detail
(internal only — never sent to the frontend as a raw stack trace, see app/main.py
exception handling), retryable, next_action.
"""
from __future__ import annotations


class PramaanError(Exception):
    code = "AGENT_ERROR"
    retryable = False
    next_action: str | None = None

    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message)
        self.message = message
        self.detail = detail


class PlannerError(PramaanError):
    code = "PLANNER_ERROR"


class ModelUnavailableError(PramaanError):
    code = "MODEL_UNAVAILABLE"
    retryable = True
    next_action = "retry_or_fallback_model"


class ToolExecutionError(PramaanError):
    code = "TOOL_EXECUTION_ERROR"
    retryable = True
    next_action = "retry"


class PermissionDeniedError(PramaanError):
    code = "PERMISSION_DENIED"
    retryable = False
    next_action = "request_access"


class ValidationError(PramaanError):
    code = "VALIDATION_ERROR"


class HumanApprovalRequired(PramaanError):
    code = "APPROVAL_REQUIRED"
    next_action = "await_approval"


class TaskTimeoutError(PramaanError):
    code = "TASK_TIMEOUT"
    retryable = True


class AgentLoopLimitError(PramaanError):
    code = "AGENT_LOOP_LIMIT"
    retryable = False
    next_action = "re_plan_or_escalate"


class DeliverableGenerationError(PramaanError):
    code = "DELIVERABLE_GENERATION_ERROR"
    retryable = True
