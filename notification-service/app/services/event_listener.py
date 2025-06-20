"""
Service d'écoute des événements Redis/RabbitMQ
"""
import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional
import redis.asyncio as redis
from datetime import datetime

from app.core.config import settings
from app.tasks.event_tasks import process_event

logger = logging.getLogger(__name__)


class EventListener:
    """Service d'écoute des événements"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.is_listening = False
        self.event_handlers: Dict[str, Callable] = {}
        
    async def connect(self):
        """Connexion à Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Tester la connexion
            await self.redis_client.ping()
            logger.info("✅ Connexion Redis établie pour l'écoute d'événements")
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Redis: {e}")
            raise
    
    async def disconnect(self):
        """Déconnexion de Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("🔌 Connexion Redis fermée")
    
    async def start_listening(self):
        """Démarrer l'écoute des événements"""
        if not self.redis_client:
            await self.connect()
        
        self.is_listening = True
        logger.info("🎧 Démarrage de l'écoute des événements...")
        
        try:
            # Écouter la queue d'événements PresencePro
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(settings.event_queue_name)
            
            logger.info(f"📡 Écoute sur la queue: {settings.event_queue_name}")
            
            async for message in pubsub.listen():
                if not self.is_listening:
                    break
                
                if message["type"] == "message":
                    await self._handle_event_message(message["data"])
                    
        except Exception as e:
            logger.error(f"❌ Erreur écoute événements: {e}")
            raise
        finally:
            await pubsub.unsubscribe(settings.event_queue_name)
            await pubsub.close()
    
    async def stop_listening(self):
        """Arrêter l'écoute des événements"""
        self.is_listening = False
        logger.info("🛑 Arrêt de l'écoute des événements")
    
    async def _handle_event_message(self, message_data: str):
        """Traiter un message d'événement"""
        try:
            # Parser le JSON
            event_data = json.loads(message_data)
            event_type = event_data.get("event_type")
            
            logger.info(f"📨 Événement reçu: {event_type}")
            
            # Valider les données de base
            if not self._validate_event_data(event_data):
                logger.warning(f"⚠️ Données d'événement invalides: {event_data}")
                return
            
            # Traiter l'événement de manière asynchrone avec Celery
            process_event.delay(event_data)
            
            logger.info(f"✅ Événement {event_type} envoyé pour traitement")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON: {e}")
        except Exception as e:
            logger.error(f"❌ Erreur traitement message: {e}")
    
    def _validate_event_data(self, event_data: Dict[str, Any]) -> bool:
        """Valider les données d'un événement"""
        required_fields = ["event_type", "source_service", "data"]
        
        for field in required_fields:
            if field not in event_data:
                logger.warning(f"Champ requis manquant: {field}")
                return False
        
        # Valider les types d'événements supportés
        supported_events = [
            "absence_detected",
            "justification_submitted",
            "justification_approved", 
            "justification_rejected",
            "parent_approval_required",
            "admin_validation_required",
            "message_received",
            "attendance_alert",
            "system_alert"
        ]
        
        if event_data["event_type"] not in supported_events:
            logger.warning(f"Type d'événement non supporté: {event_data['event_type']}")
            return False
        
        return True
    
    async def publish_event(self, event_data: Dict[str, Any]):
        """Publier un événement (pour tests)"""
        try:
            if not self.redis_client:
                await self.connect()
            
            # Ajouter timestamp si pas présent
            if "timestamp" not in event_data:
                event_data["timestamp"] = datetime.now().isoformat()
            
            # Publier sur la queue
            await self.redis_client.publish(
                settings.event_queue_name,
                json.dumps(event_data)
            )
            
            logger.info(f"📤 Événement publié: {event_data.get('event_type')}")
            
        except Exception as e:
            logger.error(f"❌ Erreur publication événement: {e}")
            raise
    
    async def get_queue_info(self) -> Dict[str, Any]:
        """Obtenir des informations sur la queue"""
        try:
            if not self.redis_client:
                await self.connect()
            
            # Informations Redis
            info = await self.redis_client.info()
            
            return {
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory"),
                "used_memory_human": info.get("used_memory_human"),
                "total_commands_processed": info.get("total_commands_processed"),
                "queue_name": settings.event_queue_name,
                "is_listening": self.is_listening
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération info queue: {e}")
            return {}


class WebhookEventListener:
    """Service d'écoute des événements via webhooks"""
    
    def __init__(self):
        self.webhook_secret = settings.webhook_secret
    
    def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """Valider la signature d'un webhook"""
        import hmac
        import hashlib
        
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
            
        except Exception as e:
            logger.error(f"Erreur validation signature webhook: {e}")
            return False
    
    async def handle_webhook(self, payload: Dict[str, Any], signature: str = None) -> bool:
        """Traiter un webhook"""
        try:
            # Valider la signature si fournie
            if signature:
                payload_str = json.dumps(payload, sort_keys=True)
                if not self.validate_webhook_signature(payload_str, signature):
                    logger.warning("Signature webhook invalide")
                    return False
            
            # Traiter l'événement
            from app.tasks.event_tasks import process_webhook_event
            process_webhook_event.delay(payload)
            
            logger.info(f"Webhook traité: {payload.get('event_type')}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur traitement webhook: {e}")
            return False


# Instances globales
event_listener = EventListener()
webhook_listener = WebhookEventListener()
