"""In-process application store for the current MVP.

The repository boundary is intentionally small so it can be replaced by a
PostgreSQL repository later without changing API contracts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

TASKS: dict[str, dict[str, Any]] = {}
RUNS: dict[str, dict[str, Any]] = {}
DELIVERABLES: dict[str, dict[str, Any]] = {}
AUDIT_EVENTS: list[dict[str, Any]] = []
WORKSPACES: dict[str, dict[str, Any]] = {
    "ws-default": {
        "id": "ws-default",
        "name": "PRAMAAN Sovereign Workspace",
        "description": "Local-first workspace for sovereign agent execution and evidence review.",
        "documentCount": 0,
        "activeTasks": 0,
        "pendingApprovals": 0,
        "deliverableCount": 0,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_audit(**event: Any) -> dict[str, Any]:
    record = {"id": event.get("id") or f"aud_{len(AUDIT_EVENTS) + 1}", "timestamp": event.get("timestamp") or now_iso(), **event}
    AUDIT_EVENTS.insert(0, record)
    return record
