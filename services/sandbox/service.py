from services.sandbox.runner.contract import ExecutionRequest, ExecutionResult
from services.sandbox.runner.runtime_factory import create_runtime


class SandboxService:
    def __init__(self):
        self.runtime = create_runtime()

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return self.runtime.execute(request)