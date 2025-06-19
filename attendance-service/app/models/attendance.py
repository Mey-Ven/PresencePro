"""
Modèles de données pour la gestion des présences
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.database import Base


class AttendanceStatus(PyEnum):
    """Statuts de présence"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    PARTIAL = "partial"  # Présence partielle


class AttendanceMethod(PyEnum):
    """Méthodes d'enregistrement de présence"""
    MANUAL = "manual"
    FACE_RECOGNITION = "face_recognition"
    QR_CODE = "qr_code"
    RFID = "rfid"
    API = "api"


class Attendance(Base):
    """Modèle principal pour les présences"""
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Références vers les autres services
    student_id = Column(String(50), nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    schedule_id = Column(Integer, nullable=True, index=True)  # Référence vers course-service
    
    # Informations de présence
    status = Column(Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.ABSENT)
    method = Column(Enum(AttendanceMethod), nullable=False, default=AttendanceMethod.MANUAL)
    
    # Horodatage
    scheduled_start_time = Column(DateTime(timezone=True), nullable=True)
    scheduled_end_time = Column(DateTime(timezone=True), nullable=True)
    actual_arrival_time = Column(DateTime(timezone=True), nullable=True)
    actual_departure_time = Column(DateTime(timezone=True), nullable=True)
    marked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Métadonnées
    confidence_score = Column(Float, nullable=True)  # Pour reconnaissance faciale
    location = Column(String(100), nullable=True)  # Salle, bâtiment
    device_id = Column(String(100), nullable=True)  # ID du dispositif d'enregistrement
    
    # Commentaires et justifications
    notes = Column(Text, nullable=True)
    excuse_reason = Column(String(255), nullable=True)
    excuse_document_url = Column(String(500), nullable=True)
    
    # Validation et modification
    is_validated = Column(Boolean, default=False)
    validated_by = Column(String(50), nullable=True)  # ID de l'utilisateur validateur
    validated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Attendance(student_id='{self.student_id}', course_id={self.course_id}, status='{self.status}')>"


class AttendanceSession(Base):
    """Sessions de présence pour grouper les enregistrements"""
    __tablename__ = "attendance_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String(100), nullable=False)
    course_id = Column(Integer, nullable=False, index=True)
    schedule_id = Column(Integer, nullable=True, index=True)
    
    # Période de la session
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    # Configuration
    auto_mark_absent = Column(Boolean, default=True)
    grace_period_minutes = Column(Integer, default=15)
    
    # Statut de la session
    is_active = Column(Boolean, default=True)
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    closed_by = Column(String(50), nullable=True)
    
    # Statistiques
    total_students = Column(Integer, default=0)
    present_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)
    late_count = Column(Integer, default=0)
    
    # Audit
    created_by = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    # attendances = relationship("Attendance", backref="session", foreign_keys="Attendance.schedule_id")
    
    def __repr__(self):
        return f"<AttendanceSession(name='{self.session_name}', course_id={self.course_id})>"


class AttendanceRule(Base):
    """Règles de présence pour automatiser les processus"""
    __tablename__ = "attendance_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scope de la règle
    course_id = Column(Integer, nullable=True, index=True)  # Null = règle globale
    student_id = Column(String(50), nullable=True, index=True)  # Null = tous les étudiants
    
    # Configuration de la règle
    auto_mark_absent_after_minutes = Column(Integer, default=120)
    late_threshold_minutes = Column(Integer, default=10)
    grace_period_minutes = Column(Integer, default=15)
    
    # Conditions
    require_excuse_for_absence = Column(Boolean, default=False)
    allow_late_marking = Column(Boolean, default=True)
    max_late_markings_per_week = Column(Integer, nullable=True)
    
    # Statut
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Plus élevé = plus prioritaire
    
    # Audit
    created_by = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AttendanceRule(name='{self.name}', course_id={self.course_id})>"


class AttendanceAlert(Base):
    """Alertes de présence pour notifications"""
    __tablename__ = "attendance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Type d'alerte
    alert_type = Column(String(50), nullable=False)  # absence_pattern, late_pattern, etc.
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Cible de l'alerte
    student_id = Column(String(50), nullable=False, index=True)
    course_id = Column(Integer, nullable=True, index=True)
    
    # Contenu de l'alerte
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Données contextuelles
    context_data = Column(Text, nullable=True)  # JSON avec données supplémentaires
    
    # Statut
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(String(50), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AttendanceAlert(type='{self.alert_type}', student_id='{self.student_id}')>"
