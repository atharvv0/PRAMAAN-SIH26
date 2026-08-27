from app.db.session import SessionLocal

from app.services.task_service import (
    get_tasks_service,
)

from app.services.tool_service import (
    get_tools_service,
)

from app.services.tool_call_service import (
    create_tool_call_service,
    get_tool_call_service,
    get_tool_calls_by_task_service,
    get_tool_calls_by_tool_service,
    get_tool_calls_service,
    update_tool_call_service,
)


db = SessionLocal()

try:

    # --------------------------------------------------
    # GET EXISTING TASK
    # --------------------------------------------------

    tasks = get_tasks_service(
        db,
        limit=1,
    )

    if not tasks:
        raise ValueError(
            "No task found. Create a task first."
        )

    task = tasks[0]


    # --------------------------------------------------
    # GET EXISTING TOOL
    # --------------------------------------------------

    tools = get_tools_service(
        db,
        limit=1,
    )

    if not tools:
        raise ValueError(
            "No tool found. Create a tool first."
        )

    tool = tools[0]


    # --------------------------------------------------
    # CREATE TOOL CALL
    # --------------------------------------------------

    tool_call = create_tool_call_service(
        db=db,
        task_id=task.task_id,
        tool_id=tool.tool_id,
        agent_name="PRAMAAN-Test-Agent",
        args_json={
            "test": True,
            "message": "Tool call service test",
        },
        status="pending",
    )

    print("Created Tool Call:")
    print("ID:", tool_call.tool_call_id)
    print("Task ID:", tool_call.task_id)
    print("Tool ID:", tool_call.tool_id)
    print("Agent:", tool_call.agent_name)
    print("Status:", tool_call.status)


    # --------------------------------------------------
    # GET BY ID
    # --------------------------------------------------

    found = get_tool_call_service(
        db,
        tool_call.tool_call_id,
    )

    print("\nGet Tool Call:")
    print(found.tool_call_id)


    # --------------------------------------------------
    # GET BY TASK
    # --------------------------------------------------

    task_calls = get_tool_calls_by_task_service(
        db,
        task.task_id,
    )

    print(
        "\nTool Calls By Task:",
        len(task_calls),
    )


    # --------------------------------------------------
    # GET BY TOOL
    # --------------------------------------------------

    tool_calls = get_tool_calls_by_tool_service(
        db,
        tool.tool_id,
    )

    print(
        "Tool Calls By Tool:",
        len(tool_calls),
    )


    # --------------------------------------------------
    # GET ALL
    # --------------------------------------------------

    all_calls = get_tool_calls_service(
        db,
        limit=100,
    )

    print(
        "Total Tool Calls:",
        len(all_calls),
    )


    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    updated = update_tool_call_service(
        db=db,
        tool_call_id=tool_call.tool_call_id,
        result_json={
            "success": True,
            "output": "Test completed successfully",
        },
        status="completed",
    )

    print("\nUpdated Tool Call:")
    print("Status:", updated.status)
    print("Result:", updated.result_json)
    print("Ended At:", updated.ended_at)


finally:
    db.close()