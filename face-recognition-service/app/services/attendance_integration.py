"""
Service d'intégration avec l'attendance-service
"""
import httpx
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings
from app.models.schemas import RecognitionResult


class AttendanceIntegrationService:
    """Service pour intégrer avec l'attendance-service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.attendance_service_url = settings.attendance_service_url
        self.auth_service_url = settings.auth_service_url
        
    async def record_attendance(self, recognition: RecognitionResult, camera_id: str = "default") -> bool:
        """Enregistrer une présence via l'attendance-service"""
        if not recognition.user_id or recognition.status != "recognized":
            self.logger.debug("Pas d'enregistrement de présence: utilisateur non reconnu")
            return False
        
        try:
            # Préparer les données de présence
            attendance_data = {
                "user_id": recognition.user_id,
                "timestamp": recognition.timestamp.isoformat(),
                "method": "face_recognition",
                "camera_id": camera_id,
                "confidence": recognition.confidence,
                "status": "present"
            }
            
            # Appeler l'attendance-service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.attendance_service_url}/api/v1/attendance/record",
                    json=attendance_data,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    self.logger.info(f"Présence enregistrée pour {recognition.user_id}")
                    return True
                else:
                    self.logger.warning(f"Échec enregistrement présence: {response.status_code}")
                    return False
                    
        except httpx.TimeoutException:
            self.logger.error("Timeout lors de l'enregistrement de présence")
            return False
        except httpx.ConnectError:
            self.logger.error("Impossible de se connecter à l'attendance-service")
            return False
        except Exception as e:
            self.logger.error(f"Erreur enregistrement présence: {e}")
            return False
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un utilisateur via user-service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.user_service_url}/api/v1/users/{user_id}",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"Utilisateur {user_id} non trouvé")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Erreur récupération info utilisateur: {e}")
            return None
    
    async def verify_user_access(self, user_id: str, camera_id: str = "default") -> bool:
        """Vérifier si un utilisateur a accès à une zone/caméra"""
        try:
            # Pour l'instant, on autorise tous les utilisateurs reconnus
            # Dans une version future, on pourrait vérifier les permissions
            user_info = await self.get_user_info(user_id)
            return user_info is not None
            
        except Exception as e:
            self.logger.error(f"Erreur vérification accès: {e}")
            return False
    
    async def get_attendance_stats(self, user_id: str = None, date: str = None) -> Optional[Dict[str, Any]]:
        """Récupérer les statistiques de présence"""
        try:
            params = {}
            if user_id:
                params["user_id"] = user_id
            if date:
                params["date"] = date
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.attendance_service_url}/api/v1/attendance/stats",
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            self.logger.error(f"Erreur récupération stats présence: {e}")
            return None
    
    async def notify_recognition_event(self, recognition: RecognitionResult, camera_id: str):
        """Notifier un événement de reconnaissance (pour logs/monitoring)"""
        try:
            event_data = {
                "event_type": "face_recognition",
                "user_id": recognition.user_id,
                "name": recognition.name,
                "confidence": recognition.confidence,
                "status": recognition.status,
                "timestamp": recognition.timestamp.isoformat(),
                "camera_id": camera_id
            }
            
            # Pour l'instant, on log seulement
            # Dans une version future, on pourrait envoyer à un service de monitoring
            self.logger.info(f"Événement reconnaissance: {event_data}")
            
        except Exception as e:
            self.logger.error(f"Erreur notification événement: {e}")
    
    def is_attendance_service_available(self) -> bool:
        """Vérifier si l'attendance-service est disponible"""
        try:
            import requests
            response = requests.get(
                f"{self.attendance_service_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except:
            return False


class AttendanceProcessor:
    """Processeur pour gérer les reconnaissances et enregistrer les présences"""
    
    def __init__(self):
        self.integration_service = AttendanceIntegrationService()
        self.logger = logging.getLogger(__name__)
        self.processed_recognitions = set()  # Éviter les doublons
        
    async def process_recognition(self, recognition: RecognitionResult, camera_id: str = "default"):
        """Traiter une reconnaissance et enregistrer la présence si nécessaire"""
        try:
            # Créer une clé unique pour éviter les doublons
            recognition_key = f"{recognition.user_id}_{recognition.timestamp.strftime('%Y%m%d_%H%M')}"
            
            if recognition_key in self.processed_recognitions:
                self.logger.debug(f"Reconnaissance déjà traitée: {recognition_key}")
                return
            
            # Vérifier si l'utilisateur est reconnu
            if recognition.status == "recognized" and recognition.user_id:
                # Vérifier l'accès
                has_access = await self.integration_service.verify_user_access(
                    recognition.user_id, camera_id
                )
                
                if has_access:
                    # Enregistrer la présence
                    success = await self.integration_service.record_attendance(
                        recognition, camera_id
                    )
                    
                    if success:
                        self.processed_recognitions.add(recognition_key)
                        self.logger.info(f"Présence enregistrée pour {recognition.name}")
                    else:
                        self.logger.warning(f"Échec enregistrement présence pour {recognition.name}")
                else:
                    self.logger.warning(f"Accès refusé pour {recognition.name}")
            
            # Notifier l'événement dans tous les cas
            await self.integration_service.notify_recognition_event(recognition, camera_id)
            
        except Exception as e:
            self.logger.error(f"Erreur traitement reconnaissance: {e}")
    
    def cleanup_old_recognitions(self):
        """Nettoyer les anciennes reconnaissances pour éviter l'accumulation"""
        # Garder seulement les reconnaissances des dernières heures
        # Pour simplifier, on vide tout si on dépasse 1000 entrées
        if len(self.processed_recognitions) > 1000:
            self.processed_recognitions.clear()
            self.logger.info("Cache des reconnaissances nettoyé")
