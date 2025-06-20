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
from app.core.auth import get_current_user # Assumed location

router = APIRouter()


@router.post("/create", response_model=JustificationResponse)
async def create_justification(
    request: JustificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Créer une nouvelle justification d'absence
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        current_user_id = current_user["id"]

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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Soumettre une justification pour approbation
    """
    try:
        justification_service = JustificationService(db)
        current_user_id = current_user["id"]
        
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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Approbation parentale d'une justification
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        current_user_id = current_user["id"]
        
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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Validation administrative d'une justification
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        current_user_id = current_user["id"]
        user_role = current_user["role"] # Supposant que le rôle est dans le token
        
        # Vérifier que l'utilisateur est admin
        if user_role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=403,
                detail="Seuls les administrateurs ou enseignants peuvent valider les justifications"
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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Récupérer une justification par ID
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        current_user_id = current_user["id"]
        user_role = current_user["role"]

        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")
        
        # Vérifier les permissions d'accès
        if user_role == "student" and justification.student_id != current_user_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        if user_role == "parent":
            is_parent = await integration_service.verify_parent_student_relationship(current_user_id, justification.student_id)
            if not is_parent:
                raise HTTPException(status_code=403, detail="Accès non autorisé")

        # Les admins et enseignants ont accès
        if user_role not in ["admin", "teacher", "student", "parent"]:
             raise HTTPException(status_code=403, detail="Rôle utilisateur inconnu ou non autorisé")

        return justification
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/student/{student_id}", response_model=List[JustificationResponse])
async def get_student_justifications(
    student_id: str,
    status: Optional[JustificationStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Récupérer les justifications d'un étudiant
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        current_user_id = current_user["id"]
        user_role = current_user["role"]
        
        # Vérifier les permissions d'accès
        if user_role == "student" and student_id != current_user_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")

        if user_role == "parent":
            is_parent = await integration_service.verify_parent_student_relationship(current_user_id, student_id)
            if not is_parent:
                raise HTTPException(status_code=403, detail="Accès non autorisé")

        # Les admins et enseignants ont accès
        if user_role not in ["admin", "teacher", "student", "parent"]:
             raise HTTPException(status_code=403, detail="Rôle utilisateur inconnu ou non autorisé")
        
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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Récupérer les justifications en attente d'approbation parentale
    """
    try:
        justification_service = JustificationService(db)
        current_user_id = current_user["id"]
        user_role = current_user["role"]
        
        # Vérifier que l'utilisateur est un parent
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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Récupérer les justifications en attente de validation administrative
    """
    try:
        justification_service = JustificationService(db)
        user_role = current_user["role"]
        
        # Vérifier que l'utilisateur est admin ou enseignant
        if user_role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=403,
                detail="Seuls les administrateurs ou enseignants peuvent voir les validations en attente"
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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Mettre à jour une justification
    """
    try:
        justification_service = JustificationService(db)
        current_user_id = current_user["id"]
        user_role = current_user["role"]
        
        # Vérifier que la justification appartient à l'utilisateur ou que l'utilisateur est admin/enseignant
        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")
        
        if user_role == "student" and justification.student_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Vous ne pouvez modifier que vos propres justifications"
            )
        elif user_role not in ["admin", "teacher", "student"]:
             raise HTTPException(status_code=403, detail="Accès non autorisé pour modifier cette justification")

        result = justification_service.update_justification(
            justification_id,
            update,
            current_user_id # L'auteur de la modification est toujours l'utilisateur actuel
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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Récupérer le statut d'une justification
    """
    try:
        justification_service = JustificationService(db)
        integration_service = IntegrationService()
        current_user_id = current_user["id"]
        user_role = current_user["role"]

        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")

        # Vérifier les permissions d'accès
        if user_role == "student" and justification.student_id != current_user_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")

        if user_role == "parent":
            is_parent = await integration_service.verify_parent_student_relationship(current_user_id, justification.student_id)
            if not is_parent:
                raise HTTPException(status_code=403, detail="Accès non autorisé")

        # Les admins et enseignants ont accès
        if user_role not in ["admin", "teacher", "student", "parent"]:
             raise HTTPException(status_code=403, detail="Rôle utilisateur inconnu ou non autorisé")

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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Uploader un document pour une justification
    """
    try:
        file_service = FileService(db)
        justification_service = JustificationService(db)
        current_user_id = current_user["id"]
        user_role = current_user["role"]

        # Vérifier que la justification existe
        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")

        # Vérifier les permissions d'upload
        # Seul l'étudiant concerné ou un admin/enseignant peut uploader des documents
        if user_role == "student" and justification.student_id != current_user_id:
            raise HTTPException(status_code=403, detail="Vous ne pouvez uploader des documents que pour vos propres justifications.")
        elif user_role not in ["admin", "teacher", "student"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé pour uploader des documents.")

        document = await file_service.upload_document(
            file,
            justification_id,
            current_user_id, # L'uploader est l'utilisateur actuel
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
    current_user: dict = Depends(get_current_user)  # Remplacer par la dépendance d'authentification
):
    """
    Récupérer les documents d'une justification
    """
    try:
        file_service = FileService(db)
        justification_service = JustificationService(db) # Ajout pour récupérer la justification
        integration_service = IntegrationService()
        current_user_id = current_user["id"]
        user_role = current_user["role"]

        # Vérifier que la justification existe pour vérifier les droits ensuite
        justification = justification_service.get_justification(justification_id)
        if not justification:
            raise HTTPException(status_code=404, detail="Justification non trouvée")

        # Vérifier les permissions d'accès aux documents
        if user_role == "student" and justification.student_id != current_user_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé aux documents de cette justification.")

        if user_role == "parent":
            is_parent = await integration_service.verify_parent_student_relationship(current_user_id, justification.student_id)
            if not is_parent:
                raise HTTPException(status_code=403, detail="Accès non autorisé aux documents de cette justification.")

        # Les admins et enseignants ont accès
        if user_role not in ["admin", "teacher", "student", "parent"]:
             raise HTTPException(status_code=403, detail="Rôle utilisateur inconnu ou non autorisé à voir les documents.")

        documents = await file_service.get_justification_documents(justification_id)

        return documents

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
