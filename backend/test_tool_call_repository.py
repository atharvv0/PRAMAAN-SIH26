from datetime import datetime, timezone

from app.db.session import SessionLocal

from app.repositories.tool_call_repository import (
    create_tool_call,
    get_tool_call,
    get_tool_calls_by_task,
    get_tool_calls_by_tool,
    get_tool_calls,
    update_tool_call,
)

from app.models.task import Task
from app.models.tool import Tool


db = SessionLocal()

try:

    task = db.query(Task).first()
    tool = db.query(Tool).first()

    if task is None:
        print("No task found.")

    elif tool is None:
        print("No tool found.")

    else:

        tool_call = create_tool_call(
            db=db,
            task_id=task.task_id,
            tool_id=tool.tool_id,
            agent_name="PRAMAAN-Test-Agent",
            args_json={
                "query": "test inspection report"
            },
            status="pending",
        )

        print("Created Tool Call:")
        print("Tool Call ID:", tool_call.tool_call_id)
        print("Task ID:", tool_call.task_id)
        print("Tool ID:", tool_call.tool_id)
        print("Agent:", tool_call.agent_name)
        print("Args:", tool_call.args_json)
        print("Status:", tool_call.status)
        print("Started At:", tool_call.started_at)

        found = get_tool_call(
            db,
            tool_call.tool_call_id,
        )

        print("\nGet Tool Call:")
        print(found.agent_name)

        updated = update_tool_call(
            db,
            tool_call.tool_call_id,
            result_json={
                "result": "test successful"
            },
            status="completed",
            ended_at=datetime.now(timezone.utc),
        )

        print("\nUpdated Tool Call:")
        print("Status:", updated.status)
        print("Result:", updated.result_json)
        print("Ended At:", updated.ended_at)

        task_calls = get_tool_calls_by_task(
            db,
            task.task_id,
        )

        print(
            "\nTool Calls for Task:",
            len(task_calls),
        )

        tool_calls_for_tool = get_tool_calls_by_tool(
            db,
            tool.tool_id,
        )

        print(
            "Calls for Tool:",
            len(tool_calls_for_tool),
        )

        all_calls = get_tool_calls(db)

        print(
            "Total Tool Calls:",
            len(all_calls),
        )

finally:
    db.close()