from uuid import uuid4

from app.db.session import SessionLocal

from app.services.tool_service import (
    create_tool_service,
    get_tool_service,
    get_tool_by_name_service,
    get_tools_by_type_service,
    get_tools_service,
    update_tool_service,
    delete_tool_service,
)


db = SessionLocal()

# Unique name so repeated test runs do not fail
tool_name = f"PRAMAAN-Test-Tool-{uuid4().hex[:8]}"
updated_tool_name = f"{tool_name}-Updated"

try:

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    tool = create_tool_service(
        db=db,
        name=tool_name,
        tool_type="document_parser",
        status="active",
    )

    print("Created Tool:")
    print("ID:", tool.tool_id)
    print("Name:", tool.name)
    print("Type:", tool.tool_type)
    print("Status:", tool.status)

    # --------------------------------------------------
    # GET BY ID
    # --------------------------------------------------

    found = get_tool_service(
        db,
        tool.tool_id,
    )

    print("\nGet Tool:")
    print("Name:", found.name)

    # --------------------------------------------------
    # GET BY NAME
    # --------------------------------------------------

    found_by_name = get_tool_by_name_service(
        db,
        tool_name,
    )

    print("\nGet Tool By Name:")
    print("ID:", found_by_name.tool_id)

    # --------------------------------------------------
    # GET BY TYPE
    # --------------------------------------------------

    tools_by_type = get_tools_by_type_service(
        db,
        "document_parser",
    )

    print("\nTools By Type:")
    print("Count:", len(tools_by_type))

    # --------------------------------------------------
    # GET ALL
    # --------------------------------------------------

    tools = get_tools_service(
        db,
        limit=100,
    )

    print("\nTotal Tools:")
    print(len(tools))

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    updated = update_tool_service(
        db=db,
        tool_id=tool.tool_id,
        name=updated_tool_name,
        tool_type="document_parser",
        status="inactive",
    )

    print("\nUpdated Tool:")
    print("Name:", updated.name)
    print("Type:", updated.tool_type)
    print("Status:", updated.status)

    # --------------------------------------------------
    # GET UPDATED TOOL
    # --------------------------------------------------

    updated_found = get_tool_service(
        db,
        tool.tool_id,
    )

    print("\nVerified Updated Tool:")
    print("Name:", updated_found.name)
    print("Status:", updated_found.status)

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------

    deleted = delete_tool_service(
        db,
        tool.tool_id,
    )

    print("\nDeleted Tool:")
    print(deleted)

finally:
    db.close()