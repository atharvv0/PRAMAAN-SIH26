from app.db.session import SessionLocal

from app.services.task_service import (
    get_tasks_service,
)

from app.services.model_version_service import (
    get_model_versions_service,
)

from app.services.model_call_service import (
    create_model_call_service,
    get_model_call_service,
    get_model_calls_by_task_service,
    get_model_calls_by_model_version_service,
    get_model_calls_service,
    update_model_call_service,
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
    # GET EXISTING MODEL VERSION
    # --------------------------------------------------

    versions = get_model_versions_service(
        db,
        limit=1,
    )

    if not versions:
        raise ValueError(
            "No model version found. Create one first."
        )

    model_version = versions[0]


    # --------------------------------------------------
    # CREATE MODEL CALL
    # --------------------------------------------------

    model_call = create_model_call_service(
        db=db,
        task_id=task.task_id,
        model_version_id=model_version.model_version_id,
        purpose="PRAMAAN model call service test",
        input_tokens=100,
        output_tokens=50,
        latency_ms=250,
        status="pending",
    )

    print("Created Model Call:")
    print("ID:", model_call.model_call_id)
    print("Task ID:", model_call.task_id)
    print("Model Version ID:", model_call.model_version_id)
    print("Purpose:", model_call.purpose)
    print("Input Tokens:", model_call.input_tokens)
    print("Output Tokens:", model_call.output_tokens)
    print("Latency:", model_call.latency_ms)
    print("Status:", model_call.status)


    # --------------------------------------------------
    # GET BY ID
    # --------------------------------------------------

    found = get_model_call_service(
        db,
        model_call.model_call_id,
    )

    print("\nGet Model Call:")
    print(found.model_call_id)


    # --------------------------------------------------
    # GET BY TASK
    # --------------------------------------------------

    task_calls = get_model_calls_by_task_service(
        db,
        task.task_id,
    )

    print(
        "\nModel Calls By Task:",
        len(task_calls),
    )


    # --------------------------------------------------
    # GET BY MODEL VERSION
    # --------------------------------------------------

    version_calls = (
        get_model_calls_by_model_version_service(
            db,
            model_version.model_version_id,
        )
    )

    print(
        "Model Calls By Model Version:",
        len(version_calls),
    )


    # --------------------------------------------------
    # GET ALL
    # --------------------------------------------------

    all_calls = get_model_calls_service(
        db,
        limit=100,
    )

    print(
        "Total Model Calls:",
        len(all_calls),
    )


    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    updated = update_model_call_service(
        db=db,
        model_call_id=model_call.model_call_id,
        output_tokens=75,
        latency_ms=300,
        status="completed",
    )

    print("\nUpdated Model Call:")
    print("Output Tokens:", updated.output_tokens)
    print("Latency:", updated.latency_ms)
    print("Status:", updated.status)


finally:
    db.close()