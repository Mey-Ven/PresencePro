"""
Configuration du service de notifications
"""
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any


class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "notification-service"
    service_version: str = "1.0.0"
    service_port: int = 8008
    host: str = "0.0.0.0"
    debug: bool = True
    
    # Database Configuration (pour logs et historique)
    database_url: str = "sqlite:///./notifications.db"
    # database_url: str = "postgresql://postgres:password@localhost:5432/presencepro_notifications"
    
    # Redis Configuration (Celery Broker)
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: List[str] = ["json"]
    celery_timezone: str = "Europe/Paris"
    celery_enable_utc: bool = True
    
    # Email Configuration - SMTP
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    email_from: str = "noreply@presencepro.com"
    email_from_name: str = "PresencePro"
    
    # Email Configuration - SendGrid
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@presencepro.com"
    sendgrid_from_name: str = "PresencePro"
    use_sendgrid: bool = False
    
    # SMS Configuration - Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    sms_enabled: bool = False
    
    # Push Notifications - Firebase
    firebase_server_key: str = ""
    firebase_project_id: str = ""
    push_notifications_enabled: bool = False
    
    # Integration avec autres services
    auth_service_url: str = "http://localhost:8001"
    user_service_url: str = "http://localhost:8002"
    attendance_service_url: str = "http://localhost:8005"
    justification_service_url: str = "http://localhost:8006"
    messaging_service_url: str = "http://localhost:8007"
    
    # Security
    secret_key: str = "notification-service-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Notification Settings
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 60
    batch_size: int = 100
    rate_limit_per_minute: int = 60
    
    # Template Configuration
    template_dir: str = "./templates"
    default_language: str = "fr"
    supported_languages: List[str] = ["fr", "en"]
    
    # Event Configuration
    event_queue_name: str = "presencepro_events"
    webhook_secret: str = "webhook-secret-change-in-production"
    
    # Notification Types
    notification_types: Dict[str, bool] = {
        "absence_detected": True,
        "justification_submitted": True,
        "justification_approved": True,
        "justification_rejected": True,
        "parent_approval_required": True,
        "admin_validation_required": True,
        "message_received": True,
        "attendance_alert": True,
        "weekly_report": True,
        "monthly_report": True
    }
    
    # Notification Channels
    notification_channels: Dict[str, bool] = {
        "email": True,
        "sms": False,
        "push": False,
        "webhook": False
    }
    
    # User Preferences (defaults)
    default_user_preferences: Dict[str, Any] = {
        "email_notifications": True,
        "sms_notifications": False,
        "push_notifications": True,
        "immediate_alerts": True,
        "daily_digest": True,
        "weekly_report": True,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "timezone": "Europe/Paris"
    }
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/notifications.log"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Development
    mock_email_sending: bool = False
    save_emails_to_file: bool = True
    email_output_dir: str = "./logs/emails"
    
    class Config:
        env_file = ".env"


settings = Settings()
