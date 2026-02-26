from pydantic_settings import BaseSettings
from functools import lru_cache
import json


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://cps_user:cps_secret_password@localhost:5432/checkprint"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = '["http://localhost:5173"]'
    ENVIRONMENT: str = "development"

    @property
    def cors_origins_list(self) -> list[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
