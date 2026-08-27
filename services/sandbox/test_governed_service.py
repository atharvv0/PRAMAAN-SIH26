from services.sandbox.governed_service import GovernedSandboxService
from services.sandbox.runner.contract import ExecutionRequest
from services.governance.security.models import PolicyDecision


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

    decision = PolicyDecision(
        decision="ALLOW",
        reason="Role is authorized to use this tool",
        role="admin",
        action="execute_command",
        timestamp="test",
    )

    result = service.execute(
        decision,
        make_request("governed-allow", "print(2 + 3)")
    )

    assert result.status == "COMPLETED"
    assert result.stdout == "5\n"


def test_denied_execution():
    service = GovernedSandboxService()

    decision = PolicyDecision(
        decision="DENY",
        reason="Role is not authorized to use this tool",
        role="user",
        action="execute_command",
        timestamp="test",
    )

    result = service.execute(
        decision,
        make_request("governed-deny", "print(2 + 3)")
    )

    assert result.status == "REJECTED"
    assert "Execution denied" in result.error


if __name__ == "__main__":
    test_allowed_execution()
    test_denied_execution()
    print("All GovernedSandboxService tests passed.")