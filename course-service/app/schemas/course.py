"""
Schémas Pydantic pour les cours et emplois du temps
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime, date, time
from app.models.course import DayOfWeek, CourseStatus, AssignmentType


# Schémas de base pour Course
class CourseBase(BaseModel):
    """Schéma de base pour les cours"""
    name: str = Field(..., min_length=1, max_length=200, description="Nom du cours")
    code: str = Field(..., min_length=1, max_length=20, description="Code du cours")
    description: Optional[str] = Field(None, description="Description du cours")
    subject: str = Field(..., min_length=1, max_length=100, description="Matière")
    level: str = Field(..., min_length=1, max_length=50, description="Niveau (6ème, 5ème, etc.)")
    credits: int = Field(default=1, ge=1, le=10, description="Nombre de crédits")
    max_students: int = Field(default=30, ge=1, le=100, description="Nombre maximum d'étudiants")
    status: CourseStatus = Field(default=CourseStatus.ACTIVE, description="Statut du cours")
    academic_year: str = Field(..., min_length=1, max_length=20, description="Année académique")
    semester: str = Field(..., min_length=1, max_length=20, description="Semestre")


class CourseCreate(CourseBase):
    """Schéma pour la création d'un cours"""
    pass


class CourseUpdate(BaseModel):
    """Schéma pour la mise à jour d'un cours"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    level: Optional[str] = Field(None, min_length=1, max_length=50)
    credits: Optional[int] = Field(None, ge=1, le=10)
    max_students: Optional[int] = Field(None, ge=1, le=100)
    status: Optional[CourseStatus] = None
    academic_year: Optional[str] = Field(None, min_length=1, max_length=20)
    semester: Optional[str] = Field(None, min_length=1, max_length=20)


class Course(CourseBase):
    """Schéma complet pour les cours"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schémas de base pour Schedule
class ScheduleBase(BaseModel):
    """Schéma de base pour les emplois du temps"""
    day_of_week: DayOfWeek = Field(..., description="Jour de la semaine")
    start_time: time = Field(..., description="Heure de début")
    end_time: time = Field(..., description="Heure de fin")
    room: Optional[str] = Field(None, max_length=50, description="Salle")
    building: Optional[str] = Field(None, max_length=100, description="Bâtiment")
    start_date: date = Field(..., description="Date de début de validité")
    end_date: date = Field(..., description="Date de fin de validité")
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('L\'heure de fin doit être après l\'heure de début')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('La date de fin doit être après la date de début')
        return v


class ScheduleCreate(ScheduleBase):
    """Schéma pour la création d'un emploi du temps"""
    course_id: int = Field(..., description="ID du cours")


class ScheduleUpdate(BaseModel):
    """Schéma pour la mise à jour d'un emploi du temps"""
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    room: Optional[str] = Field(None, max_length=50)
    building: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class Schedule(ScheduleBase):
    """Schéma complet pour les emplois du temps"""
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schémas de base pour CourseAssignment
class CourseAssignmentBase(BaseModel):
    """Schéma de base pour l'attribution des cours"""
    user_id: str = Field(..., min_length=1, max_length=50, description="ID de l'utilisateur")
    assignment_type: AssignmentType = Field(..., description="Type d'attribution")
    is_primary: bool = Field(default=False, description="Attribution principale")
    valid_from: date = Field(..., description="Date de début de validité")
    valid_to: Optional[date] = Field(None, description="Date de fin de validité")
    
    @validator('valid_to')
    def validate_valid_to(cls, v, values):
        if v and 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('La date de fin doit être après la date de début')
        return v


class CourseAssignmentCreate(CourseAssignmentBase):
    """Schéma pour la création d'une attribution de cours"""
    course_id: int = Field(..., description="ID du cours")


class CourseAssignmentUpdate(BaseModel):
    """Schéma pour la mise à jour d'une attribution de cours"""
    is_primary: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class CourseAssignment(CourseAssignmentBase):
    """Schéma complet pour l'attribution des cours"""
    id: int
    course_id: int
    assigned_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schémas composés
class CourseWithSchedules(Course):
    """Cours avec ses emplois du temps"""
    schedules: List[Schedule] = []


class CourseWithAssignments(Course):
    """Cours avec ses attributions"""
    assignments: List[CourseAssignment] = []


class CourseComplete(Course):
    """Cours complet avec emplois du temps et attributions"""
    schedules: List[Schedule] = []
    assignments: List[CourseAssignment] = []


# Schémas pour les réponses d'API
class CourseList(BaseModel):
    """Liste paginée de cours"""
    courses: List[Course]
    total: int
    page: int
    size: int
    pages: int


class AssignmentRequest(BaseModel):
    """Requête d'attribution multiple"""
    course_id: int = Field(..., description="ID du cours")
    assignments: List[CourseAssignmentCreate] = Field(..., description="Liste des attributions")


# Schémas pour les statistiques
class CourseStats(BaseModel):
    """Statistiques d'un cours"""
    course_id: int
    total_students: int
    total_teachers: int
    total_schedules: int
    next_class: Optional[datetime] = None
