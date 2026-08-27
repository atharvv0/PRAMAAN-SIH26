import os

from services.sandbox.runner.firecracker_runtime import FirecrackerRuntime
from services.sandbox.runner.local_runner import LocalRunner
from services.sandbox.runner.runtime import ExecutionRuntime


def create_runtime() -> ExecutionRuntime:
    runtime = os.getenv("SANDBOX_RUNTIME", "local").lower()

    if runtime == "local":
        return LocalRunner()

    if runtime == "firecracker":
        return FirecrackerRuntime()

    raise ValueError(f"Unsupported sandbox runtime: {runtime}")