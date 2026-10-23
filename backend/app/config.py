"""Application configuration loaded from environment variables / .env file."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings.

    Every value can be overridden through an environment variable or a `.env`
    file placed in the repository root.  See `.env.example` for the full list.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- application -----------------------------------------------------
    app_name: str = "EventEase API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    debug: bool = False

    # --- database --------------------------------------------------------
    # Primary target is MySQL 8.0.  A SQLite URL can be used for a zero-setup
    # development/demo run (see README "Running without MySQL").
    database_url: str = "mysql+pymysql://eventease:eventease@127.0.0.1:3306/eventease"
    sql_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # --- behaviour -------------------------------------------------------
    # Create the schema + demo data automatically when the API starts.
    auto_init_db: bool = False
    # Comma separated list of browser origins allowed to call the API.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
