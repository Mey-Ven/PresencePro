"""
Configuration du Config Service
"""
from typing import Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration du Config Service"""
    
    # Configuration du serveur
    config_host: str = Field(default="0.0.0.0", env="CONFIG_HOST")
    config_port: int = Field(default=8010, env="CONFIG_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Configuration du stockage
    config_storage_type: str = Field(default="file", env="CONFIG_STORAGE_TYPE")  # file, consul, redis
    config_base_path: str = Field(default="./configs", env="CONFIG_BASE_PATH")
    config_encryption_key: str = Field(env="CONFIG_ENCRYPTION_KEY")
    
    # Configuration Consul
    consul_host: str = Field(default="localhost", env="CONSUL_HOST")
    consul_port: int = Field(default=8500, env="CONSUL_PORT")
    consul_token: Optional[str] = Field(default=None, env="CONSUL_TOKEN")
    
    # Configuration Redis
    redis_url: str = Field(default="redis://localhost:6379/1", env="REDIS_URL")
    
    # Sécurité
    api_key_header: str = Field(default="X-Config-API-Key", env="API_KEY_HEADER")
    master_api_key: str = Field(env="MASTER_API_KEY")
    service_api_keys: str = Field(default="", env="SERVICE_API_KEYS")
    
    # Monitoring
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    
    # File Watching
    enable_file_watching: bool = Field(default=True, env="ENABLE_FILE_WATCHING")
    config_reload_interval: int = Field(default=30, env="CONFIG_RELOAD_INTERVAL")
    
    # Backup
    enable_config_backup: bool = Field(default=True, env="ENABLE_CONFIG_BACKUP")
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    backup_path: str = Field(default="./backups", env="BACKUP_PATH")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def service_api_keys_dict(self) -> Dict[str, str]:
        """Parse service API keys from string format"""
        if not self.service_api_keys:
            return {}
        
        keys = {}
        for pair in self.service_api_keys.split(','):
            if ':' in pair:
                service, key = pair.strip().split(':', 1)
                keys[service] = key
        return keys

    @property
    def supported_services(self) -> List[str]:
        """Liste des services supportés"""
        return [
            "auth-service",
            "user-service", 
            "course-service",
            "face-recognition-service",
            "attendance-service",
            "justification-service",
            "messaging-service",
            "notification-service",
            "statistics-service",
            "gateway-service",
            "admin-panel-service",
            "config-service"
        ]

    @property
    def default_service_configs(self) -> Dict[str, Dict]:
        """Configurations par défaut pour chaque service"""
        return {
            "auth-service": {
                "host": "0.0.0.0",
                "port": 8001,
                "database_url": "sqlite:///./auth.db",
                "jwt_secret_key": "auth-jwt-secret-key",
                "jwt_algorithm": "HS256",
                "jwt_access_token_expire_minutes": 30,
                "jwt_refresh_token_expire_days": 7,
                "password_hash_algorithm": "bcrypt",
                "enable_registration": True,
                "enable_email_verification": False,
                "redis_url": "redis://localhost:6379/0"
            },
            "user-service": {
                "host": "0.0.0.0",
                "port": 8002,
                "database_url": "sqlite:///./users.db",
                "auth_service_url": "http://localhost:8001",
                "enable_user_import": True,
                "max_file_size_mb": 10,
                "allowed_file_types": ["csv", "xlsx"],
                "default_user_role": "student"
            },
            "course-service": {
                "host": "0.0.0.0",
                "port": 8003,
                "database_url": "postgresql://user:password@localhost/courses",
                "auth_service_url": "http://localhost:8001",
                "max_students_per_class": 50,
                "academic_year_start_month": 9,
                "enable_course_scheduling": True
            },
            "face-recognition-service": {
                "host": "0.0.0.0",
                "port": 8004,
                "model_path": "./models/face_recognition_model.pkl",
                "confidence_threshold": 0.6,
                "max_image_size_mb": 5,
                "supported_formats": ["jpg", "jpeg", "png"],
                "enable_gpu": False,
                "batch_size": 32
            },
            "attendance-service": {
                "host": "0.0.0.0",
                "port": 8005,
                "database_url": "postgresql://user:password@localhost/attendance",
                "auth_service_url": "http://localhost:8001",
                "face_recognition_service_url": "http://localhost:8004",
                "auto_mark_late_minutes": 15,
                "enable_face_recognition": True,
                "enable_qr_code": True
            },
            "justification-service": {
                "host": "0.0.0.0",
                "port": 8006,
                "database_url": "postgresql://user:password@localhost/justifications",
                "auth_service_url": "http://localhost:8001",
                "notification_service_url": "http://localhost:8008",
                "max_file_size_mb": 10,
                "allowed_file_types": ["pdf", "jpg", "png"],
                "auto_approval_types": ["medical"],
                "approval_workflow_enabled": True
            },
            "messaging-service": {
                "host": "0.0.0.0",
                "port": 8007,
                "database_url": "mongodb://localhost:27017/messaging",
                "auth_service_url": "http://localhost:8001",
                "enable_websocket": True,
                "max_message_length": 1000,
                "enable_file_sharing": True,
                "max_file_size_mb": 25
            },
            "notification-service": {
                "host": "0.0.0.0",
                "port": 8008,
                "redis_url": "redis://localhost:6379/2",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "email_from": "noreply@presencepro.com",
                "enable_email": True,
                "enable_sms": False,
                "enable_push": False
            },
            "statistics-service": {
                "host": "0.0.0.0",
                "port": 8009,
                "database_url": "postgresql://user:password@localhost/statistics",
                "redis_url": "redis://localhost:6379/3",
                "auth_service_url": "http://localhost:8001",
                "attendance_service_url": "http://localhost:8005",
                "cache_ttl_seconds": 300,
                "enable_real_time_stats": True,
                "export_formats": ["json", "csv", "xlsx", "pdf"]
            },
            "gateway-service": {
                "host": "0.0.0.0",
                "port": 8000,
                "jwt_secret_key": "gateway-jwt-secret-key",
                "redis_url": "redis://localhost:6379/0",
                "rate_limit_requests_per_minute": 100,
                "rate_limit_burst": 20,
                "cors_origins": ["http://localhost:3000"],
                "service_timeout": 10
            },
            "admin-panel-service": {
                "port": 3000,
                "api_base_url": "http://localhost:8000",
                "enable_hot_reload": True,
                "build_path": "./build",
                "public_path": "./public"
            },
            "config-service": {
                "host": "0.0.0.0",
                "port": 8010,
                "config_storage_type": "file",
                "config_base_path": "./configs",
                "enable_file_watching": True,
                "enable_config_backup": True
            }
        }


# Instance globale des paramètres
settings = Settings()
