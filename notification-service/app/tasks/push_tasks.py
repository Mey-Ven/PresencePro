"""
Tâches Celery pour les notifications push
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_push_notification_task(
    self,
    notification_id: str,
    device_tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    notification_type: Optional[str] = None,
    priority: str = "normal"
):
    """Tâche d'envoi de notification push"""
    try:
        if not settings.push_notifications_enabled:
            logger.info("Notifications push désactivées dans la configuration")
            return {"success": False, "reason": "push_disabled"}
        
        logger.info(f"Envoi notification push {notification_id} à {len(device_tokens)} appareils")
        
        # TODO: Implémenter l'envoi push avec Firebase
        if settings.firebase_server_key:
            result = await send_push_via_firebase(device_tokens, title, body, data)
        else:
            # Mode développement - simuler l'envoi
            result = {
                "success": True,
                "provider": "mock",
                "message": "Notification push simulée en mode développement",
                "sent_count": len(device_tokens),
                "timestamp": datetime.now()
            }
            logger.info(f"Push simulée: {title} - {body[:50]}...")
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur envoi push {notification_id}: {e}")
        
        # Retry si possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        
        raise


async def send_push_via_firebase(
    device_tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Envoyer notification push via Firebase"""
    try:
        from pyfcm import FCMNotification
        
        push_service = FCMNotification(api_key=settings.firebase_server_key)
        
        # Préparer les données
        notification_data = data or {}
        
        # Envoyer à plusieurs appareils
        result = push_service.notify_multiple_devices(
            registration_ids=device_tokens,
            message_title=title,
            message_body=body,
            data_message=notification_data
        )
        
        logger.info(f"Notification push envoyée via Firebase: {result}")
        
        return {
            "success": True,
            "provider": "firebase",
            "multicast_id": result.get("multicast_id"),
            "success_count": result.get("success"),
            "failure_count": result.get("failure"),
            "results": result.get("results", []),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Erreur Firebase: {e}")
        return {
            "success": False,
            "provider": "firebase",
            "error": str(e),
            "timestamp": datetime.now()
        }


@celery_app.task
def send_bulk_push_notifications_task(notifications: List[Dict[str, Any]]):
    """Tâche d'envoi de notifications push en lot"""
    try:
        logger.info(f"Envoi de {len(notifications)} notifications push en lot")
        
        results = []
        for notification_data in notifications:
            task = send_push_notification_task.delay(**notification_data)
            results.append({
                "notification_id": notification_data.get("notification_id"),
                "task_id": task.id,
                "device_count": len(notification_data.get("device_tokens", []))
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Erreur envoi lot push: {e}")
        raise


@celery_app.task
def update_device_token(user_id: str, device_token: str, platform: str = "android"):
    """Mettre à jour le token d'appareil d'un utilisateur"""
    try:
        # TODO: Stocker les tokens d'appareils en base de données
        # pour pouvoir envoyer des notifications push ciblées
        
        logger.info(f"Token d'appareil mis à jour pour {user_id}: {device_token[:20]}...")
        
        return {"success": True, "user_id": user_id}
        
    except Exception as e:
        logger.error(f"Erreur mise à jour token: {e}")
        raise


@celery_app.task
def cleanup_invalid_tokens():
    """Nettoyer les tokens d'appareils invalides"""
    try:
        # TODO: Implémenter le nettoyage des tokens invalides
        # en utilisant les retours de Firebase
        
        logger.info("Nettoyage des tokens invalides")
        
        return {"success": True, "cleaned_tokens": 0}
        
    except Exception as e:
        logger.error(f"Erreur nettoyage tokens: {e}")
        raise
