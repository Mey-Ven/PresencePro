"""
Configuration Celery pour les tâches asynchrones
"""
from celery import Celery
from celery.signals import worker_ready, worker_shutdown
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Configuration Celery
celery_app = Celery(
    "notification-service",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.sms_tasks", 
        "app.tasks.push_tasks",
        "app.tasks.event_tasks"
    ]
)

# Configuration Celery
celery_app.conf.update(
    task_serializer=settings.celery_task_serializer,
    result_serializer=settings.celery_result_serializer,
    accept_content=settings.celery_accept_content,
    timezone=settings.celery_timezone,
    enable_utc=settings.celery_enable_utc,
    
    # Configuration des tâches
    task_routes={
        "app.tasks.email_tasks.*": {"queue": "email"},
        "app.tasks.sms_tasks.*": {"queue": "sms"},
        "app.tasks.push_tasks.*": {"queue": "push"},
        "app.tasks.event_tasks.*": {"queue": "events"}
    },
    
    # Configuration des retry
    task_default_retry_delay=settings.retry_delay_seconds,
    task_max_retry_delay=600,  # 10 minutes max
    task_default_max_retries=settings.max_retry_attempts,
    
    # Configuration des workers
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Configuration du monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Configuration des résultats
    result_expires=3600,  # 1 heure
    result_persistent=True,
    
    # Configuration de la sécurité
    worker_hijack_root_logger=False,
    worker_log_color=False,
    
    # Beat scheduler (pour les tâches périodiques)
    beat_schedule={
        "send-daily-digest": {
            "task": "app.tasks.email_tasks.send_daily_digest",
            "schedule": 60.0 * 60.0 * 24.0,  # Tous les jours
            "options": {"queue": "email"}
        },
        "send-weekly-report": {
            "task": "app.tasks.email_tasks.send_weekly_report", 
            "schedule": 60.0 * 60.0 * 24.0 * 7.0,  # Toutes les semaines
            "options": {"queue": "email"}
        },
        "cleanup-old-notifications": {
            "task": "app.tasks.event_tasks.cleanup_old_notifications",
            "schedule": 60.0 * 60.0 * 24.0,  # Tous les jours
            "options": {"queue": "events"}
        }
    }
)


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Handler appelé quand un worker est prêt"""
    logger.info("🚀 Celery worker prêt")


@worker_shutdown.connect  
def worker_shutdown_handler(sender=None, **kwargs):
    """Handler appelé quand un worker s'arrête"""
    logger.info("🛑 Celery worker arrêté")


# Fonction pour obtenir l'instance Celery
def get_celery_app():
    """Obtenir l'instance Celery"""
    return celery_app
