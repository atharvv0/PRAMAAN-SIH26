from app.db.session import SessionLocal

from app.repositories.model_call_repository import (
    create_model_call,
    get_model_call,
    get_model_calls_by_task,
    get_model_calls_by_model_version,
    get_model_calls,
    update_model_call,
)

from app.models.task import Task
from app.models.model_version import ModelVersion


db = SessionLocal()

try:

    task = db.query(Task).first()
    model_version = db.query(ModelVersion).first()

    if task is None:
        print("No task found.")

    elif model_version is None:
        print("No model version found.")

    else:

        model_call = create_model_call(
            db=db,
            task_id=task.task_id,
            model_version_id=model_version.model_version_id,
            purpose="repository-test",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1200,
            status="completed",
        )

        print("Created Model Call:")
        print(
            "Model Call ID:",
            model_call.model_call_id,
        )
        print(
            "Task ID:",
            model_call.task_id,
        )
        print(
            "Model Version ID:",
            model_call.model_version_id,
        )
        print(
            "Purpose:",
            model_call.purpose,
        )
        print(
            "Input Tokens:",
            model_call.input_tokens,
        )
        print(
            "Output Tokens:",
            model_call.output_tokens,
        )
        print(
            "Latency:",
            model_call.latency_ms,
        )
        print(
            "Status:",
            model_call.status,
        )
        print(
            "Created At:",
            model_call.created_at,
        )

        found = get_model_call(
            db,
            model_call.model_call_id,
        )

        print("\nGet Model Call:")
        print(found.purpose)

        task_calls = get_model_calls_by_task(
            db,
            task.task_id,
        )

        print(
            "\nModel Calls for Task:",
            len(task_calls),
        )

        version_calls = get_model_calls_by_model_version(
            db,
            model_version.model_version_id,
        )

        print(
            "Calls for Model Version:",
            len(version_calls),
        )

        updated = update_model_call(
            db,
            model_call.model_call_id,
            output_tokens=75,
            latency_ms=1500,
            status="completed",
        )

        print("\nUpdated Model Call:")
        print(
            "Output Tokens:",
            updated.output_tokens,
        )
        print(
            "Latency:",
            updated.latency_ms,
        )
        print(
            "Status:",
            updated.status,
        )

        all_calls = get_model_calls(db)

        print(
            "\nTotal Model Calls:",
            len(all_calls),
        )

finally:
    db.close()
    