from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.tool_call import ToolCall


def create_tool_call(
    db: Session,
    task_id,
    tool_id,
    agent_name: str,
    args_json: dict = None,
    status: str = "pending",
):
    tool_call = ToolCall(
        task_id=task_id,
        tool_id=tool_id,
        agent_name=agent_name,
        args_json=args_json,
        status=status,
        started_at=datetime.now(timezone.utc),
    )

    db.add(tool_call)
    db.commit()
    db.refresh(tool_call)

    return tool_call


def get_tool_call(
    db: Session,
    tool_call_id,
):
    return (
        db.query(ToolCall)
        .filter(ToolCall.tool_call_id == tool_call_id)
        .first()
    )


def get_tool_calls_by_task(
    db: Session,
    task_id,
):
    return (
        db.query(ToolCall)
        .filter(ToolCall.task_id == task_id)
        .order_by(ToolCall.started_at)
        .all()
    )


def get_tool_calls_by_tool(
    db: Session,
    tool_id,
):
    return (
        db.query(ToolCall)
        .filter(ToolCall.tool_id == tool_id)
        .order_by(ToolCall.started_at)
        .all()
    )


def get_tool_calls(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(ToolCall)
        .order_by(ToolCall.started_at)
        .limit(limit)
        .all()
    )


def update_tool_call(
    db: Session,
    tool_call_id,
    result_json: dict = None,
    status: str = None,
    ended_at=None,
    error_message: str = None,
):
    tool_call = get_tool_call(
        db,
        tool_call_id,
    )

    if tool_call is None:
        return None

    if result_json is not None:
        tool_call.result_json = result_json

    if status is not None:
        tool_call.status = status

    if ended_at is not None:
        tool_call.ended_at = ended_at

    if error_message is not None:
        tool_call.error_message = error_message

    db.commit()
    db.refresh(tool_call)

    return tool_call