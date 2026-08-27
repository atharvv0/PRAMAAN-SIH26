from contract import ExecutionPolicy, ExecutionRequest
from local_runner import LocalRunner


request = ExecutionRequest(
    request_id="test-003",
    workspace_id=None,
    project_id=None,
    task_id=None,
    language="python",
    code="while True: pass",
    policy=ExecutionPolicy(timeout_seconds=2),
)

runner = LocalRunner()
result = runner.execute(request)

print(result)