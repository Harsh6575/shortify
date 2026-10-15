from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Shortify"

    MONGODB_URL: str
    MONGODB_DB_NAME: str = "shortify"
    REDIS_URL: str
    # Public origin used to build short links, e.g. https://sho.rt
    BASE_URL: str = "http://localhost:8000"

    # Real environment variables take precedence over .env, so containers configure the app without a file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
