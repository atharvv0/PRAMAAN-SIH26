"""
Central settings object. Never hard-code config elsewhere — read it from here.
Values come from environment variables / .env (see .env.example at repo root).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "info"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "pramaan"
    postgres_user: str = "pramaan"
    postgres_password: str = "changeme"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    jwt_secret: str = "changeme"
    jwt_expiry_minutes: int = 60

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
