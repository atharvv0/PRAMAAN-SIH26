from services.sandbox.service import SandboxService
from services.sandbox.runner.contract import ExecutionRequest


def test_sandbox_service():
    service = SandboxService()

    request = ExecutionRequest(
        request_id="service-test",
        workspace_id=None,
        project_id=None,
        task_id=None,
        language="python",
        code="print(2 + 3)",
    )

    result = service.execute(request)

    assert result.status == "COMPLETED"
    assert result.stdout == "5\n"
    assert result.exit_code == 0


if __name__ == "__main__":
    test_sandbox_service()
    print("All SandboxService tests passed.")