from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # Database
    database_url: str
    database_url_test: str | None = None
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 200


@lru_cache()
def get_settings() -> Settings:
    return Settings()
