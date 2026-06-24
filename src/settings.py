from enum import StrEnum

from pydantic_settings import BaseSettings


class Envs(StrEnum):
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    """
    Application settings.

    Environments:
        - DEV: Uses DuckDB as the database backend.
        - PROD: Uses BigQuery as the database backend.
    """

    app_env: Envs = Envs.DEV
    project_id: str | None = None
    duckdb_path: str | None = None

    @property
    def is_dev(self) -> bool:
        return self.app_env == Envs.DEV

    @property
    def is_prod(self) -> bool:
        return self.app_env == Envs.PROD


def get_settings() -> Settings:
    return Settings()
