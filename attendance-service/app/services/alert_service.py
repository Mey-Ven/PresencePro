"""
Service de gestion des alertes et notifications de présence
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import logging
import json

from app.models.attendance import Attendance, AttendanceAlert, AttendanceStatus
from app.models.schemas import AttendanceAlert as AttendanceAlertSchema
from app.core.config import settings


class AlertService:
    """Service de gestion des alertes de présence"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def create_alert(
        self,
        alert_type: str,
        student_id: str,
        title: str,
        message: str,
        severity: str = "medium",
        course_id: Optional[int] = None,
        context_data: Optional[Dict[str, Any]] = None
    ) -> AttendanceAlertSchema:
        """Créer une nouvelle alerte"""
        try:
            alert = AttendanceAlert(
                alert_type=alert_type,
                severity=severity,
                student_id=student_id,
                course_id=course_id,
                title=title,
                message=message,
                context_data=json.dumps(context_data) if context_data else None
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            self.logger.info(f"Alerte créée: {alert_type} pour étudiant {student_id}")
            return AttendanceAlertSchema.from_orm(alert)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur création alerte: {e}")
            raise
    
    def check_absence_patterns(self, student_id: str, course_id: Optional[int] = None) -> List[AttendanceAlertSchema]:
        """Vérifier les patterns d'absence et créer des alertes si nécessaire"""
        alerts = []
        
        try:
            # Période d'analyse (dernières 4 semaines)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(weeks=4)
            
            # Récupérer les présences de la période
            query = self.db.query(Attendance).filter(
                and_(
                    Attendance.student_id == student_id,
                    func.date(Attendance.marked_at) >= start_date,
                    func.date(Attendance.marked_at) <= end_date
                )
            )
            
            if course_id:
                query = query.filter(Attendance.course_id == course_id)
            
            attendances = query.all()
            
            if not attendances:
                return alerts
            
            # Analyser les patterns
            total_sessions = len(attendances)
            absent_sessions = len([a for a in attendances if a.status == AttendanceStatus.ABSENT])
            late_sessions = len([a for a in attendances if a.status == AttendanceStatus.LATE])
            
            absence_rate = absent_sessions / total_sessions
            late_rate = late_sessions / total_sessions
            
            # Alertes basées sur les taux
            if absence_rate > 0.3:  # Plus de 30% d'absences
                severity = "high" if absence_rate > 0.5 else "medium"
                alert = self.create_alert(
                    alert_type="high_absence_rate",
                    student_id=student_id,
                    course_id=course_id,
                    title="Taux d'absence élevé",
                    message=f"Taux d'absence de {absence_rate:.1%} sur les 4 dernières semaines",
                    severity=severity,
                    context_data={
                        "absence_rate": absence_rate,
                        "total_sessions": total_sessions,
                        "absent_sessions": absent_sessions,
                        "period_start": start_date.isoformat(),
                        "period_end": end_date.isoformat()
                    }
                )
                alerts.append(alert)
            
            if late_rate > 0.4:  # Plus de 40% de retards
                alert = self.create_alert(
                    alert_type="frequent_lateness",
                    student_id=student_id,
                    course_id=course_id,
                    title="Retards fréquents",
                    message=f"Taux de retard de {late_rate:.1%} sur les 4 dernières semaines",
                    severity="medium",
                    context_data={
                        "late_rate": late_rate,
                        "total_sessions": total_sessions,
                        "late_sessions": late_sessions,
                        "period_start": start_date.isoformat(),
                        "period_end": end_date.isoformat()
                    }
                )
                alerts.append(alert)
            
            # Vérifier les absences consécutives
            consecutive_absences = self._count_consecutive_absences(attendances)
            if consecutive_absences >= 3:
                severity = "critical" if consecutive_absences >= 5 else "high"
                alert = self.create_alert(
                    alert_type="consecutive_absences",
                    student_id=student_id,
                    course_id=course_id,
                    title="Absences consécutives",
                    message=f"{consecutive_absences} absences consécutives détectées",
                    severity=severity,
                    context_data={
                        "consecutive_count": consecutive_absences
                    }
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Erreur vérification patterns absence: {e}")
            return alerts
    
    def _count_consecutive_absences(self, attendances: List[Attendance]) -> int:
        """Compter les absences consécutives récentes"""
        # Trier par date décroissante
        sorted_attendances = sorted(attendances, key=lambda a: a.marked_at, reverse=True)
        
        consecutive_count = 0
        for attendance in sorted_attendances:
            if attendance.status == AttendanceStatus.ABSENT:
                consecutive_count += 1
            else:
                break
        
        return consecutive_count
    
    def check_daily_alerts(self) -> List[AttendanceAlertSchema]:
        """Vérifier les alertes quotidiennes"""
        alerts = []
        
        try:
            today = datetime.now().date()
            
            # Étudiants absents aujourd'hui
            today_absences = self.db.query(Attendance).filter(
                and_(
                    func.date(Attendance.marked_at) == today,
                    Attendance.status == AttendanceStatus.ABSENT
                )
            ).all()
            
            # Grouper par étudiant
            student_absences = {}
            for absence in today_absences:
                if absence.student_id not in student_absences:
                    student_absences[absence.student_id] = []
                student_absences[absence.student_id].append(absence)
            
            # Créer des alertes pour les étudiants avec plusieurs absences aujourd'hui
            for student_id, absences in student_absences.items():
                if len(absences) > 1:
                    alert = self.create_alert(
                        alert_type="multiple_daily_absences",
                        student_id=student_id,
                        title="Multiples absences aujourd'hui",
                        message=f"{len(absences)} absences enregistrées aujourd'hui",
                        severity="medium",
                        context_data={
                            "absence_count": len(absences),
                            "courses": [a.course_id for a in absences],
                            "date": today.isoformat()
                        }
                    )
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Erreur vérification alertes quotidiennes: {e}")
            return alerts
    
    def get_student_alerts(
        self,
        student_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[AttendanceAlertSchema]:
        """Récupérer les alertes d'un étudiant"""
        try:
            query = self.db.query(AttendanceAlert).filter(AttendanceAlert.student_id == student_id)
            
            if unread_only:
                query = query.filter(AttendanceAlert.is_read == False)
            
            alerts = query.order_by(desc(AttendanceAlert.created_at)).limit(limit).all()
            
            return [AttendanceAlertSchema.from_orm(alert) for alert in alerts]
            
        except Exception as e:
            self.logger.error(f"Erreur récupération alertes étudiant: {e}")
            return []
    
    def mark_alert_as_read(self, alert_id: int) -> bool:
        """Marquer une alerte comme lue"""
        try:
            alert = self.db.query(AttendanceAlert).filter(AttendanceAlert.id == alert_id).first()
            
            if alert:
                alert.is_read = True
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur marquage alerte lue: {e}")
            return False
    
    def resolve_alert(self, alert_id: int, resolved_by: str) -> bool:
        """Résoudre une alerte"""
        try:
            alert = self.db.query(AttendanceAlert).filter(AttendanceAlert.id == alert_id).first()
            
            if alert:
                alert.is_resolved = True
                alert.resolved_by = resolved_by
                alert.resolved_at = datetime.now()
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur résolution alerte: {e}")
            return False
    
    def get_pending_alerts_count(self) -> int:
        """Compter les alertes en attente"""
        try:
            return self.db.query(AttendanceAlert).filter(
                and_(
                    AttendanceAlert.is_read == False,
                    AttendanceAlert.is_resolved == False
                )
            ).count()
            
        except Exception as e:
            self.logger.error(f"Erreur comptage alertes en attente: {e}")
            return 0
