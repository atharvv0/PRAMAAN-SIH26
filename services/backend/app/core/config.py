"""Central application settings."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "info"

    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_db: str = "pramaan"
    postgres_user: str = "pramaan"
    postgres_password: str = "changeme"
    database_url_override: str | None = Field(default=None, validation_alias="DATABASE_URL")

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    jwt_secret: str = "changeme"
    jwt_expiry_minutes: int = 60

    ollama_host: str = "localhost"
    ollama_port: int = 11434
    reasoning_model_name: str = "qwen3:4b"
    coding_model_name: str = "qwen3:4b"
    vision_model_name: str = "gemma3:4b"
    ocr_model_name: str = "gemma3:4b"
    embedding_model_name: str = "nomic-embed-text"
    ollama_no_cloud: str = "1"

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def ollama_base_url(self) -> str:
        return f"http://{self.ollama_host}:{self.ollama_port}"

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


settings = Settings()
