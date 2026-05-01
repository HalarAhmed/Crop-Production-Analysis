from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    # Database
    # Default keeps imports/runs working; override in `.env` for your real DB.
    database_url: str = "postgresql+psycopg2://postgres:password@localhost:5432/dbms-project"

    # ML
    ml_models_dir: str = "ml_models"

    def ml_models_path(self) -> Path:
        p = Path(self.ml_models_dir)
        if not p.is_absolute():
            # repo root = backend/.. (this file lives in backend/)
            p = (Path(__file__).resolve().parent.parent / p).resolve()
        return p


settings = Settings()

