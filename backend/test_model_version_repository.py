from app.db.session import SessionLocal

from app.repositories.model_repository import get_models

from app.repositories.model_version_repository import (
    create_model_version,
    get_model_version,
    get_model_versions_by_model,
    get_model_version_by_version,
    get_model_versions,
)


db = SessionLocal()

try:

    model = get_models(db, limit=1)

    if not model:
        print("No model found. Create a model first.")

    else:

        model = model[0]

        existing = get_model_version_by_version(
            db,
            model.model_id,
            "1.0-test",
        )

        if existing:
            model_version = existing

            print("Model Version already exists:")
            print(
                "Model Version ID:",
                model_version.model_version_id,
            )
            print(
                "Model ID:",
                model_version.model_id,
            )
            print(
                "Version:",
                model_version.version,
            )
            print(
                "Weights Path:",
                model_version.weights_path,
            )
            print(
                "Quantization:",
                model_version.quantization,
            )
            print(
                "VRAM:",
                model_version.vram_required_gb,
            )
            print(
                "License:",
                model_version.license,
            )
            print(
                "Status:",
                model_version.status,
            )

        else:

            model_version = create_model_version(
                db=db,
                model_id=model.model_id,
                version="1.0-test",
                weights_path="models/test/model",
                quantization="4bit",
                vram_required_gb=8.0,
                license="Apache-2.0",
                status="active",
            )

            print("Created Model Version:")
            print(
                "Model Version ID:",
                model_version.model_version_id,
            )
            print(
                "Model ID:",
                model_version.model_id,
            )
            print(
                "Version:",
                model_version.version,
            )
            print(
                "Weights Path:",
                model_version.weights_path,
            )
            print(
                "Quantization:",
                model_version.quantization,
            )
            print(
                "VRAM:",
                model_version.vram_required_gb,
            )
            print(
                "License:",
                model_version.license,
            )
            print(
                "Status:",
                model_version.status,
            )

        found = get_model_version(
            db,
            model_version.model_version_id,
        )

        print("\nGet Model Version:")
        print(found.version)

        versions_for_model = get_model_versions_by_model(
            db,
            model.model_id,
        )

        print(
            "\nVersions for Model:",
            len(versions_for_model),
        )

        version = get_model_version_by_version(
            db,
            model.model_id,
            "1.0-test",
        )

        print(
            "Get by Version:",
            version.version if version else None,
        )

        all_versions = get_model_versions(db)

        print(
            "Total Model Versions:",
            len(all_versions),
        )

finally:
    db.close()