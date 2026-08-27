from services.sandbox.runner.contract import ExecutionRequest
from services.sandbox.runner.firecracker_runtime import FirecrackerRuntime


def test_firecracker_unavailable():
    runtime = FirecrackerRuntime()

    request = ExecutionRequest(
        request_id="test-firecracker",
        workspace_id=None,
        project_id=None,
        task_id=None,
        language="python",
        code="print(5)",
    )

    result = runtime.execute(request)

    assert result.status == "ERROR"
    assert result.error == "Firecracker runtime is not available"


if __name__ == "__main__":
    test_firecracker_unavailable()
    print("All FirecrackerRuntime tests passed.")