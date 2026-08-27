import os

from services.sandbox.runner.local_runner import LocalRunner
from services.sandbox.runner.runtime import ExecutionRuntime


def create_runtime() -> ExecutionRuntime:
    runtime = os.getenv("SANDBOX_RUNTIME", "local").lower()

    if runtime == "local":
        return LocalRunner()

    raise ValueError(f"Unsupported sandbox runtime: {runtime}")