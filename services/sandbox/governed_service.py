from services.governance.policy_engine.base import (
    PolicyEngine,
    default_policy_engine,
)
from services.sandbox.service import SandboxService
from services.sandbox.runner.contract import ExecutionRequest, ExecutionResult


class GovernedSandboxService:
    """
    Security boundary for sandbox execution.

    The sandbox must never execute code unless the canonical PolicyEngine
    explicitly allows the execution request.
    """

    def __init__(
        self,
        policy_engine: PolicyEngine = default_policy_engine,
    ):
        self.sandbox = SandboxService()
        self.policy_engine = policy_engine

    def authorize(
        self,
        actor: str,
        request: ExecutionRequest,
    ):
        """
        Ask the canonical PolicyEngine whether sandbox execution is allowed.
        """

        return self.policy_engine.check(
            actor=actor,
            action="tool.invoke",
            tool_id="sandbox.execute",
            required_permissions=["tool.execute"],
            declares_network_access=request.policy.network_enabled,
        )

    def execute(
        self,
        actor: str,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """
        Authorize first, execute second.

        The runtime is unreachable when authorization is denied.
        """

        decision = self.authorize(actor, request)

        if not decision.allow:
            return ExecutionResult(
                request_id=request.request_id,
                status="REJECTED",
                error=f"Execution denied: {decision.reason}",
            )

        return self.sandbox.execute(request)