from sqlalchemy.orm import Session

from app.repositories.tool_repository import (
    create_tool,
    get_tool,
    get_tool_by_name,
    get_tools,
    get_tools_by_type,
    update_tool,
    delete_tool,
)


VALID_STATUSES = {
    "active",
    "inactive",
}


def create_tool_service(
    db: Session,
    name: str,
    tool_type: str,
    status: str = "active",
):
    # Validate name
    if not name or not name.strip():
        raise ValueError("Tool name is required.")

    # Validate tool type
    if not tool_type or not tool_type.strip():
        raise ValueError("Tool type is required.")

    # Validate status
    if status not in VALID_STATUSES:
        raise ValueError("Invalid tool status.")

    # Check duplicate tool name
    existing = get_tool_by_name(
        db,
        name.strip(),
    )

    if existing is not None:
        raise ValueError(
            "A tool with this name already exists."
        )

    return create_tool(
        db=db,
        name=name.strip(),
        tool_type=tool_type.strip(),
        status=status,
    )


def get_tool_service(
    db: Session,
    tool_id,
):
    tool = get_tool(
        db,
        tool_id,
    )

    if tool is None:
        raise ValueError("Tool not found.")

    return tool


def get_tool_by_name_service(
    db: Session,
    name: str,
):
    if not name or not name.strip():
        raise ValueError("Tool name is required.")

    tool = get_tool_by_name(
        db,
        name.strip(),
    )

    if tool is None:
        raise ValueError("Tool not found.")

    return tool


def get_tools_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_tools(
        db,
        limit=limit,
    )


def get_tools_by_type_service(
    db: Session,
    tool_type: str,
):
    if not tool_type or not tool_type.strip():
        raise ValueError(
            "Tool type is required."
        )

    return get_tools_by_type(
        db,
        tool_type.strip(),
    )


def update_tool_service(
    db: Session,
    tool_id,
    name: str = None,
    tool_type: str = None,
    status: str = None,
):
    # Validate name
    if name is not None:
        if not name.strip():
            raise ValueError(
                "Tool name cannot be empty."
            )

        name = name.strip()

        # Check duplicate name
        existing = get_tool_by_name(
            db,
            name,
        )

        if (
            existing is not None
            and existing.tool_id != tool_id
        ):
            raise ValueError(
                "A tool with this name already exists."
            )

    # Validate tool type
    if tool_type is not None:
        if not tool_type.strip():
            raise ValueError(
                "Tool type cannot be empty."
            )

        tool_type = tool_type.strip()

    # Validate status
    if status is not None:
        if status not in VALID_STATUSES:
            raise ValueError(
                "Invalid tool status."
            )

    tool = update_tool(
        db=db,
        tool_id=tool_id,
        name=name,
        tool_type=tool_type,
        status=status,
    )

    if tool is None:
        raise ValueError("Tool not found.")

    return tool


def delete_tool_service(
    db: Session,
    tool_id,
):
    deleted = delete_tool(
        db,
        tool_id,
    )

    if not deleted:
        raise ValueError("Tool not found.")

    return True