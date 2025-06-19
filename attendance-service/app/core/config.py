"""
Configuration du service de gestion des présences
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "attendance-service"
    service_version: str = "1.0.0"
    service_port: int = 8005
    host: str = "0.0.0.0"
    debug: bool = True
    
    # Database Configuration (SQLite pour développement)
    database_url: str = "sqlite:///./attendance.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Security
    secret_key: str = "attendance-service-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Integration avec autres services
    auth_service_url: str = "http://localhost:8001"
    user_service_url: str = "http://localhost:8002"
    course_service_url: str = "http://localhost:8003"
    face_recognition_service_url: str = "http://localhost:8004"
    
    # Attendance Configuration
    attendance_grace_period_minutes: int = 15  # Période de grâce pour marquer présent
    late_threshold_minutes: int = 10  # Seuil pour marquer en retard
    auto_mark_absent_hours: int = 2  # Marquer absent après X heures
    
    # Timezone
    default_timezone: str = "Europe/Paris"
    
    # Reporting
    max_export_records: int = 10000
    report_cache_ttl_seconds: int = 300  # 5 minutes
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/attendance.log"
    
    class Config:
        env_file = ".env"


settings = Settings()
