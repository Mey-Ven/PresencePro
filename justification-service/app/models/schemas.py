"""
Schémas Pydantic pour la validation des données
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class JustificationStatus(str, Enum):
    """Statuts de justification"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PARENT_PENDING = "parent_pending"
    PARENT_APPROVED = "parent_approved"
    PARENT_REJECTED = "parent_rejected"
    ADMIN_PENDING = "admin_pending"
    ADMIN_APPROVED = "admin_approved"
    ADMIN_REJECTED = "admin_rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class JustificationType(str, Enum):
    """Types de justification"""
    MEDICAL = "medical"
    FAMILY = "family"
    TRANSPORT = "transport"
    PERSONAL = "personal"
    ACADEMIC = "academic"
    OTHER = "other"


class JustificationPriority(str, Enum):
    """Priorités de justification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class JustificationCreate(BaseModel):
    """Création d'une justification"""
    title: str = Field(..., min_length=5, max_length=200, description="Titre de la justification")
    description: str = Field(..., min_length=10, description="Description détaillée")
    justification_type: JustificationType = Field(JustificationType.OTHER, description="Type de justification")
    priority: JustificationPriority = Field(JustificationPriority.MEDIUM, description="Priorité")
    
    # Dates d'absence
    absence_start_date: datetime = Field(..., description="Date de début d'absence")
    absence_end_date: datetime = Field(..., description="Date de fin d'absence")
    
    # Références optionnelles
    course_id: Optional[int] = Field(None, description="ID du cours concerné")
    attendance_id: Optional[int] = Field(None, description="ID de la présence à justifier")
    
    # Métadonnées
    notes: Optional[str] = Field(None, description="Notes additionnelles")
    
    @validator('absence_end_date')
    def validate_dates(cls, v, values):
        if 'absence_start_date' in values and v < values['absence_start_date']:
            raise ValueError('La date de fin doit être postérieure à la date de début')
        return v


class JustificationUpdate(BaseModel):
    """Mise à jour d'une justification"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    justification_type: Optional[JustificationType] = None
    priority: Optional[JustificationPriority] = None
    absence_start_date: Optional[datetime] = None
    absence_end_date: Optional[datetime] = None
    notes: Optional[str] = None


class JustificationApproval(BaseModel):
    """Approbation/Rejet d'une justification"""
    approved: bool = Field(..., description="Approuvé ou rejeté")
    comment: Optional[str] = Field(None, description="Commentaire sur la décision")
    internal_notes: Optional[str] = Field(None, description="Notes internes (admin seulement)")


class JustificationResponse(BaseModel):
    """Réponse pour une justification"""
    id: int
    student_id: str
    course_id: Optional[int] = None
    attendance_id: Optional[int] = None
    
    # Contenu
    title: str
    description: str
    justification_type: JustificationType
    priority: JustificationPriority
    
    # Dates
    absence_start_date: datetime
    absence_end_date: datetime
    
    # Workflow
    status: JustificationStatus
    
    # Approbation parentale
    parent_approval_required: bool
    parent_approved_by: Optional[str] = None
    parent_approved_at: Optional[datetime] = None
    parent_rejection_reason: Optional[str] = None
    
    # Validation administrative
    admin_validation_required: bool
    admin_validated_by: Optional[str] = None
    admin_validated_at: Optional[datetime] = None
    admin_rejection_reason: Optional[str] = None
    
    # Métadonnées
    notes: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Audit
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Documents attachés
    documents: List['JustificationDocumentResponse'] = []
    
    class Config:
        from_attributes = True
        use_enum_values = True


class JustificationDocumentResponse(BaseModel):
    """Réponse pour un document de justification"""
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    description: Optional[str] = None
    is_primary: bool
    uploaded_by: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class JustificationHistoryResponse(BaseModel):
    """Réponse pour l'historique d'une justification"""
    id: int
    action: str
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    comment: Optional[str] = None
    changed_by: str
    changed_at: datetime
    
    class Config:
        from_attributes = True


class JustificationStats(BaseModel):
    """Statistiques des justifications"""
    total_justifications: int
    pending_approval: int
    pending_validation: int
    approved: int
    rejected: int
    expired: int
    
    # Par type
    by_type: Dict[str, int] = {}
    
    # Par priorité
    by_priority: Dict[str, int] = {}
    
    # Taux d'approbation
    approval_rate: float
    average_processing_time_hours: float


class StudentJustificationReport(BaseModel):
    """Rapport de justifications pour un étudiant"""
    student_id: str
    student_name: Optional[str] = None
    period_start: date
    period_end: date
    
    # Statistiques
    total_justifications: int
    approved_justifications: int
    rejected_justifications: int
    pending_justifications: int
    
    # Détails
    justifications: List[JustificationResponse] = []
    
    # Tendances
    most_common_type: Optional[str] = None
    average_processing_time: Optional[float] = None


class JustificationTemplate(BaseModel):
    """Template de justification"""
    id: Optional[int] = None
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    justification_type: JustificationType
    title_template: str = Field(..., min_length=5, max_length=200)
    description_template: str = Field(..., min_length=10)
    default_priority: JustificationPriority = JustificationPriority.MEDIUM
    requires_documents: bool = False
    max_absence_days: Optional[int] = Field(None, ge=1, le=365)
    is_active: bool = True
    is_public: bool = True
    
    class Config:
        from_attributes = True
        use_enum_values = True


class JustificationNotificationResponse(BaseModel):
    """Réponse pour une notification"""
    id: int
    justification_id: int
    recipient_type: str
    notification_type: str
    title: str
    message: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class BulkJustificationAction(BaseModel):
    """Action en lot sur les justifications"""
    justification_ids: List[int] = Field(..., min_items=1, max_items=100)
    action: str = Field(..., pattern="^(approve|reject|expire|cancel)$")
    comment: Optional[str] = None


class JustificationSearchFilters(BaseModel):
    """Filtres de recherche pour les justifications"""
    student_id: Optional[str] = None
    course_id: Optional[int] = None
    status: Optional[JustificationStatus] = None
    justification_type: Optional[JustificationType] = None
    priority: Optional[JustificationPriority] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_by: Optional[str] = None
    
    # Pagination
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class ServiceHealth(BaseModel):
    """Santé du service"""
    status: str
    service: str
    version: str
    database_connected: bool
    total_justifications: int
    pending_approvals: int
    pending_validations: int
    upload_directory_writable: bool


# Mise à jour des références forward
JustificationResponse.model_rebuild()
