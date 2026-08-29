from services.sandbox.governed_service import GovernedSandboxService
from services.sandbox.runner.contract import ExecutionRequest


def make_request(request_id, code):
    return ExecutionRequest(
        request_id=request_id,
        workspace_id=None,
        project_id=None,
        task_id=None,
        language="python",
        code=code,
    )


def test_allowed_execution():
    service = GovernedSandboxService()

    result = service.execute(
        "demo-admin",
        make_request("governed-allow", "print(2 + 3)"),
    )

    assert result.status == "COMPLETED"
    assert result.stdout == "5\n"


def test_denied_execution():
    service = GovernedSandboxService()

    result = service.execute(
        "demo-user",
        make_request("governed-deny", "print(2 + 3)"),
    )

    assert result.status == "REJECTED"
    assert "Execution denied" in result.error


if __name__ == "__main__":
    test_allowed_execution()
    test_denied_execution()
    print("All GovernedSandboxService tests passed.")