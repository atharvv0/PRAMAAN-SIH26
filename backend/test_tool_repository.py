from app.db.session import SessionLocal

from app.repositories.tool_repository import (
    create_tool,
    get_tool,
    get_tool_by_name,
    get_tools,
    get_tools_by_type,
)


db = SessionLocal()

try:

    existing = get_tool_by_name(
        db,
        "PRAMAAN Test Tool",
    )

    if existing:
        tool = existing

        print("Tool already exists:")
        print("Tool ID:", tool.tool_id)
        print("Name:", tool.name)
        print("Type:", tool.tool_type)
        print("Status:", tool.status)

    else:

        tool = create_tool(
            db=db,
            name="PRAMAAN Test Tool",
            tool_type="document_search",
            status="active",
        )

        print("Created Tool:")
        print("Tool ID:", tool.tool_id)
        print("Name:", tool.name)
        print("Type:", tool.tool_type)
        print("Status:", tool.status)

    found = get_tool(
        db,
        tool.tool_id,
    )

    print("\nGet Tool:")
    print(found.name)

    type_tools = get_tools_by_type(
        db,
        tool.tool_type,
    )

    print(
        "\nTools of this type:",
        len(type_tools),
    )

    tools = get_tools(db)

    print(
        "Total Tools:",
        len(tools),
    )

finally:
    db.close()