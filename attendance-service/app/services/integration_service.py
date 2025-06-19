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
        self.face_recognition_service_url = settings.face_recognition_service_url
    
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
    
    async def get_course_schedule(self, course_id: int, date: date = None) -> List[Dict[str, Any]]:
        """Récupérer l'emploi du temps d'un cours"""
        try:
            params = {}
            if date:
                params["date"] = date.isoformat()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.course_service_url}/api/v1/schedules/course/{course_id}",
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return []
                    
        except Exception as e:
            self.logger.error(f"Erreur récupération emploi du temps: {e}")
            return []
    
    async def get_course_students(self, course_id: int) -> List[Dict[str, Any]]:
        """Récupérer la liste des étudiants d'un cours"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.course_service_url}/api/v1/assignments/course/{course_id}/students",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return []
                    
        except Exception as e:
            self.logger.error(f"Erreur récupération étudiants cours: {e}")
            return []
    
    async def get_student_courses(self, student_id: str) -> List[Dict[str, Any]]:
        """Récupérer la liste des cours d'un étudiant"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.course_service_url}/api/v1/courses/student/{student_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return []
                    
        except Exception as e:
            self.logger.error(f"Erreur récupération cours étudiant: {e}")
            return []
    
    async def notify_face_recognition_attendance(self, student_id: str, course_id: int, status: str) -> bool:
        """Notifier le service de reconnaissance faciale d'un enregistrement de présence"""
        try:
            notification_data = {
                "student_id": student_id,
                "course_id": course_id,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "source": "attendance-service"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.face_recognition_service_url}/api/v1/notifications/attendance",
                    json=notification_data,
                    timeout=5.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Erreur notification reconnaissance faciale: {e}")
            return False
    
    async def validate_attendance_request(self, student_id: str, course_id: int) -> Dict[str, Any]:
        """Valider une demande de présence"""
        validation_result = {
            "valid": False,
            "student_exists": False,
            "course_exists": False,
            "student_enrolled": False,
            "course_active": False,
            "errors": []
        }
        
        try:
            # Vérifier l'existence de l'étudiant
            student_info = await self.get_user_info(student_id)
            if student_info:
                validation_result["student_exists"] = True
            else:
                validation_result["errors"].append(f"Étudiant {student_id} non trouvé")
            
            # Vérifier l'existence du cours
            course_info = await self.get_course_info(course_id)
            if course_info:
                validation_result["course_exists"] = True
                validation_result["course_active"] = course_info.get("status") == "active"
                if not validation_result["course_active"]:
                    validation_result["errors"].append(f"Cours {course_id} non actif")
            else:
                validation_result["errors"].append(f"Cours {course_id} non trouvé")
            
            # Vérifier l'inscription de l'étudiant au cours
            if validation_result["student_exists"] and validation_result["course_exists"]:
                course_students = await self.get_course_students(course_id)
                student_enrolled = any(s.get("user_id") == student_id for s in course_students)
                validation_result["student_enrolled"] = student_enrolled
                
                if not student_enrolled:
                    validation_result["errors"].append(f"Étudiant {student_id} non inscrit au cours {course_id}")
            
            # Déterminer la validité globale
            validation_result["valid"] = (
                validation_result["student_exists"] and
                validation_result["course_exists"] and
                validation_result["student_enrolled"] and
                validation_result["course_active"]
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Erreur validation demande présence: {e}")
            validation_result["errors"].append(f"Erreur de validation: {str(e)}")
            return validation_result
    
    async def get_current_schedule(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer le créneau horaire actuel d'un cours"""
        try:
            now = datetime.now()
            schedules = await self.get_course_schedule(course_id, now.date())
            
            # Trouver le créneau actuel
            for schedule in schedules:
                start_time = datetime.fromisoformat(schedule.get("start_time", ""))
                end_time = datetime.fromisoformat(schedule.get("end_time", ""))
                
                # Ajouter une marge de 30 minutes avant et après
                margin = 30 * 60  # 30 minutes en secondes
                if (start_time.timestamp() - margin) <= now.timestamp() <= (end_time.timestamp() + margin):
                    return schedule
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur récupération créneau actuel: {e}")
            return None
    
    def is_service_available(self, service_name: str) -> bool:
        """Vérifier si un service est disponible"""
        service_urls = {
            "auth": self.auth_service_url,
            "user": self.user_service_url,
            "course": self.course_service_url,
            "face_recognition": self.face_recognition_service_url
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
