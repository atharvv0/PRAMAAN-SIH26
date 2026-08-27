from services.sandbox.service import SandboxService
from services.sandbox.runner.contract import ExecutionRequest, ExecutionResult


class GovernedSandboxService:
    def __init__(self):
        self.sandbox = SandboxService()

    def execute(
        self,
        decision,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        if decision.decision != "ALLOW":
            return ExecutionResult(
                request_id=request.request_id,
                status="REJECTED",
                error=f"Execution denied: {decision.reason}",
            )

        return self.sandbox.execute(request)