"""
Routes pour la gestion des cours
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.core.database import get_db
# from app.core.auth import require_admin, require_teacher, require_student, get_user_id
from app.services.course_service import CourseService
from app.schemas.course import (
    Course, CourseCreate, CourseUpdate, CourseList, CourseStats,
    CourseWithSchedules, CourseWithAssignments, CourseComplete
)
from app.models.course import CourseStatus

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=Course, status_code=201)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db)
    # current_user: dict = Depends(require_admin())
):
    """Créer un nouveau cours"""
    try:
        service = CourseService(db)
        return service.create_course(course_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=CourseList)
def get_courses(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=100, description="Taille de la page"),
    subject: Optional[str] = Query(None, description="Filtrer par matière"),
    level: Optional[str] = Query(None, description="Filtrer par niveau"),
    academic_year: Optional[str] = Query(None, description="Filtrer par année académique"),
    semester: Optional[str] = Query(None, description="Filtrer par semestre"),
    status: Optional[CourseStatus] = Query(None, description="Filtrer par statut"),
    db: Session = Depends(get_db)
    # current_user: dict = Depends(require_student())
):
    """Récupérer la liste des cours avec pagination et filtres"""
    service = CourseService(db)
    
    skip = (page - 1) * size
    courses = service.get_courses(
        skip=skip,
        limit=size,
        subject=subject,
        level=level,
        academic_year=academic_year,
        semester=semester,
        status=status
    )
    
    total = service.count_courses(
        subject=subject,
        level=level,
        academic_year=academic_year,
        semester=semester,
        status=status
    )
    
    pages = (total + size - 1) // size
    
    return CourseList(
        courses=courses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/search")
def search_courses(
    q: str = Query(..., min_length=1, description="Terme de recherche"),
    limit: int = Query(20, ge=1, le=50, description="Nombre maximum de résultats"),
    db: Session = Depends(get_db)
    # current_user: dict = Depends(require_student())
):
    """Rechercher des cours par nom, code ou description"""
    service = CourseService(db)
    return service.search_courses(q, limit)


@router.get("/{course_id}", response_model=Course)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
    # current_user: dict = Depends(require_student())
):
    """Récupérer un cours par son ID"""
    service = CourseService(db)
    course = service.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    return course


@router.get("/{course_id}/complete", response_model=CourseComplete)
def get_course_complete(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer un cours avec ses emplois du temps et attributions"""
    service = CourseService(db)
    course = service.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    return course


@router.get("/{course_id}/stats", response_model=CourseStats)
def get_course_stats(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer les statistiques d'un cours"""
    service = CourseService(db)
    stats = service.get_course_stats(course_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    return stats


@router.put("/{course_id}", response_model=Course)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db)
    # current_user: dict = Depends(require_admin())
):
    """Mettre à jour un cours"""
    service = CourseService(db)
    course = service.update_course(course_id, course_data)
    if not course:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    return course


@router.delete("/{course_id}", status_code=204)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db)
    # current_user: dict = Depends(require_admin())
):
    """Supprimer un cours"""
    service = CourseService(db)
    if not service.delete_course(course_id):
        raise HTTPException(status_code=404, detail="Cours non trouvé")


@router.get("/teacher/{teacher_id}")
def get_teacher_courses(
    teacher_id: str,
    db: Session = Depends(get_db)
):
    """Récupérer les cours d'un enseignant"""
    service = CourseService(db)
    return service.get_courses_by_teacher(teacher_id)


@router.get("/student/{student_id}")
def get_student_courses(
    student_id: str,
    db: Session = Depends(get_db)
):
    """Récupérer les cours d'un étudiant"""
    service = CourseService(db)
    return service.get_courses_by_student(student_id)
