"""
Configuration du Gateway Service
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration du Gateway Service"""
    
    # Configuration du serveur
    gateway_host: str = Field(default="0.0.0.0", env="GATEWAY_HOST")
    gateway_port: int = Field(default=8000, env="GATEWAY_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # JWT Configuration
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Services URLs
    auth_service_url: str = Field(env="AUTH_SERVICE_URL")
    user_service_url: str = Field(env="USER_SERVICE_URL")
    course_service_url: str = Field(env="COURSE_SERVICE_URL")
    face_recognition_service_url: str = Field(env="FACE_RECOGNITION_SERVICE_URL")
    attendance_service_url: str = Field(env="ATTENDANCE_SERVICE_URL")
    justification_service_url: str = Field(env="JUSTIFICATION_SERVICE_URL")
    messaging_service_url: str = Field(env="MESSAGING_SERVICE_URL")
    notification_service_url: str = Field(env="NOTIFICATION_SERVICE_URL")
    statistics_service_url: str = Field(env="STATISTICS_SERVICE_URL")
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=100, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_burst: int = Field(default=20, env="RATE_LIMIT_BURST")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Health Check
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    service_timeout: int = Field(default=10, env="SERVICE_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def service_routes(self) -> dict:
        """Mapping des routes vers les services"""
        return {
            "/api/v1/auth": self.auth_service_url,
            "/api/v1/users": self.user_service_url,
            "/api/v1/students": self.user_service_url,
            "/api/v1/teachers": self.user_service_url,
            "/api/v1/parents": self.user_service_url,
            "/api/v1/courses": self.course_service_url,
            "/api/v1/classes": self.course_service_url,
            "/api/v1/face-recognition": self.face_recognition_service_url,
            "/api/v1/attendance": self.attendance_service_url,
            "/api/v1/justifications": self.justification_service_url,
            "/api/v1/messaging": self.messaging_service_url,
            "/api/v1/notifications": self.notification_service_url,
            "/api/v1/stats": self.statistics_service_url,
        }

    @property
    def public_routes(self) -> List[str]:
        """Routes publiques qui ne nécessitent pas d'authentification"""
        return [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

    @property
    def admin_only_routes(self) -> List[str]:
        """Routes réservées aux administrateurs"""
        return [
            "/api/v1/users",
            "/api/v1/students",
            "/api/v1/teachers", 
            "/api/v1/parents",
            "/api/v1/courses",
            "/api/v1/classes",
            "/api/v1/stats/global",
            "/api/v1/notifications/broadcast",
        ]

    @property
    def teacher_routes(self) -> List[str]:
        """Routes accessibles aux enseignants"""
        return [
            "/api/v1/attendance",
            "/api/v1/justifications",
            "/api/v1/stats/class",
            "/api/v1/stats/student",
            "/api/v1/messaging",
        ]


# Instance globale des paramètres
settings = Settings()
