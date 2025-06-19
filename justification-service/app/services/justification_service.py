"""
Service principal de gestion des justifications
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
import logging
from dateutil import tz

from app.models.justification import (
    Justification, JustificationDocument, JustificationHistory,
    JustificationStatus, JustificationType, JustificationPriority
)
from app.models.schemas import (
    JustificationCreate, JustificationUpdate, JustificationApproval,
    JustificationResponse, JustificationStats, StudentJustificationReport
)
from app.core.config import settings


class JustificationService:
    """Service de gestion des justifications"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.timezone = tz.gettz(settings.default_timezone)
    
    def create_justification(
        self, 
        request: JustificationCreate, 
        student_id: str,
        created_by: str = None
    ) -> JustificationResponse:
        """Créer une nouvelle justification"""
        try:
            # Calculer les dates importantes
            submission_deadline = datetime.now() + timedelta(days=settings.max_justification_days)
            expires_at = datetime.now() + timedelta(days=settings.auto_expire_days)
            
            # Créer la justification
            justification = Justification(
                student_id=student_id,
                course_id=request.course_id,
                attendance_id=request.attendance_id,
                title=request.title,
                description=request.description,
                justification_type=request.justification_type.value if hasattr(request.justification_type, 'value') else request.justification_type,
                priority=request.priority.value if hasattr(request.priority, 'value') else request.priority,
                absence_start_date=request.absence_start_date,
                absence_end_date=request.absence_end_date,
                notes=request.notes,
                status="draft",
                parent_approval_required=settings.require_parent_approval,
                admin_validation_required=settings.require_admin_validation,
                submission_deadline=submission_deadline,
                expires_at=expires_at,
                created_by=created_by or student_id
            )
            
            self.db.add(justification)
            self.db.commit()
            self.db.refresh(justification)
            
            # Ajouter à l'historique
            self._add_history(
                justification.id,
                "created",
                None,
                "draft",
                "Justification créée",
                created_by or student_id
            )
            
            self.logger.info(f"Justification créée: {justification.id} par {student_id}")
            return JustificationResponse.from_orm(justification)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur création justification: {e}")
            raise
    
    def submit_justification(self, justification_id: int, submitted_by: str) -> JustificationResponse:
        """Soumettre une justification pour approbation"""
        try:
            justification = self.db.query(Justification).filter(
                Justification.id == justification_id
            ).first()
            
            if not justification:
                raise ValueError(f"Justification {justification_id} non trouvée")
            
            if justification.status != "draft":
                raise ValueError(f"Justification déjà soumise (statut: {justification.status})")

            # Vérifier les permissions
            if justification.student_id != submitted_by:
                raise ValueError("Seul l'étudiant peut soumettre sa justification")

            # Déterminer le prochain statut
            if justification.parent_approval_required:
                new_status = "parent_pending"
            elif justification.admin_validation_required:
                new_status = "admin_pending"
            else:
                new_status = "admin_approved"
            
            # Mettre à jour le statut
            old_status = justification.status
            justification.status = new_status
            justification.updated_by = submitted_by
            justification.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(justification)
            
            # Ajouter à l'historique
            self._add_history(
                justification.id,
                "submitted",
                old_status,
                new_status,
                "Justification soumise pour approbation",
                submitted_by
            )
            
            self.logger.info(f"Justification {justification_id} soumise par {submitted_by}")
            return JustificationResponse.from_orm(justification)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur soumission justification: {e}")
            raise
    
    def approve_by_parent(
        self, 
        justification_id: int, 
        approval: JustificationApproval,
        parent_id: str
    ) -> JustificationResponse:
        """Approbation parentale d'une justification"""
        try:
            justification = self.db.query(Justification).filter(
                Justification.id == justification_id
            ).first()
            
            if not justification:
                raise ValueError(f"Justification {justification_id} non trouvée")
            
            if justification.status != "parent_pending":
                raise ValueError(f"Justification non en attente d'approbation parentale")

            # TODO: Vérifier que parent_id est bien le parent de l'étudiant

            old_status = justification.status

            if approval.approved:
                # Approbation
                justification.status = (
                    "admin_pending"
                    if justification.admin_validation_required
                    else "admin_approved"
                )
                justification.parent_approved_by = parent_id
                justification.parent_approved_at = datetime.now()
                action = "parent_approved"
                comment = approval.comment or "Approuvé par les parents"
            else:
                # Rejet
                justification.status = "parent_rejected"
                justification.parent_rejection_reason = approval.comment
                action = "parent_rejected"
                comment = approval.comment or "Rejeté par les parents"
            
            justification.updated_by = parent_id
            justification.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(justification)
            
            # Ajouter à l'historique
            self._add_history(
                justification.id,
                action,
                old_status,
                justification.status,
                comment,
                parent_id
            )
            
            self.logger.info(f"Justification {justification_id} {'approuvée' if approval.approved else 'rejetée'} par parent {parent_id}")
            return JustificationResponse.from_orm(justification)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur approbation parentale: {e}")
            raise
    
    def validate_by_admin(
        self, 
        justification_id: int, 
        approval: JustificationApproval,
        admin_id: str
    ) -> JustificationResponse:
        """Validation administrative d'une justification"""
        try:
            justification = self.db.query(Justification).filter(
                Justification.id == justification_id
            ).first()
            
            if not justification:
                raise ValueError(f"Justification {justification_id} non trouvée")
            
            if justification.status not in ["admin_pending", "parent_approved"]:
                raise ValueError(f"Justification non en attente de validation administrative")

            old_status = justification.status

            if approval.approved:
                # Validation
                justification.status = "admin_approved"
                justification.admin_validated_by = admin_id
                justification.admin_validated_at = datetime.now()
                action = "admin_approved"
                comment = approval.comment or "Validé par l'administration"
            else:
                # Rejet
                justification.status = "admin_rejected"
                justification.admin_rejection_reason = approval.comment
                action = "admin_rejected"
                comment = approval.comment or "Rejeté par l'administration"
            
            if approval.internal_notes:
                justification.internal_notes = approval.internal_notes
            
            justification.updated_by = admin_id
            justification.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(justification)
            
            # Ajouter à l'historique
            self._add_history(
                justification.id,
                action,
                old_status,
                justification.status,
                comment,
                admin_id
            )
            
            self.logger.info(f"Justification {justification_id} {'validée' if approval.approved else 'rejetée'} par admin {admin_id}")
            return JustificationResponse.from_orm(justification)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur validation administrative: {e}")
            raise
    
    def get_justification(self, justification_id: int) -> Optional[JustificationResponse]:
        """Récupérer une justification par ID"""
        try:
            justification = self.db.query(Justification).filter(
                Justification.id == justification_id
            ).first()
            
            if justification:
                return JustificationResponse.from_orm(justification)
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur récupération justification: {e}")
            raise
    
    def get_student_justifications(
        self,
        student_id: str,
        status: Optional[JustificationStatus] = None,
        limit: int = 50
    ) -> List[JustificationResponse]:
        """Récupérer les justifications d'un étudiant"""
        try:
            query = self.db.query(Justification).filter(
                Justification.student_id == student_id
            )
            
            if status:
                query = query.filter(Justification.status == status)
            
            justifications = query.order_by(desc(Justification.created_at)).limit(limit).all()
            
            return [JustificationResponse.from_orm(j) for j in justifications]
            
        except Exception as e:
            self.logger.error(f"Erreur récupération justifications étudiant: {e}")
            raise
    
    def get_pending_approvals(self, parent_id: str) -> List[JustificationResponse]:
        """Récupérer les justifications en attente d'approbation parentale"""
        try:
            # TODO: Filtrer par les enfants du parent
            justifications = self.db.query(Justification).filter(
                Justification.status == "parent_pending"
            ).order_by(desc(Justification.created_at)).all()
            
            return [JustificationResponse.from_orm(j) for j in justifications]
            
        except Exception as e:
            self.logger.error(f"Erreur récupération approbations en attente: {e}")
            raise
    
    def get_pending_validations(self) -> List[JustificationResponse]:
        """Récupérer les justifications en attente de validation administrative"""
        try:
            justifications = self.db.query(Justification).filter(
                Justification.status == "admin_pending"
            ).order_by(desc(Justification.created_at)).all()
            
            return [JustificationResponse.from_orm(j) for j in justifications]
            
        except Exception as e:
            self.logger.error(f"Erreur récupération validations en attente: {e}")
            raise
    
    def update_justification(
        self, 
        justification_id: int, 
        update: JustificationUpdate,
        updated_by: str
    ) -> JustificationResponse:
        """Mettre à jour une justification"""
        try:
            justification = self.db.query(Justification).filter(
                Justification.id == justification_id
            ).first()
            
            if not justification:
                raise ValueError(f"Justification {justification_id} non trouvée")
            
            if justification.status != "draft":
                raise ValueError("Seules les justifications en brouillon peuvent être modifiées")
            
            # Mettre à jour les champs fournis
            update_data = update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(justification, field, value)
            
            justification.updated_by = updated_by
            justification.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(justification)
            
            # Ajouter à l'historique
            self._add_history(
                justification.id,
                "updated",
                None,
                None,
                f"Justification modifiée: {', '.join(update_data.keys())}",
                updated_by
            )
            
            return JustificationResponse.from_orm(justification)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur mise à jour justification: {e}")
            raise
    
    def _add_history(
        self,
        justification_id: int,
        action: str,
        old_status: Optional[str],
        new_status: Optional[str],
        comment: str,
        changed_by: str
    ):
        """Ajouter une entrée à l'historique"""
        try:
            history = JustificationHistory(
                justification_id=justification_id,
                action=action,
                old_status=old_status,
                new_status=new_status,
                comment=comment,
                changed_by=changed_by
            )
            
            self.db.add(history)
            self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Erreur ajout historique: {e}")
            # Ne pas faire échouer l'opération principale
