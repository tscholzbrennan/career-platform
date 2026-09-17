from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Career Platform"
    SQLITE_DB_PATH: str = "career_platform.db"
    FALLBACK_PROFILE_PATH: str = "data/fallback-profile.json"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
