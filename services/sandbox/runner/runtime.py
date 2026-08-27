from abc import ABC, abstractmethod

from services.sandbox.runner.contract import ExecutionRequest, ExecutionResult


class ExecutionRuntime(ABC):
    @abstractmethod
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        pass