from services.sandbox.runner.contract import ExecutionRequest, ExecutionResult
from services.sandbox.runner.runtime import ExecutionRuntime


class FirecrackerRuntime(ExecutionRuntime):
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(
            request_id=request.request_id,
            status="ERROR",
            error="Firecracker runtime is not available",
        )