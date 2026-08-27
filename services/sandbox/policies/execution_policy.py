from dataclasses import dataclass


@dataclass(frozen=True)
class SandboxLimits:
    max_timeout_seconds: int = 30
    max_memory_mb: int = 1024


class ExecutionPolicyValidator:
    def __init__(self, limits: SandboxLimits | None = None):
        self.limits = limits or SandboxLimits()

    def validate(self, timeout_seconds: int, memory_mb: int, network_enabled: bool) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")

        if timeout_seconds > self.limits.max_timeout_seconds:
            raise ValueError(
                f"timeout_seconds cannot exceed {self.limits.max_timeout_seconds}"
            )

        if memory_mb <= 0:
            raise ValueError("memory_mb must be greater than 0")

        if memory_mb > self.limits.max_memory_mb:
            raise ValueError(
                f"memory_mb cannot exceed {self.limits.max_memory_mb}"
            )

        if network_enabled:
            raise ValueError("network access is disabled in the sandbox")