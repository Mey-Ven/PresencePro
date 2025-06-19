"""
Routes pour la gestion des emplois du temps
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.services.schedule_service import ScheduleService
from app.schemas.course import Schedule, ScheduleCreate, ScheduleUpdate
from app.models.course import DayOfWeek

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.post("/", response_model=Schedule, status_code=201)
def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """Créer un nouveau créneau horaire"""
    try:
        service = ScheduleService(db)
        return service.create_schedule(schedule_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/weekly")
def get_weekly_schedule(
    start_date: Optional[date] = Query(None, description="Date de début de semaine (défaut: cette semaine)"),
    db: Session = Depends(get_db)
):
    """Récupérer l'emploi du temps de la semaine"""
    service = ScheduleService(db)
    return service.get_weekly_schedule(start_date)


@router.get("/teacher/{teacher_id}/weekly")
def get_teacher_weekly_schedule(
    teacher_id: str,
    week_start: Optional[date] = Query(None, description="Date de début de semaine (défaut: cette semaine)"),
    db: Session = Depends(get_db)
):
    """Récupérer l'emploi du temps hebdomadaire d'un enseignant"""
    service = ScheduleService(db)
    return service.get_teacher_schedule(teacher_id, week_start)


@router.get("/course/{course_id}")
def get_course_schedules(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer tous les créneaux d'un cours"""
    service = ScheduleService(db)
    return service.get_schedules_by_course(course_id)


@router.get("/day/{day}")
def get_day_schedules(
    day: DayOfWeek,
    active_date: Optional[date] = Query(None, description="Date de référence (défaut: aujourd'hui)"),
    db: Session = Depends(get_db)
):
    """Récupérer les créneaux d'un jour donné"""
    service = ScheduleService(db)
    return service.get_schedules_by_day(day, active_date)


@router.get("/room/{room}")
def get_room_schedules(
    room: str,
    active_date: Optional[date] = Query(None, description="Date de référence (défaut: aujourd'hui)"),
    db: Session = Depends(get_db)
):
    """Récupérer les créneaux d'une salle donnée"""
    service = ScheduleService(db)
    return service.get_schedules_by_room(room, active_date)


@router.get("/{schedule_id}", response_model=Schedule)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer un créneau horaire par son ID"""
    service = ScheduleService(db)
    schedule = service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Créneau horaire non trouvé")
    return schedule


@router.put("/{schedule_id}", response_model=Schedule)
def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un créneau horaire"""
    try:
        service = ScheduleService(db)
        schedule = service.update_schedule(schedule_id, schedule_data)
        if not schedule:
            raise HTTPException(status_code=404, detail="Créneau horaire non trouvé")
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer un créneau horaire"""
    service = ScheduleService(db)
    if not service.delete_schedule(schedule_id):
        raise HTTPException(status_code=404, detail="Créneau horaire non trouvé")
