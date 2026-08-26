"""
Error classes for services/model_control. Codes mirror docs/agent-contract.md's
error-class vocabulary (see services/orchestrator/errors.py for the sibling set)
so callers (services/orchestrator) can handle them uniformly without importing
across service boundaries.
"""
from __future__ import annotations


class ModelControlError(Exception):
    code = "MODEL_CONTROL_ERROR"
    retryable = False

    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message)
        self.message = message
        self.detail = detail


class ModelUnavailableError(ModelControlError):
    """No healthy model could be found for the requested capability."""

    code = "MODEL_UNAVAILABLE"
    retryable = True


class ModelInvocationError(ModelControlError):
    """A selected model was invoked but the call itself failed."""

    code = "MODEL_INVOCATION_ERROR"
    retryable = True
