from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Career Platform"
    DATABASE_URL: str = ""
    SQLITE_DB_PATH: str = "career_platform.db"
    FALLBACK_PROFILE_PATH: str = "data/fallback-profile.json"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def resolve_database_url(raw: str, sqlite_path: str, on_railway: bool) -> str:
    # Railway hands out postgres:// or postgresql:// URLs; SQLAlchemy needs the
    # psycopg (v3) driver named explicitly. Unset means local SQLite, except on
    # Railway, where the container disk is wiped on every deploy.
    if not raw:
        if on_railway:
            raise RuntimeError("DATABASE_URL is not set; reference the Postgres service's DATABASE_URL")
        return f"sqlite:///{sqlite_path}"
    for prefix in ("postgres://", "postgresql://"):
        if raw.startswith(prefix):
            return "postgresql+psycopg://" + raw[len(prefix):]
    return raw


settings = Settings()
