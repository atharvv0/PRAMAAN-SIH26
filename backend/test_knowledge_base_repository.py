from app.db.session import SessionLocal

from app.repositories.knowledge_base_repository import (
    create_knowledge_base,
    get_knowledge_base,
    get_knowledge_bases_by_workspace,
    get_knowledge_bases,
)

from app.models.workspace import Workspace


db = SessionLocal()

try:

    workspace = db.query(Workspace).first()

    if workspace is None:
        print("No workspace found.")

    else:

        knowledge_base = create_knowledge_base(
            db=db,
            workspace_id=workspace.workspace_id,
            name="PRAMAAN Test Knowledge Base",
            description="Testing knowledge base repository",
            status="active",
        )

        print("Created Knowledge Base:")
        print(
            "Knowledge Base ID:",
            knowledge_base.knowledge_base_id,
        )
        print(
            "Workspace ID:",
            knowledge_base.workspace_id,
        )
        print(
            "Name:",
            knowledge_base.name,
        )
        print(
            "Description:",
            knowledge_base.description,
        )
        print(
            "Status:",
            knowledge_base.status,
        )

        found = get_knowledge_base(
            db,
            knowledge_base.knowledge_base_id,
        )

        print("\nGet Knowledge Base:")
        print(found.name)

        workspace_kbs = get_knowledge_bases_by_workspace(
            db,
            workspace.workspace_id,
        )

        print(
            "\nKnowledge Bases in Workspace:",
            len(workspace_kbs),
        )

        knowledge_bases = get_knowledge_bases(db)

        print(
            "Total Knowledge Bases:",
            len(knowledge_bases),
        )

finally:
    db.close()