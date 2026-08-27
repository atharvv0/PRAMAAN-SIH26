from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.task_service import (
    create_task_service,
    get_task_service,
    get_tasks_service,
    update_task_service,
    delete_task_service,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreateRequest(BaseModel):
    project_id: UUID
    created_by: UUID
    title: str
    intent: str


class TaskUpdateRequest(BaseModel):
    title: str | None = None
    intent: str | None = None
    status: str | None = None
    sensitivity_class: str | None = None


def task_to_dict(task):
    return {
        "task_id": str(task.task_id),
        "project_id": str(task.project_id),
        "created_by": str(task.created_by),
        "title": task.title,
        "intent": task.intent,
        "status": task.status,
        "sensitivity_class": task.sensitivity_class,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.post("", status_code=201)
def create_task(
    payload: TaskCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        task = create_task_service(
            db=db,
            project_id=payload.project_id,
            created_by=payload.created_by,
            title=payload.title,
            intent=payload.intent,
        )
        return task_to_dict(task)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("/{task_id}")
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        task = get_task_service(
            db=db,
            task_id=task_id,
        )
        return task_to_dict(task)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("")
def get_tasks(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        tasks = get_tasks_service(
            db=db,
            limit=limit,
        )

        return [task_to_dict(task) for task in tasks]

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.put("/{task_id}")
def update_task(
    task_id: UUID,
    payload: TaskUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        task = update_task_service(
            db=db,
            task_id=task_id,
            title=payload.title,
            intent=payload.intent,
            status=payload.status,
            sensitivity_class=payload.sensitivity_class,
        )

        return task_to_dict(task)

    except ValueError as exc:
        if str(exc) == "Task not found.":
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.delete("/{task_id}")
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        delete_task_service(
            db=db,
            task_id=task_id,
        )

        return {
            "message": "Task deleted successfully"
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
