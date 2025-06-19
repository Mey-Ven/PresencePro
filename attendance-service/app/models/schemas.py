"""
Schémas Pydantic pour la validation des données
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum


class AttendanceStatus(str, Enum):
    """Statuts de présence"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    PARTIAL = "partial"


class AttendanceMethod(str, Enum):
    """Méthodes d'enregistrement"""
    MANUAL = "manual"
    FACE_RECOGNITION = "face_recognition"
    QR_CODE = "qr_code"
    RFID = "rfid"
    API = "api"


class AttendanceMarkRequest(BaseModel):
    """Requête pour marquer une présence"""
    student_id: str = Field(..., description="ID de l'étudiant")
    course_id: Optional[int] = Field(None, description="ID du cours")
    schedule_id: Optional[int] = Field(None, description="ID du créneau horaire")
    status: AttendanceStatus = Field(AttendanceStatus.PRESENT, description="Statut de présence")
    method: AttendanceMethod = Field(AttendanceMethod.MANUAL, description="Méthode d'enregistrement")
    
    # Horodatage optionnel (défaut: maintenant)
    marked_time: Optional[datetime] = Field(None, description="Heure de marquage")
    
    # Métadonnées optionnelles
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Score de confiance")
    location: Optional[str] = Field(None, max_length=100, description="Localisation")
    device_id: Optional[str] = Field(None, max_length=100, description="ID du dispositif")
    notes: Optional[str] = Field(None, description="Notes additionnelles")
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Le score de confiance doit être entre 0.0 et 1.0')
        return v


class AttendanceUpdate(BaseModel):
    """Mise à jour d'une présence"""
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None
    excuse_reason: Optional[str] = None
    excuse_document_url: Optional[str] = None
    is_validated: Optional[bool] = None


class AttendanceResponse(BaseModel):
    """Réponse pour une présence"""
    id: int
    student_id: str
    course_id: Optional[int] = None
    schedule_id: Optional[int] = None
    status: AttendanceStatus
    method: AttendanceMethod
    
    # Horodatage
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    actual_arrival_time: Optional[datetime] = None
    actual_departure_time: Optional[datetime] = None
    marked_at: datetime
    
    # Métadonnées
    confidence_score: Optional[float] = None
    location: Optional[str] = None
    device_id: Optional[str] = None
    notes: Optional[str] = None
    excuse_reason: Optional[str] = None
    
    # Validation
    is_validated: bool
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    
    # Audit
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


class AttendanceSessionCreate(BaseModel):
    """Création d'une session de présence"""
    session_name: str = Field(..., max_length=100, description="Nom de la session")
    course_id: int = Field(..., description="ID du cours")
    schedule_id: Optional[int] = Field(None, description="ID du créneau")
    start_time: datetime = Field(..., description="Heure de début")
    end_time: datetime = Field(..., description="Heure de fin")
    auto_mark_absent: bool = Field(True, description="Marquer automatiquement absent")
    grace_period_minutes: int = Field(15, ge=0, le=60, description="Période de grâce en minutes")


class AttendanceSessionResponse(BaseModel):
    """Réponse pour une session de présence"""
    id: int
    session_name: str
    course_id: int
    schedule_id: Optional[int] = None
    start_time: datetime
    end_time: datetime
    is_active: bool
    is_closed: bool
    
    # Statistiques
    total_students: int
    present_count: int
    absent_count: int
    late_count: int
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceStats(BaseModel):
    """Statistiques de présence"""
    total_sessions: int
    total_attendances: int
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    attendance_rate: float
    punctuality_rate: float


class StudentAttendanceReport(BaseModel):
    """Rapport de présence pour un étudiant"""
    student_id: str
    student_name: Optional[str] = None
    period_start: date
    period_end: date
    
    # Statistiques globales
    total_sessions: int
    attended_sessions: int
    missed_sessions: int
    late_sessions: int
    attendance_rate: float
    
    # Détail par cours
    course_stats: List[Dict[str, Any]] = []
    
    # Tendances
    weekly_attendance: List[Dict[str, Any]] = []
    recent_absences: List[AttendanceResponse] = []


class CourseAttendanceReport(BaseModel):
    """Rapport de présence pour un cours"""
    course_id: int
    course_name: Optional[str] = None
    period_start: date
    period_end: date
    
    # Statistiques globales
    total_sessions: int
    total_students: int
    average_attendance_rate: float
    
    # Détail par session
    session_stats: List[Dict[str, Any]] = []
    
    # Étudiants avec problèmes
    low_attendance_students: List[Dict[str, Any]] = []
    frequent_late_students: List[Dict[str, Any]] = []


class AttendanceAlert(BaseModel):
    """Alerte de présence"""
    id: int
    alert_type: str
    severity: str
    student_id: str
    course_id: Optional[int] = None
    title: str
    message: str
    is_read: bool
    is_resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class BulkAttendanceRequest(BaseModel):
    """Requête pour marquer plusieurs présences"""
    course_id: int
    schedule_id: Optional[int] = None
    session_name: Optional[str] = None
    attendances: List[AttendanceMarkRequest]
    
    @validator('attendances')
    def validate_attendances(cls, v):
        if not v:
            raise ValueError('Au moins une présence doit être fournie')
        if len(v) > 1000:
            raise ValueError('Maximum 1000 présences par requête')
        return v


class AttendanceExportRequest(BaseModel):
    """Requête d'export de présences"""
    format: str = Field("excel", pattern="^(excel|csv|pdf)$")
    course_id: Optional[int] = None
    student_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_stats: bool = True
    include_charts: bool = False


class ServiceHealth(BaseModel):
    """Santé du service"""
    status: str
    service: str
    version: str
    database_connected: bool
    total_attendances: int
    active_sessions: int
    pending_alerts: int
