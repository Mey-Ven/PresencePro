"""
Routes API pour la gestion des enseignants
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..core.database import get_db
from ..core.auth import get_current_user, require_admin, require_teacher
from ..services.teacher_service import TeacherService
from ..schemas.user import Teacher, TeacherCreate, TeacherUpdate

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.post("/", response_model=Teacher, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Crée un nouvel enseignant (Admin seulement)"""
    service = TeacherService(db)
    
    # Vérifier si l'enseignant existe déjà
    if service.get_teacher_by_user_id(teacher_data.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un enseignant avec cet user_id existe déjà"
        )
    
    if service.get_teacher_by_employee_number(teacher_data.employee_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un enseignant avec ce numéro d'employé existe déjà"
        )
    
    return service.create_teacher(teacher_data)


@router.get("/", response_model=List[Teacher])
async def get_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_teacher)
):
    """Récupère la liste des enseignants (Teacher+ seulement)"""
    service = TeacherService(db)
    return service.get_teachers(skip=skip, limit=limit, department=department)


@router.get("/search", response_model=List[Teacher])
async def search_teachers(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_teacher)
):
    """Recherche des enseignants (Teacher+ seulement)"""
    service = TeacherService(db)
    return service.search_teachers(q, skip=skip, limit=limit)


@router.get("/by-department/{department}", response_model=List[Teacher])
async def get_teachers_by_department(
    department: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_teacher)
):
    """Récupère les enseignants d'un département (Teacher+ seulement)"""
    service = TeacherService(db)
    return service.get_teachers_by_department(department)


@router.get("/by-subject/{subject}", response_model=List[Teacher])
async def get_teachers_by_subject(
    subject: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_teacher)
):
    """Récupère les enseignants d'une matière (Teacher+ seulement)"""
    service = TeacherService(db)
    return service.get_teachers_by_subject(subject)


@router.get("/{teacher_id}", response_model=Teacher)
async def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Récupère un enseignant par son ID"""
    service = TeacherService(db)
    teacher = service.get_teacher(teacher_id)
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enseignant non trouvé"
        )
    
    # Vérifier les permissions
    user_role = current_user.get("role", "")
    if user_role in ["admin", "teacher"]:
        return teacher
    elif user_role == "teacher":
        # Un enseignant ne peut voir que ses propres informations
        if teacher.user_id != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        return teacher
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )


@router.put("/{teacher_id}", response_model=Teacher)
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Met à jour un enseignant (Admin seulement)"""
    service = TeacherService(db)
    teacher = service.update_teacher(teacher_id, teacher_data)
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enseignant non trouvé"
        )
    
    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Supprime un enseignant (Admin seulement)"""
    service = TeacherService(db)
    
    if not service.delete_teacher(teacher_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enseignant non trouvé"
        )
