from app.db.session import SessionLocal
from app.models.task import Task
from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.file import File
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.task_file import TaskFile
from app.models.task_step import TaskStep
from app.models.tool import Tool
from app.models.model_capability import ModelCapability
from app.models.model import Model
from app.models.model_version import ModelVersion
from app.models.tool_call import ToolCall
from app.models.model_call import ModelCall
from app.models.evidence_record import EvidenceRecord
from app.models.approval import Approval
from app.models.deliverable import Deliverable
from app.models.audit_event import AuditEvent

db = SessionLocal()

try:
    tasks = db.query(Task).limit(5).all()
    users = db.query(User).limit(5).all()
    workspaces = db.query(Workspace).limit(5).all()
    projects = db.query(Project).limit(5).all()
    files = db.query(File).limit(5).all()
    knowledge_bases = db.query(KnowledgeBase).limit(5).all()
    documents = db.query(Document).limit(5).all()
    document_chunks = db.query(DocumentChunk).limit(5).all()
    task_files = db.query(TaskFile).limit(5).all()
    task_steps = db.query(TaskStep).limit(5).all()
    tools = db.query(Tool).limit(5).all()
    capabilities = db.query(ModelCapability).limit(5).all()
    models = db.query(Model).limit(5).all()
    model_versions = db.query(ModelVersion).limit(5).all()
    tool_calls = db.query(ToolCall).limit(5).all()
    model_calls = db.query(ModelCall).limit(5).all()
    evidence_records = db.query(EvidenceRecord).limit(5).all()
    approvals = db.query(Approval).limit(5).all()
    deliverables = db.query(Deliverable).limit(5).all()
    audit_events = db.query(AuditEvent).limit(5).all()


    print("Knowledge Bases found:", len(knowledge_bases))
    print("Tasks found:", len(tasks))
    print("Users found:", len(users))
    print("Workspaces found:", len(workspaces))
    print("Files found:", len(files))
    print("Projects found:", len(projects))
    print("Documents found:", len(documents))
    print("Document Chunks found:", len(document_chunks))
    print("Task Files found:", len(task_files))
    print("Task Steps found:", len(task_steps))
    print("Tools found:", len(tools))
    print("Model Capabilities found:", len(capabilities))
    print("Models found:", len(models))
    print("Model Versions found:", len(model_versions))
    print("Tool Calls found:", len(tool_calls))
    print("Model Calls found:", len(model_calls))
    print("Evidence Records found:", len(evidence_records))
    print("Approvals found:", len(approvals))
    print("Deliverables found:", len(deliverables))
    print("Audit Events found:", len(audit_events))

    for event in audit_events:
        print(
        "Audit Event:",
        event.audit_event_id,
        event.actor_type,
        event.action,
        event.target_type,
        event.decision
    )

    for deliverable in deliverables:
        print(
        "Deliverable:",
        deliverable.deliverable_id,
        deliverable.task_id,
        deliverable.file_id,
        deliverable.format,
        deliverable.version,
        deliverable.approval_state
    )

    for approval in approvals:
        print(
        "Approval:",
        approval.approval_id,
        approval.task_id,
        approval.requested_from,
        approval.status,
        approval.decision
    )  

    for evidence in evidence_records:
        print(
        "Evidence:",
        evidence.evidence_id,
        evidence.task_id,
        evidence.validation_status,
        evidence.confidence
    )

    for call in model_calls:
        print(
        "Model Call:",
        call.model_call_id,
        call.task_id,
        call.model_version_id,
        call.purpose,
        call.status
    )

    for call in tool_calls:
        print(
        "Tool Call:",
        call.tool_call_id,
        call.task_id,
        call.tool_id,
        call.agent_name,
        call.status
    )

    for mv in model_versions:
        print(
        "Model Version:",
        mv.model_version_id,
        mv.model_id,
        mv.version,
        mv.quantization,
        mv.vram_required_gb,
        mv.license,
        mv.status
    )

    for model in models:
        print(
        "Model:",
        model.model_id,
        model.name,
        model.runtime,
        model.status
    )

    for capability in capabilities:
        print(
        "Capability:",
        capability.model_version_id,
        capability.capability,
        capability.score
    )

    for tool in tools:
        print(
        "Tool:",
        tool.tool_id,
        tool.name,
        tool.tool_type,
        tool.status
    )

    for step in task_steps:
        print(
        "Task Step:",
        step.step_id,
        step.task_id,
        step.step_no,
        step.status
    )

    for task_file in task_files:
        print(
        "Task File:",
        task_file.task_id,
        task_file.file_id,
        task_file.role
    )

    for chunk in document_chunks:
        print(
        "Chunk:",
        chunk.chunk_id,
        chunk.document_id,
        chunk.chunk_index
    )

    for document in documents:
        print(
        "Document:",
        document.document_id,
        document.title,
        document.status
    )
    for user in users:
        print(
            "User:",
            user.user_id,
            user.email,
            user.display_name
        )
    for kb in knowledge_bases:
        print(
        "Knowledge Base:",
        kb.knowledge_base_id,
        kb.name,
        kb.status
    )

    for file in files:
        print(
        "File:",
        file.file_id,
        file.filename,
        file.mime_type
    )
    for workspace in workspaces:
        print(
            "Workspace:",
            workspace.workspace_id,
            workspace.name,
            workspace.sensitivity_class
        )
    
    for task in tasks:
        print(
        "Task:",
        task.task_id,
        task.project_id,
        task.title,
        task.status
    )
    for project in projects:
        print(
            "Project:",
            project.project_id,
            project.name,
            project.status
    ) 

finally:
    db.close()