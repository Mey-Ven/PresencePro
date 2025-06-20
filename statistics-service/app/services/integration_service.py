"""
Service d'intégration avec les autres microservices PresencePro
"""
import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import date, datetime
import asyncio
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.statistics import AttendanceRecord

logger = logging.getLogger(__name__)


class IntegrationService:
    """Service d'intégration avec les autres microservices"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(settings.query_timeout_seconds)
        self.auth_service_url = settings.auth_service_url
        self.user_service_url = settings.user_service_url
        self.course_service_url = settings.course_service_url
        self.attendance_service_url = settings.attendance_service_url
        self.justification_service_url = settings.justification_service_url
    
    async def sync_attendance_data(
        self, 
        start_date: date = None, 
        end_date: date = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Synchroniser les données de présence depuis attendance-service"""
        try:
            logger.info("🔄 Synchronisation des données de présence...")
            
            # Paramètres de requête
            params = {}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            if force_refresh:
                params["force_refresh"] = "true"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Récupérer les données de présence
                response = await client.get(
                    f"{self.attendance_service_url}/attendance/records",
                    params=params
                )
                
                if response.status_code == 200:
                    attendance_data = response.json()
                    
                    # Sauvegarder en base locale pour les statistiques
                    saved_count = await self._save_attendance_records(attendance_data.get("records", []))
                    
                    logger.info(f"✅ {saved_count} enregistrements de présence synchronisés")
                    
                    return {
                        "success": True,
                        "records_synced": saved_count,
                        "source": "attendance-service",
                        "timestamp": datetime.now()
                    }
                else:
                    logger.error(f"Erreur récupération données présence: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "timestamp": datetime.now()
                    }
                    
        except Exception as e:
            logger.error(f"Erreur synchronisation données présence: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def get_student_info(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un étudiant"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.user_service_url}/users/{student_id}")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Étudiant {student_id} non trouvé: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur récupération info étudiant {student_id}: {e}")
            return None
    
    async def get_class_info(self, class_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'une classe"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.course_service_url}/classes/{class_id}")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Classe {class_id} non trouvée: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur récupération info classe {class_id}: {e}")
            return None
    
    async def get_course_info(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un cours"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.course_service_url}/courses/{course_id}")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Cours {course_id} non trouvé: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur récupération info cours {course_id}: {e}")
            return None
    
    async def get_justifications(
        self, 
        student_id: str = None, 
        start_date: date = None, 
        end_date: date = None
    ) -> List[Dict[str, Any]]:
        """Récupérer les justifications d'absence"""
        try:
            params = {}
            if student_id:
                params["student_id"] = student_id
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.justification_service_url}/justifications",
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json().get("justifications", [])
                else:
                    logger.warning(f"Erreur récupération justifications: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erreur récupération justifications: {e}")
            return []
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Valider un token JWT avec auth-service"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_service_url}/auth/validate",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Token invalide: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur validation token: {e}")
            return None
    
    async def get_user_permissions(self, user_id: str, token: str) -> List[str]:
        """Récupérer les permissions d'un utilisateur"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_service_url}/auth/permissions/{user_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json().get("permissions", [])
                else:
                    logger.warning(f"Erreur récupération permissions: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erreur récupération permissions: {e}")
            return []
    
    async def _save_attendance_records(self, records: List[Dict[str, Any]]) -> int:
        """Sauvegarder les enregistrements de présence en base locale"""
        try:
            db = SessionLocal()
            saved_count = 0
            
            for record_data in records:
                try:
                    # Vérifier si l'enregistrement existe déjà
                    existing = db.query(AttendanceRecord).filter(
                        AttendanceRecord.student_id == record_data.get("student_id"),
                        AttendanceRecord.course_id == record_data.get("course_id"),
                        AttendanceRecord.date == datetime.fromisoformat(record_data.get("date")).date()
                    ).first()
                    
                    if not existing:
                        # Créer un nouvel enregistrement
                        attendance_record = AttendanceRecord(
                            student_id=record_data.get("student_id"),
                            course_id=record_data.get("course_id"),
                            class_id=record_data.get("class_id"),
                            teacher_id=record_data.get("teacher_id"),
                            date=datetime.fromisoformat(record_data.get("date")).date(),
                            time_slot=record_data.get("time_slot"),
                            status=record_data.get("status"),
                            detection_method=record_data.get("detection_method"),
                            confidence_score=record_data.get("confidence_score"),
                            is_justified=record_data.get("is_justified", False),
                            justification_id=record_data.get("justification_id")
                        )
                        
                        db.add(attendance_record)
                        saved_count += 1
                    else:
                        # Mettre à jour l'enregistrement existant si nécessaire
                        if existing.status != record_data.get("status"):
                            existing.status = record_data.get("status")
                            existing.is_justified = record_data.get("is_justified", False)
                            existing.justification_id = record_data.get("justification_id")
                            existing.updated_at = datetime.now()
                            saved_count += 1
                
                except Exception as e:
                    logger.error(f"Erreur sauvegarde enregistrement: {e}")
                    continue
            
            db.commit()
            db.close()
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde enregistrements présence: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
            return 0
    
    async def check_services_health(self) -> Dict[str, bool]:
        """Vérifier la santé des services externes"""
        services_status = {}
        
        services = {
            "auth-service": f"{self.auth_service_url}/health",
            "user-service": f"{self.user_service_url}/health",
            "course-service": f"{self.course_service_url}/health",
            "attendance-service": f"{self.attendance_service_url}/health",
            "justification-service": f"{self.justification_service_url}/health"
        }
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            for service_name, health_url in services.items():
                try:
                    response = await client.get(health_url)
                    services_status[service_name] = response.status_code == 200
                except Exception as e:
                    logger.warning(f"Service {service_name} non disponible: {e}")
                    services_status[service_name] = False
        
        return services_status
    
    async def enrich_statistics_with_metadata(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichir les statistiques avec des métadonnées des autres services"""
        try:
            enriched_data = stats_data.copy()
            
            # Enrichir avec les informations d'étudiant si applicable
            if "student_id" in stats_data:
                student_info = await self.get_student_info(stats_data["student_id"])
                if student_info:
                    enriched_data["student_info"] = {
                        "name": student_info.get("name"),
                        "email": student_info.get("email"),
                        "class_id": student_info.get("class_id")
                    }
            
            # Enrichir avec les informations de classe si applicable
            if "class_id" in stats_data:
                class_info = await self.get_class_info(stats_data["class_id"])
                if class_info:
                    enriched_data["class_info"] = {
                        "name": class_info.get("name"),
                        "level": class_info.get("level"),
                        "teacher_id": class_info.get("teacher_id")
                    }
            
            # Ajouter les justifications si applicable
            if "student_id" in stats_data and "period_start" in stats_data:
                justifications = await self.get_justifications(
                    student_id=stats_data["student_id"],
                    start_date=stats_data["period_start"],
                    end_date=stats_data["period_end"]
                )
                enriched_data["justifications_count"] = len(justifications)
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Erreur enrichissement statistiques: {e}")
            return stats_data


# Instance globale du service
integration_service = IntegrationService()
