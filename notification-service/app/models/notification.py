"""
Modèles de données pour les notifications
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from app.core.database import Base


class NotificationStatus(str, Enum):
    """Statuts de notification"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """Types de notification"""
    ABSENCE_DETECTED = "absence_detected"
    JUSTIFICATION_SUBMITTED = "justification_submitted"
    JUSTIFICATION_APPROVED = "justification_approved"
    JUSTIFICATION_REJECTED = "justification_rejected"
    PARENT_APPROVAL_REQUIRED = "parent_approval_required"
    ADMIN_VALIDATION_REQUIRED = "admin_validation_required"
    MESSAGE_RECEIVED = "message_received"
    ATTENDANCE_ALERT = "attendance_alert"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"
    SYSTEM_ALERT = "system_alert"


class NotificationChannel(str, Enum):
    """Canaux de notification"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class Priority(str, Enum):
    """Priorités de notification"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Modèles SQLAlchemy

class NotificationLog(Base):
    """Log des notifications envoyées"""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiants
    notification_id = Column(String(255), unique=True, index=True)
    user_id = Column(String(255), index=True)
    
    # Type et canal
    notification_type = Column(String(50), index=True)
    channel = Column(String(20), index=True)
    priority = Column(String(20), default="normal")
    
    # Contenu
    subject = Column(String(500))
    content = Column(Text)
    template_id = Column(String(255))
    template_data = Column(JSON)
    
    # Destinataire
    recipient_email = Column(String(255))
    recipient_phone = Column(String(50))
    recipient_name = Column(String(255))
    
    # Statut et résultat
    status = Column(String(20), default="pending", index=True)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Métadonnées
    meta_data = Column(JSON)
    external_id = Column(String(255))  # ID externe (SendGrid, Twilio, etc.)
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    next_retry_at = Column(DateTime(timezone=True))
    
    # Relations (optionnelle - pas de clé étrangère stricte)
    # template = relationship("NotificationTemplate", back_populates="logs")


class NotificationTemplate(Base):
    """Templates de notifications"""
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiants
    template_id = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    
    # Type et canal
    notification_type = Column(String(50), index=True)
    channel = Column(String(20), index=True)
    language = Column(String(10), default="fr")
    
    # Contenu du template
    subject_template = Column(String(500))
    content_template = Column(Text)
    html_template = Column(Text)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Métadonnées
    variables = Column(JSON)  # Variables disponibles dans le template
    meta_data = Column(JSON)
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations (optionnelle - pas de clé étrangère stricte)
    # logs = relationship("NotificationLog", back_populates="template")


class UserPreference(Base):
    """Préférences de notification des utilisateurs"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiant utilisateur
    user_id = Column(String(255), unique=True, index=True)
    
    # Préférences par canal
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    
    # Préférences par type
    absence_notifications = Column(Boolean, default=True)
    justification_notifications = Column(Boolean, default=True)
    message_notifications = Column(Boolean, default=True)
    report_notifications = Column(Boolean, default=True)
    
    # Préférences temporelles
    immediate_alerts = Column(Boolean, default=True)
    daily_digest = Column(Boolean, default=True)
    weekly_report = Column(Boolean, default=True)
    quiet_hours_start = Column(String(5), default="22:00")
    quiet_hours_end = Column(String(5), default="07:00")
    
    # Configuration
    timezone = Column(String(50), default="Europe/Paris")
    language = Column(String(10), default="fr")
    
    # Métadonnées
    meta_data = Column(JSON)
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EventQueue(Base):
    """File d'attente des événements"""
    __tablename__ = "event_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiants
    event_id = Column(String(255), unique=True, index=True)
    source_service = Column(String(100), index=True)
    
    # Type d'événement
    event_type = Column(String(100), index=True)
    event_data = Column(JSON)
    
    # Traitement
    status = Column(String(20), default="pending", index=True)
    processed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))


# Modèles Pydantic pour les API

class NotificationRequest(BaseModel):
    """Requête de notification"""
    user_id: str
    notification_type: NotificationType
    channel: NotificationChannel
    priority: Priority = Priority.NORMAL
    subject: Optional[str] = None
    content: Optional[str] = None
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = {}
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_name: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = {}


class NotificationResponse(BaseModel):
    """Réponse de notification"""
    notification_id: str
    status: NotificationStatus
    message: str
    created_at: datetime
    sent_at: Optional[datetime] = None


class TemplateRequest(BaseModel):
    """Requête de template"""
    template_id: str
    name: str
    description: Optional[str] = None
    notification_type: NotificationType
    channel: NotificationChannel
    language: str = "fr"
    subject_template: Optional[str] = None
    content_template: str
    html_template: Optional[str] = None
    variables: Optional[Dict[str, Any]] = {}
    is_active: bool = True
    is_default: bool = False


class UserPreferenceRequest(BaseModel):
    """Requête de préférences utilisateur"""
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    absence_notifications: bool = True
    justification_notifications: bool = True
    message_notifications: bool = True
    report_notifications: bool = True
    immediate_alerts: bool = True
    daily_digest: bool = True
    weekly_report: bool = True
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"
    timezone: str = "Europe/Paris"
    language: str = "fr"


class EventRequest(BaseModel):
    """Requête d'événement"""
    event_type: str
    source_service: str
    event_data: Dict[str, Any]
    user_id: Optional[str] = None
    priority: Priority = Priority.NORMAL


class NotificationStats(BaseModel):
    """Statistiques de notifications"""
    total_sent: int
    total_failed: int
    total_pending: int
    sent_today: int
    failed_today: int
    success_rate: float
    avg_delivery_time: Optional[float] = None


class HealthCheck(BaseModel):
    """Vérification de santé"""
    service: str
    status: str
    timestamp: datetime
    database_connected: bool
    redis_connected: bool
    celery_workers: int
    queue_size: int
    last_notification_sent: Optional[datetime] = None
