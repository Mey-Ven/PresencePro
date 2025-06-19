"""
Routes API pour la gestion des étudiants
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..core.database import get_db
from ..core.auth import get_current_user, require_admin, require_teacher
from ..services.student_service import StudentService
from ..schemas.user import Student, StudentCreate, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Crée un nouvel étudiant (Admin seulement)"""
    service = StudentService(db)
    
    # Vérifier si l'étudiant existe déjà
    if service.get_student_by_user_id(student_data.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un étudiant avec cet user_id existe déjà"
        )
    
    if service.get_student_by_number(student_data.student_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un étudiant avec ce numéro existe déjà"
        )
    
    return service.create_student(student_data)


@router.get("/", response_model=List[Student])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    class_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_teacher)
):
    """Récupère la liste des étudiants (Teacher+ seulement)"""
    service = StudentService(db)
    return service.get_students(skip=skip, limit=limit, class_name=class_name)


@router.get("/search", response_model=List[Student])
async def search_students(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_teacher)
):
    """Recherche des étudiants (Teacher+ seulement)"""
    service = StudentService(db)
    return service.search_students(q, skip=skip, limit=limit)


@router.get("/{student_id}", response_model=Student)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Récupère un étudiant par son ID"""
    service = StudentService(db)
    student = service.get_student(student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )
    
    # Vérifier les permissions
    user_role = current_user.get("role", "")
    if user_role in ["admin", "teacher"]:
        return student
    elif user_role == "parent":
        # Un parent ne peut voir que ses propres enfants
        parent_students = service.get_students_by_parent(current_user.get("id"))
        if student not in parent_students:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        return student
    elif user_role == "student":
        # Un étudiant ne peut voir que ses propres informations
        if student.user_id != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        return student
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )


@router.put("/{student_id}", response_model=Student)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Met à jour un étudiant (Admin seulement)"""
    service = StudentService(db)
    student = service.update_student(student_id, student_data)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )
    
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Supprime un étudiant (Admin seulement)"""
    service = StudentService(db)
    
    if not service.delete_student(student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )
