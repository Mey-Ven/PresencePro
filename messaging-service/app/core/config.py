"""
Configuration du service de messagerie
"""
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "messaging-service"
    service_version: str = "1.0.0"
    service_port: int = 8007
    host: str = "0.0.0.0"
    debug: bool = True
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "presencepro_messaging"
    mongodb_collection_messages: str = "messages"
    mongodb_collection_conversations: str = "conversations"
    mongodb_collection_users: str = "users"
    
    # Security
    secret_key: str = "messaging-service-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Integration avec autres services
    auth_service_url: str = "http://localhost:8001"
    user_service_url: str = "http://localhost:8002"
    
    # WebSocket Configuration
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 10
    max_connections_per_user: int = 5
    
    # Message Configuration
    max_message_length: int = 2000
    max_messages_per_conversation: int = 1000
    message_retention_days: int = 365
    
    # File Upload Configuration (pour futurs attachments)
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    
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
    notify_new_message: bool = True
    notify_offline_users: bool = True
    
    # Rate Limiting
    rate_limit_messages_per_minute: int = 30
    rate_limit_connections_per_minute: int = 10
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/messaging.log"
    
    class Config:
        env_file = ".env"


settings = Settings()
