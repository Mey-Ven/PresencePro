from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./presencepro_auth.db"

    # JWT
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Application
    app_name: str = "PresencePro Auth Service"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8001
    
    class Config:
        env_file = ".env"


settings = Settings()
