from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeBase


def create_knowledge_base(
    db: Session,
    workspace_id,
    name: str,
    description: str = None,
    status: str = "active",
):
    knowledge_base = KnowledgeBase(
        workspace_id=workspace_id,
        name=name,
        description=description,
        status=status,
    )

    db.add(knowledge_base)
    db.commit()
    db.refresh(knowledge_base)

    return knowledge_base


def get_knowledge_base(
    db: Session,
    knowledge_base_id,
):
    return (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.knowledge_base_id == knowledge_base_id
        )
        .first()
    )


def get_knowledge_bases_by_workspace(
    db: Session,
    workspace_id,
):
    return (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.workspace_id == workspace_id
        )
        .all()
    )


def get_knowledge_bases(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(KnowledgeBase)
        .limit(limit)
        .all()
    )


def update_knowledge_base(
    db: Session,
    knowledge_base_id,
    name: str = None,
    description: str = None,
    status: str = None,
):
    knowledge_base = get_knowledge_base(
        db,
        knowledge_base_id,
    )

    if knowledge_base is None:
        return None

    if name is not None:
        knowledge_base.name = name

    if description is not None:
        knowledge_base.description = description

    if status is not None:
        knowledge_base.status = status

    db.commit()
    db.refresh(knowledge_base)

    return knowledge_base


def delete_knowledge_base(
    db: Session,
    knowledge_base_id,
):
    knowledge_base = get_knowledge_base(
        db,
        knowledge_base_id,
    )

    if knowledge_base is None:
        return False

    db.delete(knowledge_base)
    db.commit()

    return True