"""
Routes API pour la gestion des justifications
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.models.schemas import (
    JustificationCreate, JustificationUpdate, JustificationApproval,
    JustificationResponse, JustificationStatus, JustificationType,
    JustificationSearchFilters, StudentJustificationReport,
    JustificationDocumentResponse
)
from app.services.justification_service import JustificationService
from app.services.integration_service import IntegrationService
from app.services.file_service import FileService

router = APIRouter()


@router.post("/create", response_model=JustificationResponse)
async def create_justification(
    request: JustificationCreate,
    db: Session = Depends(get_db),
    current_user_id: str = "student_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Créer une nouvelle justification d'absence
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        
        # Valider la demande (désactivé pour les tests)
        # validation = await integration_service.validate_justification_request(
        #     current_user_id,
        #     request.course_id,
        #     request.attendance_id
        # )
        #
        # if not validation["valid"]:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"Demande invalide: {', '.join(validation['errors'])}"
        #     )
        
        # Créer la justification
        justification = justification_service.create_justification(
            request,
            current_user_id,
            current_user_id
        )
        
        return justification
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/{justification_id}/submit", response_model=JustificationResponse)
async def submit_justification(
    justification_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = "student_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Soumettre une justification pour approbation
    """
    try:
        justification_service = JustificationService(db)
        
        justification = justification_service.submit_justification(
            justification_id,
            current_user_id
        )
        
        return justification
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/{justification_id}/approve-parent", response_model=JustificationResponse)
async def approve_by_parent(
    justification_id: int,
    approval: JustificationApproval,
    db: Session = Depends(get_db),
    current_user_id: str = "parent_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Approbation parentale d'une justification
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        
        # Récupérer la justification pour vérifier la relation parent-étudiant
        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")
        
        # Vérifier la relation parent-étudiant
        is_parent = await integration_service.verify_parent_student_relationship(
            current_user_id,
            justification.student_id
        )
        
        if not is_parent:
            raise HTTPException(
                status_code=403,
                detail="Vous n'êtes pas autorisé à approuver cette justification"
            )
        
        # Approuver la justification
        result = justification_service.approve_by_parent(
            justification_id,
            approval,
            current_user_id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/{justification_id}/validate-admin", response_model=JustificationResponse)
async def validate_by_admin(
    justification_id: int,
    approval: JustificationApproval,
    db: Session = Depends(get_db),
    current_user_id: str = "admin_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Validation administrative d'une justification
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        
        # Vérifier que l'utilisateur est admin
        user_role = await integration_service.get_user_role(current_user_id)
        if user_role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=403,
                detail="Seuls les administrateurs peuvent valider les justifications"
            )
        
        # Valider la justification
        result = justification_service.validate_by_admin(
            justification_id,
            approval,
            current_user_id
        )
        
        # Notifier le service de présences si applicable
        if result.attendance_id:
            await integration_service.notify_attendance_service(
                justification_id,
                result.attendance_id,
                result.status.value
            )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/{justification_id}", response_model=JustificationResponse)
async def get_justification(
    justification_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = "user_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Récupérer une justification par ID
    """
    try:
        justification_service = JustificationService(db)
        
        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")
        
        # TODO: Vérifier les permissions d'accès
        
        return justification
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/student/{student_id}", response_model=List[JustificationResponse])
async def get_student_justifications(
    student_id: str,
    status: Optional[JustificationStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: str = "user_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Récupérer les justifications d'un étudiant
    """
    try:
        justification_service = JustificationService(db)
        
        # TODO: Vérifier les permissions d'accès
        
        justifications = justification_service.get_student_justifications(
            student_id,
            status,
            limit
        )
        
        return justifications
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/pending/approvals", response_model=List[JustificationResponse])
async def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user_id: str = "parent_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Récupérer les justifications en attente d'approbation parentale
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        
        # Vérifier que l'utilisateur est un parent
        user_role = await integration_service.get_user_role(current_user_id)
        if user_role != "parent":
            raise HTTPException(
                status_code=403,
                detail="Seuls les parents peuvent voir les approbations en attente"
            )
        
        justifications = justification_service.get_pending_approvals(current_user_id)
        
        return justifications
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/pending/validations", response_model=List[JustificationResponse])
async def get_pending_validations(
    db: Session = Depends(get_db),
    current_user_id: str = "admin_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Récupérer les justifications en attente de validation administrative
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        
        # Vérifier que l'utilisateur est admin
        user_role = await integration_service.get_user_role(current_user_id)
        if user_role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=403,
                detail="Seuls les administrateurs peuvent voir les validations en attente"
            )
        
        justifications = justification_service.get_pending_validations()
        
        return justifications
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.put("/{justification_id}", response_model=JustificationResponse)
async def update_justification(
    justification_id: int,
    update: JustificationUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = "student_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Mettre à jour une justification
    """
    try:
        justification_service = JustificationService(db)
        
        # Vérifier que la justification appartient à l'utilisateur
        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")
        
        if justification.student_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Vous ne pouvez modifier que vos propres justifications"
            )
        
        result = justification_service.update_justification(
            justification_id,
            update,
            current_user_id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/status/{justification_id}")
async def get_justification_status(
    justification_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = "user_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Récupérer le statut d'une justification
    """
    try:
        justification_service = JustificationService(db)

        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")

        # TODO: Vérifier les permissions d'accès

        return {
            "id": justification.id,
            "status": justification.status,
            "created_at": justification.created_at,
            "updated_at": justification.updated_at,
            "parent_approval_required": justification.parent_approval_required,
            "admin_validation_required": justification.admin_validation_required,
            "parent_approved_at": justification.parent_approved_at,
            "admin_validated_at": justification.admin_validated_at,
            "expires_at": justification.expires_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


# Routes pour la gestion des documents
@router.post("/{justification_id}/documents", response_model=JustificationDocumentResponse)
async def upload_document(
    justification_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db),
    current_user_id: str = "user_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Uploader un document pour une justification
    """
    try:
        file_service = FileService(db)
        justification_service = JustificationService(db)

        # Vérifier que la justification existe
        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")

        # TODO: Vérifier les permissions d'upload

        document = await file_service.upload_document(
            file,
            justification_id,
            current_user_id,
            description,
            is_primary
        )

        return document

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/{justification_id}/documents", response_model=List[JustificationDocumentResponse])
async def get_justification_documents(
    justification_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = "user_001"  # TODO: Récupérer depuis le token JWT
):
    """
    Récupérer les documents d'une justification
    """
    try:
        file_service = FileService(db)

        documents = await file_service.get_justification_documents(justification_id)

        return documents

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
