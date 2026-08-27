from contract import ExecutionPolicy, ExecutionRequest
from local_runner import LocalRunner


runner = LocalRunner()


def test_successful_execution():
    request = ExecutionRequest(
        request_id="test-success",
        workspace_id=None,
        project_id=None,
        task_id=None,
        language="python",
        code="print(2 + 3)",
    )

    result = runner.execute(request)

    assert result.status == "COMPLETED"
    assert result.stdout == "5\n"
    assert result.exit_code == 0


def test_failed_execution():
    request = ExecutionRequest(
        request_id="test-failure",
        workspace_id=None,
        project_id=None,
        task_id=None,
        language="python",
        code="print(undefined_variable)",
    )

    result = runner.execute(request)

    assert result.status == "FAILED"
    assert result.exit_code != 0
    assert "NameError" in result.stderr


def test_timeout():
    request = ExecutionRequest(
        request_id="test-timeout",
        workspace_id=None,
        project_id=None,
        task_id=None,
        language="python",
        code="while True: pass",
        policy=ExecutionPolicy(timeout_seconds=2),
    )

    result = runner.execute(request)

    assert result.status == "TIMEOUT"
    assert result.error == "execution timed out"


if __name__ == "__main__":
    test_successful_execution()
    test_failed_execution()
    test_timeout()
    print("All LocalRunner tests passed.")