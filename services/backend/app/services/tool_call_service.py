from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories.tool_call_repository import (
    create_tool_call,
    get_tool_call,
    get_tool_calls_by_task,
    get_tool_calls_by_tool,
    get_tool_calls,
    update_tool_call,
)


VALID_STATUSES = {
    "pending",
    "running",
    "completed",
    "failed",
}


def create_tool_call_service(
    db: Session,
    task_id,
    tool_id,
    agent_name: str,
    args_json: dict = None,
    status: str = "pending",
):
    if not agent_name or not agent_name.strip():
        raise ValueError(
            "Agent name is required."
        )

    if status not in VALID_STATUSES:
        raise ValueError(
            "Invalid tool call status."
        )

    return create_tool_call(
        db=db,
        task_id=task_id,
        tool_id=tool_id,
        agent_name=agent_name.strip(),
        args_json=args_json,
        status=status,
    )


def get_tool_call_service(
    db: Session,
    tool_call_id,
):
    tool_call = get_tool_call(
        db,
        tool_call_id,
    )

    if tool_call is None:
        raise ValueError(
            "Tool call not found."
        )

    return tool_call


def get_tool_calls_by_task_service(
    db: Session,
    task_id,
):
    return get_tool_calls_by_task(
        db,
        task_id,
    )


def get_tool_calls_by_tool_service(
    db: Session,
    tool_id,
):
    return get_tool_calls_by_tool(
        db,
        tool_id,
    )


def get_tool_calls_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_tool_calls(
        db,
        limit=limit,
    )


def update_tool_call_service(
    db: Session,
    tool_call_id,
    result_json: dict = None,
    status: str = None,
    ended_at=None,
    error_message: str = None,
):
    if status is not None and status not in VALID_STATUSES:
        raise ValueError(
            "Invalid tool call status."
        )

    if status == "completed" and ended_at is None:
        ended_at = datetime.now(timezone.utc)

    if status == "failed" and ended_at is None:
        ended_at = datetime.now(timezone.utc)

    if status == "failed":
        if not error_message or not error_message.strip():
            raise ValueError(
                "Error message is required when tool call fails."
            )

        error_message = error_message.strip()

    tool_call = update_tool_call(
        db=db,
        tool_call_id=tool_call_id,
        result_json=result_json,
        status=status,
        ended_at=ended_at,
        error_message=error_message,
    )

    if tool_call is None:
        raise ValueError(
            "Tool call not found."
        )

    return tool_call