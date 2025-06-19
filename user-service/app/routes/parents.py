"""
Routes API pour la gestion des parents et relations parent-élève
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..core.database import get_db
from ..core.auth import get_current_user, require_admin, require_teacher
from ..services.parent_service import ParentService
from ..services.student_service import StudentService
from ..schemas.user import (
    Parent, ParentCreate, ParentUpdate,
    ParentStudentRelation, ParentStudentRelationCreate,
    Student
)

router = APIRouter(prefix="/parents", tags=["parents"])


@router.post("/", response_model=Parent, status_code=status.HTTP_201_CREATED)
async def create_parent(
    parent_data: ParentCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Crée un nouveau parent (Admin seulement)"""
    service = ParentService(db)
    
    # Vérifier si le parent existe déjà
    if service.get_parent_by_user_id(parent_data.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un parent avec cet user_id existe déjà"
        )
    
    return service.create_parent(parent_data)


@router.get("/", response_model=List[Parent])
async def get_parents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_teacher)
):
    """Récupère la liste des parents (Teacher+ seulement)"""
    service = ParentService(db)
    return service.get_parents(skip=skip, limit=limit)


@router.get("/search", response_model=List[Parent])
async def search_parents(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_teacher)
):
    """Recherche des parents (Teacher+ seulement)"""
    service = ParentService(db)
    return service.search_parents(q, skip=skip, limit=limit)


@router.get("/{parent_id}", response_model=Parent)
async def get_parent(
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Récupère un parent par son ID"""
    service = ParentService(db)
    parent = service.get_parent(parent_id)
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent non trouvé"
        )
    
    # Vérifier les permissions
    user_role = current_user.get("role", "")
    if user_role in ["admin", "teacher"]:
        return parent
    elif user_role == "parent":
        # Un parent ne peut voir que ses propres informations
        if parent.user_id != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        return parent
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )


@router.put("/{parent_id}", response_model=Parent)
async def update_parent(
    parent_id: int,
    parent_data: ParentUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Met à jour un parent (Admin seulement)"""
    service = ParentService(db)
    parent = service.update_parent(parent_id, parent_data)
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent non trouvé"
        )
    
    return parent


@router.delete("/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parent(
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Supprime un parent (Admin seulement)"""
    service = ParentService(db)
    
    if not service.delete_parent(parent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent non trouvé"
        )


# Routes pour les relations parent-élève
@router.post("/{parent_id}/students/{student_id}", response_model=ParentStudentRelation, status_code=status.HTTP_201_CREATED)
async def create_parent_student_relation(
    parent_id: int,
    student_id: int,
    relationship_type: str = Query(..., description="Type de relation (père, mère, tuteur, etc.)"),
    is_primary_contact: bool = Query(False),
    is_emergency_contact: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Crée une relation parent-élève (Admin seulement)"""
    service = ParentService(db)
    student_service = StudentService(db)
    
    # Vérifier que le parent et l'élève existent
    if not service.get_parent(parent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent non trouvé"
        )
    
    if not student_service.get_student(student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )
    
    # Vérifier si la relation existe déjà
    if service.relation_exists(parent_id, student_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette relation parent-élève existe déjà"
        )
    
    relation_data = ParentStudentRelationCreate(
        parent_id=parent_id,
        student_id=student_id,
        relationship_type=relationship_type,
        is_primary_contact=is_primary_contact,
        is_emergency_contact=is_emergency_contact
    )
    
    return service.create_parent_student_relation(relation_data)


@router.get("/{parent_id}/students", response_model=List[Student])
async def get_parent_students(
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Récupère les étudiants d'un parent"""
    service = ParentService(db)
    student_service = StudentService(db)
    
    # Vérifier que le parent existe
    parent = service.get_parent(parent_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent non trouvé"
        )
    
    # Vérifier les permissions
    user_role = current_user.get("role", "")
    if user_role in ["admin", "teacher"]:
        pass  # Accès autorisé
    elif user_role == "parent":
        # Un parent ne peut voir que ses propres enfants
        if parent.user_id != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )
    
    return student_service.get_students_by_parent(parent_id)


@router.delete("/relations/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parent_student_relation(
    relation_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Supprime une relation parent-élève (Admin seulement)"""
    service = ParentService(db)
    
    if not service.delete_parent_student_relation(relation_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation non trouvée"
        )
