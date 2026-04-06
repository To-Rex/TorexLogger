from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/torexlogger"
    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    admin_username: str = "admin"
    admin_password: str = "admin123"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()