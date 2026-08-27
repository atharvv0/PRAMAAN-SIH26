import subprocess
import sys
import time

from services.sandbox.runner.contract import ExecutionRequest, ExecutionResult
from services.sandbox.policies.execution_policy import ExecutionPolicyValidator


class LocalRunner:
    def __init__(self):
        self.policy_validator = ExecutionPolicyValidator()

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        start_time = time.perf_counter()

        try:
            self.policy_validator.validate(
                timeout_seconds=request.policy.timeout_seconds,
                memory_mb=request.policy.memory_mb,
                network_enabled=request.policy.network_enabled,
            )

            process = subprocess.run(
                [sys.executable, "-c", request.code],
                input=request.stdin,
                capture_output=True,
                text=True,
                timeout=request.policy.timeout_seconds,
            )

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            status = "COMPLETED" if process.returncode == 0 else "FAILED"

            return ExecutionResult(
                request_id=request.request_id,
                status=status,
                stdout=process.stdout,
                stderr=process.stderr,
                exit_code=process.returncode,
                duration_ms=duration_ms,
            )

        except subprocess.TimeoutExpired as error:
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            return ExecutionResult(
                request_id=request.request_id,
                status="TIMEOUT",
                stdout=error.stdout or "",
                stderr=error.stderr or "",
                duration_ms=duration_ms,
                error="execution timed out",
            )

        except ValueError as error:
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            return ExecutionResult(
                request_id=request.request_id,
                status="REJECTED",
                duration_ms=duration_ms,
                error=str(error),
            )

        except Exception as error:
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            return ExecutionResult(
                request_id=request.request_id,
                status="ERROR",
                duration_ms=duration_ms,
                error=str(error),
            )