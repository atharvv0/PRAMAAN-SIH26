from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExecutionPolicy:
    timeout_seconds: int = 30
    memory_mb: int = 1024
    network_enabled: bool = False


@dataclass
class ExecutionRequest:
    request_id: str
    workspace_id: Optional[str]
    project_id: Optional[str]
    task_id: Optional[str]
    language: str
    code: str
    stdin: str = ""
    policy: ExecutionPolicy = field(default_factory=ExecutionPolicy)


@dataclass
class ExecutionResult:
    request_id: str
    status: str
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None