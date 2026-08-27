from sqlalchemy.orm import Session

from app.models.tool import Tool


def create_tool(
    db: Session,
    name: str,
    tool_type: str,
    status: str = "active",
):
    tool = Tool(
        name=name,
        tool_type=tool_type,
        status=status,
    )

    db.add(tool)
    db.commit()
    db.refresh(tool)

    return tool


def get_tool(
    db: Session,
    tool_id,
):
    return (
        db.query(Tool)
        .filter(Tool.tool_id == tool_id)
        .first()
    )


def get_tool_by_name(
    db: Session,
    name: str,
):
    return (
        db.query(Tool)
        .filter(Tool.name == name)
        .first()
    )


def get_tools(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(Tool)
        .limit(limit)
        .all()
    )


def get_tools_by_type(
    db: Session,
    tool_type: str,
):
    return (
        db.query(Tool)
        .filter(Tool.tool_type == tool_type)
        .all()
    )


def update_tool(
    db: Session,
    tool_id,
    name: str = None,
    tool_type: str = None,
    status: str = None,
):
    tool = get_tool(db, tool_id)

    if tool is None:
        return None

    if name is not None:
        tool.name = name

    if tool_type is not None:
        tool.tool_type = tool_type

    if status is not None:
        tool.status = status

    db.commit()
    db.refresh(tool)

    return tool


def delete_tool(
    db: Session,
    tool_id,
):
    tool = get_tool(db, tool_id)

    if tool is None:
        return False

    db.delete(tool)
    db.commit()

    return True
    