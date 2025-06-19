"""
Service d'intégration avec les autres microservices
"""
import httpx
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, date

from app.core.config import settings


class IntegrationService:
    """Service pour intégrer avec les autres microservices PresencePro"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.auth_service_url = settings.auth_service_url
        self.user_service_url = settings.user_service_url
        self.course_service_url = settings.course_service_url
        self.attendance_service_url = settings.attendance_service_url
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifier un token JWT avec auth-service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_service_url}/api/v1/auth/verify-token",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"Token invalide: {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Erreur vérification token: {e}")
            return None
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un utilisateur"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.user_service_url}/api/v1/users/{user_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"Utilisateur {user_id} non trouvé")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Erreur récupération utilisateur: {e}")
            return None
    
    async def get_student_parents(self, student_id: str) -> List[Dict[str, Any]]:
        """Récupérer les parents d'un étudiant"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.user_service_url}/api/v1/students/{student_id}/parents",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"Parents de l'étudiant {student_id} non trouvés")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Erreur récupération parents: {e}")
            return []
    
    async def verify_parent_student_relationship(self, parent_id: str, student_id: str) -> bool:
        """Vérifier la relation parent-étudiant"""
        try:
            parents = await self.get_student_parents(student_id)
            return any(parent.get("user_id") == parent_id for parent in parents)
            
        except Exception as e:
            self.logger.error(f"Erreur vérification relation parent-étudiant: {e}")
            return False
    
    async def get_course_info(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un cours"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.course_service_url}/api/v1/courses/{course_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"Cours {course_id} non trouvé")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Erreur récupération cours: {e}")
            return None
    
    async def get_attendance_record(self, attendance_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un enregistrement de présence"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.attendance_service_url}/api/v1/attendance/{attendance_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"Présence {attendance_id} non trouvée")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Erreur récupération présence: {e}")
            return None
    
    async def update_attendance_justification(
        self, 
        attendance_id: int, 
        justification_id: int,
        status: str
    ) -> bool:
        """Mettre à jour le statut de justification dans attendance-service"""
        try:
            update_data = {
                "justification_id": justification_id,
                "justification_status": status,
                "excuse_reason": f"Justification #{justification_id}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.attendance_service_url}/api/v1/attendance/{attendance_id}",
                    json=update_data,
                    timeout=10.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Erreur mise à jour présence: {e}")
            return False
    
    async def validate_justification_request(
        self, 
        student_id: str, 
        course_id: Optional[int] = None,
        attendance_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Valider une demande de justification"""
        validation_result = {
            "valid": False,
            "student_exists": False,
            "course_exists": False,
            "attendance_exists": False,
            "student_enrolled": False,
            "errors": []
        }
        
        try:
            # Vérifier l'existence de l'étudiant
            student_info = await self.get_user_info(student_id)
            if student_info:
                validation_result["student_exists"] = True
                if student_info.get("role") != "student":
                    validation_result["errors"].append(f"L'utilisateur {student_id} n'est pas un étudiant")
            else:
                validation_result["errors"].append(f"Étudiant {student_id} non trouvé")
            
            # Vérifier l'existence du cours si fourni
            if course_id:
                course_info = await self.get_course_info(course_id)
                if course_info:
                    validation_result["course_exists"] = True
                    
                    # Vérifier l'inscription de l'étudiant au cours
                    # TODO: Implémenter la vérification d'inscription
                    validation_result["student_enrolled"] = True
                else:
                    validation_result["errors"].append(f"Cours {course_id} non trouvé")
            
            # Vérifier l'existence de la présence si fournie
            if attendance_id:
                attendance_info = await self.get_attendance_record(attendance_id)
                if attendance_info:
                    validation_result["attendance_exists"] = True
                    
                    # Vérifier que la présence appartient à l'étudiant
                    if attendance_info.get("student_id") != student_id:
                        validation_result["errors"].append(f"La présence {attendance_id} n'appartient pas à l'étudiant {student_id}")
                else:
                    validation_result["errors"].append(f"Présence {attendance_id} non trouvée")
            
            # Déterminer la validité globale
            validation_result["valid"] = (
                validation_result["student_exists"] and
                (not course_id or (validation_result["course_exists"] and validation_result["student_enrolled"])) and
                (not attendance_id or validation_result["attendance_exists"]) and
                len(validation_result["errors"]) == 0
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Erreur validation demande justification: {e}")
            validation_result["errors"].append(f"Erreur de validation: {str(e)}")
            return validation_result
    
    async def notify_attendance_service(
        self, 
        justification_id: int,
        attendance_id: Optional[int],
        status: str
    ) -> bool:
        """Notifier le service de présences d'un changement de statut"""
        try:
            if not attendance_id:
                return True  # Pas de présence à notifier
            
            notification_data = {
                "justification_id": justification_id,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "source": "justification-service"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.attendance_service_url}/api/v1/webhooks/justification",
                    json=notification_data,
                    timeout=5.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Erreur notification attendance-service: {e}")
            return False
    
    def is_service_available(self, service_name: str) -> bool:
        """Vérifier si un service est disponible"""
        service_urls = {
            "auth": self.auth_service_url,
            "user": self.user_service_url,
            "course": self.course_service_url,
            "attendance": self.attendance_service_url
        }
        
        if service_name not in service_urls:
            return False
        
        try:
            import requests
            response = requests.get(
                f"{service_urls[service_name]}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except:
            return False
    
    async def get_user_role(self, user_id: str) -> Optional[str]:
        """Récupérer le rôle d'un utilisateur"""
        try:
            user_info = await self.get_user_info(user_id)
            return user_info.get("role") if user_info else None
            
        except Exception as e:
            self.logger.error(f"Erreur récupération rôle utilisateur: {e}")
            return None
