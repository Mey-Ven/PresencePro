"""
Service métier pour la gestion des emplois du temps
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date, time, datetime, timedelta
from app.models.course import Schedule, Course, DayOfWeek
from app.schemas.course import ScheduleCreate, ScheduleUpdate


class ScheduleService:
    """Service pour la gestion des emplois du temps"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_schedule(self, schedule_data: ScheduleCreate) -> Schedule:
        """Créer un nouveau créneau horaire"""
        # Vérifier que le cours existe
        course = self.db.query(Course).filter(Course.id == schedule_data.course_id).first()
        if not course:
            raise ValueError(f"Le cours avec l'ID {schedule_data.course_id} n'existe pas")
        
        # Vérifier les conflits d'horaires pour la même salle
        if schedule_data.room:
            conflict = self._check_room_conflict(
                schedule_data.day_of_week,
                schedule_data.start_time,
                schedule_data.end_time,
                schedule_data.room,
                schedule_data.start_date,
                schedule_data.end_date
            )
            if conflict:
                raise ValueError(f"Conflit d'horaire détecté avec le créneau ID {conflict.id} pour la salle {schedule_data.room}")
        
        schedule = Schedule(**schedule_data.model_dump())
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def get_schedule(self, schedule_id: int) -> Optional[Schedule]:
        """Récupérer un créneau horaire par son ID"""
        return self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    def get_schedules_by_course(self, course_id: int) -> List[Schedule]:
        """Récupérer tous les créneaux d'un cours"""
        return self.db.query(Schedule).filter(Schedule.course_id == course_id).all()
    
    def get_schedules_by_day(self, day: DayOfWeek, active_date: date = None) -> List[Schedule]:
        """Récupérer les créneaux d'un jour donné"""
        if active_date is None:
            active_date = date.today()
        
        return self.db.query(Schedule).filter(
            and_(
                Schedule.day_of_week == day,
                Schedule.start_date <= active_date,
                Schedule.end_date >= active_date
            )
        ).order_by(Schedule.start_time).all()
    
    def get_schedules_by_room(self, room: str, active_date: date = None) -> List[Schedule]:
        """Récupérer les créneaux d'une salle donnée"""
        if active_date is None:
            active_date = date.today()
        
        return self.db.query(Schedule).filter(
            and_(
                Schedule.room == room,
                Schedule.start_date <= active_date,
                Schedule.end_date >= active_date
            )
        ).order_by(Schedule.day_of_week, Schedule.start_time).all()
    
    def get_weekly_schedule(self, start_date: date = None) -> dict:
        """Récupérer l'emploi du temps de la semaine"""
        if start_date is None:
            start_date = date.today()
        
        # Calculer le début et la fin de la semaine
        days_since_monday = start_date.weekday()
        monday = start_date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        
        schedules = self.db.query(Schedule).filter(
            and_(
                Schedule.start_date <= sunday,
                Schedule.end_date >= monday
            )
        ).order_by(Schedule.day_of_week, Schedule.start_time).all()
        
        # Organiser par jour
        weekly_schedule = {day.value: [] for day in DayOfWeek}
        for schedule in schedules:
            weekly_schedule[schedule.day_of_week.value].append(schedule)
        
        return weekly_schedule
    
    def update_schedule(self, schedule_id: int, schedule_data: ScheduleUpdate) -> Optional[Schedule]:
        """Mettre à jour un créneau horaire"""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        update_data = schedule_data.model_dump(exclude_unset=True)
        
        # Vérifier les conflits si la salle, l'horaire ou les dates changent
        if any(key in update_data for key in ['room', 'day_of_week', 'start_time', 'end_time', 'start_date', 'end_date']):
            room = update_data.get('room', schedule.room)
            day = update_data.get('day_of_week', schedule.day_of_week)
            start_time = update_data.get('start_time', schedule.start_time)
            end_time = update_data.get('end_time', schedule.end_time)
            start_date = update_data.get('start_date', schedule.start_date)
            end_date = update_data.get('end_date', schedule.end_date)
            
            if room:
                conflict = self._check_room_conflict(
                    day, start_time, end_time, room, start_date, end_date, exclude_id=schedule_id
                )
                if conflict:
                    raise ValueError(f"Conflit d'horaire détecté avec le créneau ID {conflict.id} pour la salle {room}")
        
        for field, value in update_data.items():
            setattr(schedule, field, value)
        
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """Supprimer un créneau horaire"""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return False
        
        self.db.delete(schedule)
        self.db.commit()
        return True
    
    def get_teacher_schedule(self, teacher_id: str, week_start: date = None) -> dict:
        """Récupérer l'emploi du temps d'un enseignant"""
        from app.models.course import CourseAssignment, AssignmentType
        
        if week_start is None:
            week_start = date.today()
        
        # Calculer la fin de la semaine
        week_end = week_start + timedelta(days=6)
        
        # Récupérer les cours de l'enseignant
        teacher_courses = self.db.query(Course).join(CourseAssignment).filter(
            and_(
                CourseAssignment.user_id == teacher_id,
                CourseAssignment.assignment_type == AssignmentType.TEACHER,
                CourseAssignment.valid_from <= week_end,
                or_(
                    CourseAssignment.valid_to.is_(None),
                    CourseAssignment.valid_to >= week_start
                )
            )
        ).all()
        
        course_ids = [course.id for course in teacher_courses]
        
        # Récupérer les créneaux de ces cours
        schedules = self.db.query(Schedule).filter(
            and_(
                Schedule.course_id.in_(course_ids),
                Schedule.start_date <= week_end,
                Schedule.end_date >= week_start
            )
        ).order_by(Schedule.day_of_week, Schedule.start_time).all()
        
        # Organiser par jour
        weekly_schedule = {day.value: [] for day in DayOfWeek}
        for schedule in schedules:
            weekly_schedule[schedule.day_of_week.value].append(schedule)
        
        return weekly_schedule
    
    def _check_room_conflict(
        self,
        day: DayOfWeek,
        start_time: time,
        end_time: time,
        room: str,
        start_date: date,
        end_date: date,
        exclude_id: int = None
    ) -> Optional[Schedule]:
        """Vérifier les conflits d'horaires pour une salle"""
        query = self.db.query(Schedule).filter(
            and_(
                Schedule.room == room,
                Schedule.day_of_week == day,
                # Vérification du chevauchement des horaires
                or_(
                    and_(Schedule.start_time <= start_time, Schedule.end_time > start_time),
                    and_(Schedule.start_time < end_time, Schedule.end_time >= end_time),
                    and_(Schedule.start_time >= start_time, Schedule.end_time <= end_time)
                ),
                # Vérification du chevauchement des dates
                or_(
                    and_(Schedule.start_date <= start_date, Schedule.end_date >= start_date),
                    and_(Schedule.start_date <= end_date, Schedule.end_date >= end_date),
                    and_(Schedule.start_date >= start_date, Schedule.end_date <= end_date)
                )
            )
        )
        
        if exclude_id:
            query = query.filter(Schedule.id != exclude_id)
        
        return query.first()
