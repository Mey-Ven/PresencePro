"""
Tâches Celery pour l'envoi de SMS
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_task(
    self,
    notification_id: str,
    to_phone: str,
    message: str,
    user_id: Optional[str] = None,
    notification_type: Optional[str] = None,
    priority: str = "normal"
):
    """Tâche d'envoi de SMS"""
    try:
        if not settings.sms_enabled:
            logger.info("SMS désactivé dans la configuration")
            return {"success": False, "reason": "sms_disabled"}
        
        logger.info(f"Envoi SMS {notification_id} à {to_phone}")
        
        # TODO: Implémenter l'envoi SMS avec Twilio
        if settings.twilio_account_sid and settings.twilio_auth_token:
            result = await send_sms_via_twilio(to_phone, message)
        else:
            # Mode développement - simuler l'envoi
            result = {
                "success": True,
                "provider": "mock",
                "message": "SMS simulé en mode développement",
                "timestamp": datetime.now()
            }
            logger.info(f"SMS simulé: {message[:50]}...")
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur envoi SMS {notification_id}: {e}")
        
        # Retry si possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        
        raise


async def send_sms_via_twilio(to_phone: str, message: str) -> Dict[str, Any]:
    """Envoyer SMS via Twilio"""
    try:
        from twilio.rest import Client
        
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        message_obj = client.messages.create(
            body=message,
            from_=settings.twilio_from_number,
            to=to_phone
        )
        
        logger.info(f"SMS envoyé via Twilio: {message_obj.sid}")
        
        return {
            "success": True,
            "provider": "twilio",
            "message_id": message_obj.sid,
            "status": message_obj.status,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Erreur Twilio: {e}")
        return {
            "success": False,
            "provider": "twilio",
            "error": str(e),
            "timestamp": datetime.now()
        }


@celery_app.task
def send_bulk_sms_task(sms_list: list):
    """Tâche d'envoi de SMS en lot"""
    try:
        logger.info(f"Envoi de {len(sms_list)} SMS en lot")
        
        results = []
        for sms_data in sms_list:
            task = send_sms_task.delay(**sms_data)
            results.append({
                "notification_id": sms_data.get("notification_id"),
                "task_id": task.id,
                "phone": sms_data.get("to_phone")
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Erreur envoi lot SMS: {e}")
        raise
