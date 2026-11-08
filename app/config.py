from collections.abc import Mapping

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Career Platform"
    DATABASE_URL: str = ""
    SQLITE_DB_PATH: str = "career_platform.db"
    FALLBACK_PROFILE_PATH: str = "data/fallback-profile.json"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def database_url_required(environ: Mapping[str, str]) -> bool:
    # Production must never fall back to SQLite: the site would come up with
    # placeholder content and look healthy. Read the process environment, not
    # .env, so the guard holds even when .env is missing.
    return environ.get("APP_ENV") == "production" or bool(environ.get("RAILWAY_ENVIRONMENT_NAME"))


def resolve_database_url(raw: str, sqlite_path: str, require_url: bool) -> str:
    # Hosts hand out postgres:// or postgresql:// URLs; SQLAlchemy needs the
    # psycopg (v3) driver named explicitly. Unset means local SQLite, except in
    # production.
    if not raw:
        if require_url:
            raise RuntimeError("DATABASE_URL is not set; production must not fall back to SQLite")
        return f"sqlite:///{sqlite_path}"
    for prefix in ("postgres://", "postgresql://"):
        if raw.startswith(prefix):
            return "postgresql+psycopg://" + raw[len(prefix):]
    return raw


settings = Settings()
