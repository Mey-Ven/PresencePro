"""
Service principal de gestion des présences
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging
from dateutil import tz

from app.models.attendance import Attendance, AttendanceSession, AttendanceStatus, AttendanceMethod
from app.models.schemas import (
    AttendanceMarkRequest, AttendanceUpdate, AttendanceResponse,
    AttendanceStats, StudentAttendanceReport, CourseAttendanceReport
)
from app.core.config import settings


class AttendanceService:
    """Service de gestion des présences"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.timezone = tz.gettz(settings.default_timezone)

    def create_session(self, session_data: dict) -> Dict[str, Any]: # Replace dict with actual Pydantic model if available
        """Crée une nouvelle session de présence. À IMPLÉMENTER."""
        # Placeholder implementation
        # session = AttendanceSession(**session_data.dict()) # Assuming session_data is a Pydantic model
        # self.db.add(session)
        # self.db.commit()
        # self.db.refresh(session)
        # return session # Or a Pydantic response model
        self.logger.info(f"Création de session (simulation) pour le cours: {session_data.course_id}")
        return {
            "session_id": f"session_{datetime.now().timestamp()}",
            "course_id": session_data.course_id,
            "schedule_id": session_data.schedule_id,
            "start_time": session_data.start_time,
            "end_time": session_data.end_time,
            "status": "active",
            "created_at": datetime.now()
        }

    def mark_attendance(self, request: AttendanceMarkRequest, created_by: str = None) -> AttendanceResponse:
        """Marquer une présence"""
        try:
            # Vérifier si une présence existe déjà pour cette combinaison
            existing = self.db.query(Attendance).filter(
                and_(
                    Attendance.student_id == request.student_id,
                    Attendance.course_id == request.course_id,
                    func.date(Attendance.marked_at) == func.date(request.marked_time or datetime.now())
                )
            ).first()
            
            if existing:
                # Mettre à jour la présence existante
                existing.status = request.status
                existing.method = request.method
                existing.confidence_score = request.confidence_score
                existing.location = request.location
                existing.device_id = request.device_id
                existing.notes = request.notes
                existing.updated_by = created_by
                existing.updated_at = datetime.now()
                
                if request.status == AttendanceStatus.PRESENT and not existing.actual_arrival_time:
                    existing.actual_arrival_time = request.marked_time or datetime.now()
                
                attendance = existing
            else:
                # Créer une nouvelle présence
                attendance = Attendance(
                    student_id=request.student_id,
                    course_id=request.course_id,
                    schedule_id=request.schedule_id,
                    status=request.status,
                    method=request.method,
                    confidence_score=request.confidence_score,
                    location=request.location,
                    device_id=request.device_id,
                    notes=request.notes,
                    created_by=created_by,
                    marked_at=request.marked_time or datetime.now()
                )
                
                if request.status == AttendanceStatus.PRESENT:
                    attendance.actual_arrival_time = request.marked_time or datetime.now()
                
                self.db.add(attendance)
            
            self.db.commit()
            self.db.refresh(attendance)
            
            self.logger.info(f"Présence marquée: {request.student_id} - {request.status}")
            return AttendanceResponse.from_orm(attendance)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur marquage présence: {e}")
            raise
    
    def get_student_attendance(
        self, 
        student_id: str, 
        course_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[AttendanceResponse]:
        """Récupérer les présences d'un étudiant"""
        try:
            query = self.db.query(Attendance).filter(Attendance.student_id == student_id)
            
            if course_id:
                query = query.filter(Attendance.course_id == course_id)
            
            if start_date:
                query = query.filter(func.date(Attendance.marked_at) >= start_date)
            
            if end_date:
                query = query.filter(func.date(Attendance.marked_at) <= end_date)
            
            attendances = query.order_by(desc(Attendance.marked_at)).limit(limit).all()
            
            return [AttendanceResponse.from_orm(att) for att in attendances]
            
        except Exception as e:
            self.logger.error(f"Erreur récupération présences étudiant: {e}")
            raise
    
    def get_course_attendance(
        self,
        course_id: int,
        session_date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AttendanceResponse]:
        """Récupérer les présences d'un cours"""
        try:
            query = self.db.query(Attendance).filter(Attendance.course_id == course_id)
            
            if session_date:
                query = query.filter(func.date(Attendance.marked_at) == session_date)
            elif start_date and end_date:
                query = query.filter(
                    and_(
                        func.date(Attendance.marked_at) >= start_date,
                        func.date(Attendance.marked_at) <= end_date
                    )
                )
            
            attendances = query.order_by(desc(Attendance.marked_at)).all()
            
            return [AttendanceResponse.from_orm(att) for att in attendances]
            
        except Exception as e:
            self.logger.error(f"Erreur récupération présences cours: {e}")
            raise
    
    def update_attendance(self, attendance_id: int, update: AttendanceUpdate, updated_by: str = None) -> AttendanceResponse:
        """Mettre à jour une présence"""
        try:
            attendance = self.db.query(Attendance).filter(Attendance.id == attendance_id).first()
            
            if not attendance:
                raise ValueError(f"Présence {attendance_id} non trouvée")
            
            # Mettre à jour les champs fournis
            update_data = update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(attendance, field, value)
            
            attendance.updated_by = updated_by
            attendance.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(attendance)
            
            return AttendanceResponse.from_orm(attendance)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur mise à jour présence: {e}")
            raise
    
    def get_attendance_stats(
        self,
        course_id: Optional[int] = None,
        student_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> AttendanceStats:
        """Calculer les statistiques de présence"""
        try:
            query = self.db.query(Attendance)
            
            if course_id:
                query = query.filter(Attendance.course_id == course_id)
            
            if student_id:
                query = query.filter(Attendance.student_id == student_id)
            
            if start_date:
                query = query.filter(func.date(Attendance.marked_at) >= start_date)
            
            if end_date:
                query = query.filter(func.date(Attendance.marked_at) <= end_date)
            
            # Compter par statut
            total_attendances = query.count()
            present_count = query.filter(Attendance.status == AttendanceStatus.PRESENT).count()
            absent_count = query.filter(Attendance.status == AttendanceStatus.ABSENT).count()
            late_count = query.filter(Attendance.status == AttendanceStatus.LATE).count()
            excused_count = query.filter(Attendance.status == AttendanceStatus.EXCUSED).count()
            
            # Calculer les taux
            attendance_rate = (present_count + late_count) / total_attendances if total_attendances > 0 else 0
            punctuality_rate = present_count / (present_count + late_count) if (present_count + late_count) > 0 else 0
            
            # Compter les sessions uniques
            total_sessions = query.with_entities(
                func.count(func.distinct(func.date(Attendance.marked_at)))
            ).scalar() or 0
            
            return AttendanceStats(
                total_sessions=total_sessions,
                total_attendances=total_attendances,
                present_count=present_count,
                absent_count=absent_count,
                late_count=late_count,
                excused_count=excused_count,
                attendance_rate=round(attendance_rate, 3),
                punctuality_rate=round(punctuality_rate, 3)
            )
            
        except Exception as e:
            self.logger.error(f"Erreur calcul statistiques: {e}")
            raise
    
    def generate_student_report(
        self,
        student_id: str,
        start_date: date,
        end_date: date
    ) -> StudentAttendanceReport:
        """Générer un rapport de présence pour un étudiant"""
        try:
            # Récupérer toutes les présences de la période
            attendances = self.get_student_attendance(
                student_id=student_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
            
            # Calculer les statistiques globales
            total_sessions = len(attendances)
            attended_sessions = len([a for a in attendances if a.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE]])
            missed_sessions = len([a for a in attendances if a.status == AttendanceStatus.ABSENT])
            late_sessions = len([a for a in attendances if a.status == AttendanceStatus.LATE])
            
            attendance_rate = attended_sessions / total_sessions if total_sessions > 0 else 0
            
            # Grouper par cours
            course_stats = {}
            for att in attendances:
                if att.course_id not in course_stats:
                    course_stats[att.course_id] = {
                        "course_id": att.course_id,
                        "total": 0,
                        "present": 0,
                        "absent": 0,
                        "late": 0
                    }
                
                course_stats[att.course_id]["total"] += 1
                if att.status == AttendanceStatus.PRESENT:
                    course_stats[att.course_id]["present"] += 1
                elif att.status == AttendanceStatus.ABSENT:
                    course_stats[att.course_id]["absent"] += 1
                elif att.status == AttendanceStatus.LATE:
                    course_stats[att.course_id]["late"] += 1
            
            # Absences récentes (dernières 10)
            recent_absences = [a for a in attendances if a.status == AttendanceStatus.ABSENT][:10]
            
            return StudentAttendanceReport(
                student_id=student_id,
                period_start=start_date,
                period_end=end_date,
                total_sessions=total_sessions,
                attended_sessions=attended_sessions,
                missed_sessions=missed_sessions,
                late_sessions=late_sessions,
                attendance_rate=round(attendance_rate, 3),
                course_stats=list(course_stats.values()),
                recent_absences=recent_absences
            )
            
        except Exception as e:
            self.logger.error(f"Erreur génération rapport étudiant: {e}")
            raise
    
    def auto_mark_absent(self, course_id: int, schedule_id: int, threshold_hours: int = 2):
        """Marquer automatiquement absent après un délai"""
        try:
            threshold_time = datetime.now() - timedelta(hours=threshold_hours)
            
            # Trouver les étudiants qui devraient être présents mais ne sont pas marqués
            # Cette logique nécessiterait l'intégration avec course-service pour connaître les étudiants inscrits
            
            self.logger.info(f"Auto-marquage absent pour cours {course_id}, créneau {schedule_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur auto-marquage absent: {e}")
            raise
