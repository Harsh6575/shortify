from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
import os

APP_ENV = os.getenv("APP_ENV", "dev")

class Settings(BaseSettings):
    APP_NAME: str = "Shortify"
    
    # Raw variables from .env
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_PORT: int = 27017
    REDIS_PORT: int = 6379
    MONGODB_DB_NAME: str = "shortify"

    @computed_field
    def MONGODB_URL(self) -> str:
        host = "localhost" if APP_ENV == "dev" else "mongodb"
        return f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}@{host}:{self.MONGO_PORT}"

    @computed_field
    def REDIS_URL(self) -> str:
        host = "localhost" if APP_ENV == "dev" else "redis"
        return f"redis://{host}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(
        env_file=f"infra/.env.{APP_ENV}",
        extra="ignore"
    )

settings = Settings()