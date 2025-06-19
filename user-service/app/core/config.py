"""
Configuration du service utilisateur PresencePro
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Base de données
    database_url: str = "sqlite:///./presencepro_users.db"
    
    # Service
    service_name: str = "user-service"
    service_version: str = "1.0.0"
    service_port: int = 8002
    
    # Sécurité
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    
    # Services externes
    auth_service_url: str = "http://localhost:8001"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://localhost:8001",
        "http://localhost:8002"
    ]
    
    # Logs
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


# Instance globale des paramètres
settings = Settings()
