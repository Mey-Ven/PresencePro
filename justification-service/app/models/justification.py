"""
Modèles de données pour la gestion des justifications
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.database import Base


class JustificationStatus(PyEnum):
    """Statuts de justification"""
    DRAFT = "draft"  # Brouillon
    SUBMITTED = "submitted"  # Soumise par l'étudiant
    PARENT_PENDING = "parent_pending"  # En attente d'approbation parentale
    PARENT_APPROVED = "parent_approved"  # Approuvée par les parents
    PARENT_REJECTED = "parent_rejected"  # Rejetée par les parents
    ADMIN_PENDING = "admin_pending"  # En attente de validation administrative
    ADMIN_APPROVED = "admin_approved"  # Validée par l'administration
    ADMIN_REJECTED = "admin_rejected"  # Rejetée par l'administration
    EXPIRED = "expired"  # Expirée
    CANCELLED = "cancelled"  # Annulée


class JustificationType(PyEnum):
    """Types de justification"""
    MEDICAL = "medical"  # Médical
    FAMILY = "family"  # Familial
    TRANSPORT = "transport"  # Transport
    PERSONAL = "personal"  # Personnel
    ACADEMIC = "academic"  # Académique
    OTHER = "other"  # Autre


class JustificationPriority(PyEnum):
    """Priorités de justification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Justification(Base):
    """Modèle principal pour les justifications"""
    __tablename__ = "justifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Références vers les autres services
    student_id = Column(String(50), nullable=False, index=True)
    course_id = Column(Integer, nullable=True, index=True)
    attendance_id = Column(Integer, nullable=True, index=True)  # Référence vers attendance-service
    
    # Informations de la justification
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    justification_type = Column(String(20), nullable=False, default="other")
    priority = Column(String(10), nullable=False, default="medium")
    
    # Dates concernées
    absence_start_date = Column(DateTime(timezone=True), nullable=False)
    absence_end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Workflow de validation
    status = Column(String(20), nullable=False, default="draft")
    
    # Approbation parentale
    parent_approval_required = Column(Boolean, default=True)
    parent_approved_by = Column(String(50), nullable=True)  # ID du parent
    parent_approved_at = Column(DateTime(timezone=True), nullable=True)
    parent_rejection_reason = Column(Text, nullable=True)
    
    # Validation administrative
    admin_validation_required = Column(Boolean, default=True)
    admin_validated_by = Column(String(50), nullable=True)  # ID de l'administrateur
    admin_validated_at = Column(DateTime(timezone=True), nullable=True)
    admin_rejection_reason = Column(Text, nullable=True)
    
    # Métadonnées
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)  # Notes internes administration
    
    # Dates importantes
    submission_deadline = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_by = Column(String(50), nullable=False)
    updated_by = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    documents = relationship("JustificationDocument", back_populates="justification", cascade="all, delete-orphan")
    history = relationship("JustificationHistory", back_populates="justification", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Justification(id={self.id}, student_id='{self.student_id}', status='{self.status}')>"


class JustificationDocument(Base):
    """Documents attachés aux justifications"""
    __tablename__ = "justification_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    justification_id = Column(Integer, ForeignKey("justifications.id"), nullable=False)
    
    # Informations du fichier
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Métadonnées
    description = Column(String(500), nullable=True)
    is_primary = Column(Boolean, default=False)  # Document principal
    
    # Audit
    uploaded_by = Column(String(50), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    justification = relationship("Justification", back_populates="documents")
    
    def __repr__(self):
        return f"<JustificationDocument(id={self.id}, filename='{self.filename}')>"


class JustificationHistory(Base):
    """Historique des modifications de justifications"""
    __tablename__ = "justification_history"
    
    id = Column(Integer, primary_key=True, index=True)
    justification_id = Column(Integer, ForeignKey("justifications.id"), nullable=False)
    
    # Changement effectué
    action = Column(String(100), nullable=False)  # created, submitted, approved, rejected, etc.
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=True)
    
    # Détails du changement
    comment = Column(Text, nullable=True)
    changed_fields = Column(Text, nullable=True)  # JSON des champs modifiés
    
    # Audit
    changed_by = Column(String(50), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    justification = relationship("Justification", back_populates="history")
    
    def __repr__(self):
        return f"<JustificationHistory(id={self.id}, action='{self.action}')>"


class JustificationTemplate(Base):
    """Templates de justifications prédéfinies"""
    __tablename__ = "justification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations du template
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    justification_type = Column(String(20), nullable=False)

    # Template content
    title_template = Column(String(200), nullable=False)
    description_template = Column(Text, nullable=False)

    # Configuration
    default_priority = Column(String(10), default="medium")
    requires_documents = Column(Boolean, default=False)
    max_absence_days = Column(Integer, nullable=True)
    
    # Statut
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Visible par tous les étudiants
    
    # Audit
    created_by = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<JustificationTemplate(id={self.id}, name='{self.name}')>"


class JustificationNotification(Base):
    """Notifications liées aux justifications"""
    __tablename__ = "justification_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    justification_id = Column(Integer, ForeignKey("justifications.id"), nullable=False)
    
    # Destinataire
    recipient_id = Column(String(50), nullable=False)
    recipient_type = Column(String(20), nullable=False)  # student, parent, admin
    
    # Contenu de la notification
    notification_type = Column(String(50), nullable=False)  # submission, approval_request, etc.
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Canaux de notification
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    push_sent = Column(Boolean, default=False)
    push_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statut
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<JustificationNotification(id={self.id}, type='{self.notification_type}')>"
