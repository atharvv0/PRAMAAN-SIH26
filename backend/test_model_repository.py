from app.db.session import SessionLocal

from app.repositories.model_repository import (
    create_model,
    get_model,
    get_model_by_name,
    get_models,
    get_models_by_runtime,
)


db = SessionLocal()

try:

    # Avoid creating the same test model repeatedly
    existing = get_model_by_name(
        db,
        "PRAMAAN Test Model",
    )

    if existing:
        model = existing

        print("Model already exists:")
        print("Model ID:", model.model_id)
        print("Name:", model.name)
        print("Provider:", model.provider_family)
        print("Runtime:", model.runtime)
        print("Status:", model.status)

    else:

        model = create_model(
            db=db,
            name="PRAMAAN Test Model",
            provider_family="open-weight",
            runtime="transformers",
            status="active",
        )

        print("Created Model:")
        print("Model ID:", model.model_id)
        print("Name:", model.name)
        print("Provider:", model.provider_family)
        print("Runtime:", model.runtime)
        print("Status:", model.status)

    found = get_model(
        db,
        model.model_id,
    )

    print("\nGet Model:")
    print(found.name)

    runtime_models = get_models_by_runtime(
        db,
        model.runtime,
    )

    print(
        "\nModels using runtime:",
        len(runtime_models),
    )

    models = get_models(db)

    print(
        "Total Models:",
        len(models),
    )

finally:
    db.close()