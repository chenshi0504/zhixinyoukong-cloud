import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CLOUD_DIR = os.path.dirname(_BACKEND_DIR)
_ENV_FILES = (
    os.path.join(_CLOUD_DIR, ".env"),
    os.path.join(_BACKEND_DIR, ".env"),
)


class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480   # 8 小时
    refresh_token_expire_days: int = 7
    rsa_private_key_path: str = ""
    upload_dir: str = "./uploads"
    debug: bool = False
    allowed_origins: str = "https://chenshi0504.github.io,http://localhost:5173"
    cloud_app_host: str = "0.0.0.0"
    cloud_app_port: int = 9000

    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
