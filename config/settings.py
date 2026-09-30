"""Environment-backed settings for the Gold Financial API."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Gold uses GOLD_DATABASE_URL when it is set."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/financial"
    gold_database_url: str | None = None
    enable_dev_ingest: bool = False
    prediction_service_url: str = "http://localhost:8002"
    app_name: str = "Financial API"

    @property
    def sqlalchemy_url(self) -> str:
        """Return the SQLAlchemy URL, preferring the Gold-specific override."""
        url = self.gold_database_url or self.database_url
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url.removeprefix("postgresql://")
        return url


settings = Settings()
