"""
Routes pour la gestion des attributions de cours
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.assignment_service import AssignmentService
from app.schemas.course import (
    CourseAssignment, CourseAssignmentCreate, CourseAssignmentUpdate, AssignmentRequest
)

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/", response_model=CourseAssignment, status_code=201)
def create_assignment(
    assignment_data: CourseAssignmentCreate,
    db: Session = Depends(get_db)
):
    """Créer une nouvelle attribution de cours"""
    try:
        service = AssignmentService(db)
        return service.create_assignment(assignment_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/multiple", response_model=List[CourseAssignment], status_code=201)
def create_multiple_assignments(
    request: AssignmentRequest,
    db: Session = Depends(get_db)
):
    """Assigner plusieurs utilisateurs à un cours"""
    try:
        service = AssignmentService(db)
        return service.assign_multiple_users(request.course_id, request.assignments)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{assignment_id}", response_model=CourseAssignment)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer une attribution par son ID"""
    service = AssignmentService(db)
    assignment = service.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Attribution non trouvée")
    return assignment


@router.get("/course/{course_id}")
def get_course_assignments(
    course_id: int,
    active_only: bool = Query(True, description="Afficher seulement les attributions actives"),
    db: Session = Depends(get_db)
):
    """Récupérer toutes les attributions d'un cours"""
    service = AssignmentService(db)
    return service.get_assignments_by_course(course_id, active_only)


@router.get("/course/{course_id}/teachers")
def get_course_teachers(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer les enseignants d'un cours"""
    service = AssignmentService(db)
    return service.get_teachers_by_course(course_id)


@router.get("/course/{course_id}/students")
def get_course_students(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer les étudiants d'un cours"""
    service = AssignmentService(db)
    return service.get_students_by_course(course_id)


@router.get("/user/{user_id}")
def get_user_assignments(
    user_id: str,
    active_only: bool = Query(True, description="Afficher seulement les attributions actives"),
    db: Session = Depends(get_db)
):
    """Récupérer toutes les attributions d'un utilisateur"""
    service = AssignmentService(db)
    return service.get_assignments_by_user(user_id, active_only)


@router.put("/{assignment_id}", response_model=CourseAssignment)
def update_assignment(
    assignment_id: int,
    assignment_data: CourseAssignmentUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une attribution"""
    try:
        service = AssignmentService(db)
        assignment = service.update_assignment(assignment_id, assignment_data)
        if not assignment:
            raise HTTPException(status_code=404, detail="Attribution non trouvée")
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{assignment_id}", status_code=204)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer une attribution"""
    service = AssignmentService(db)
    if not service.delete_assignment(assignment_id):
        raise HTTPException(status_code=404, detail="Attribution non trouvée")


@router.delete("/course/{course_id}/user/{user_id}", status_code=204)
def remove_user_from_course(
    course_id: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Retirer un utilisateur d'un cours"""
    service = AssignmentService(db)
    if not service.remove_user_from_course(course_id, user_id):
        raise HTTPException(status_code=404, detail="Attribution non trouvée")
