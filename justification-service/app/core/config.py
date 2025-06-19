"""
Configuration du service de gestion des justifications
"""
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "justification-service"
    service_version: str = "1.0.0"
    service_port: int = 8006
    host: str = "0.0.0.0"
    debug: bool = True
    
    # Database Configuration (PostgreSQL)
    database_url: str = "sqlite:///./justifications.db"  # SQLite pour développement
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Security
    secret_key: str = "justification-service-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Integration avec autres services
    auth_service_url: str = "http://localhost:8001"
    user_service_url: str = "http://localhost:8002"
    course_service_url: str = "http://localhost:8003"
    attendance_service_url: str = "http://localhost:8005"
    
    # Justification Configuration
    max_justification_days: int = 7  # Délai max pour justifier une absence
    auto_expire_days: int = 30  # Expiration automatique des justifications non traitées
    require_parent_approval: bool = True  # Approbation parentale obligatoire
    require_admin_validation: bool = True  # Validation administrative obligatoire
    
    # File Upload Configuration
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: str = "pdf,jpg,jpeg,png,doc,docx"

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Convertir la chaîne en liste"""
        return [ext.strip() for ext in self.allowed_file_types.split(",")]
    
    # Email Configuration
    smtp_server: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = "noreply@presencepro.com"
    
    # Timezone
    default_timezone: str = "Europe/Paris"
    
    # Notifications
    notify_parents: bool = True
    notify_admins: bool = True
    notify_students: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/justification.log"
    
    class Config:
        env_file = ".env"


settings = Settings()
