"""
Modèles de données pour les cours et emplois du temps
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Time, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DayOfWeek(enum.Enum):
    """Jours de la semaine"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class CourseStatus(enum.Enum):
    """Statut des cours"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssignmentType(enum.Enum):
    """Type d'attribution"""
    TEACHER = "teacher"
    STUDENT = "student"


class Course(Base):
    """Modèle pour les cours"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text)
    subject = Column(String(100), nullable=False, index=True)
    level = Column(String(50), nullable=False)  # 6ème, 5ème, etc.
    credits = Column(Integer, default=1)
    max_students = Column(Integer, default=30)
    status = Column(Enum(CourseStatus), default=CourseStatus.ACTIVE)
    academic_year = Column(String(20), nullable=False, index=True)
    semester = Column(String(20), nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    schedules = relationship("Schedule", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("CourseAssignment", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', code='{self.code}')>"


class Schedule(Base):
    """Modèle pour les emplois du temps"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room = Column(String(50))
    building = Column(String(100))
    
    # Dates de validité
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    course = relationship("Course", back_populates="schedules")
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, course_id={self.course_id}, day={self.day_of_week}, time={self.start_time}-{self.end_time})>"


class CourseAssignment(Base):
    """Modèle pour l'attribution des cours aux enseignants et étudiants"""
    __tablename__ = "course_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user_id = Column(String(50), nullable=False, index=True)  # ID de l'utilisateur du user-service
    assignment_type = Column(Enum(AssignmentType), nullable=False)
    is_primary = Column(Boolean, default=False)  # Enseignant principal ou étudiant régulier
    
    # Dates d'attribution
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    course = relationship("Course", back_populates="assignments")
    
    def __repr__(self):
        return f"<CourseAssignment(id={self.id}, course_id={self.course_id}, user_id='{self.user_id}', type={self.assignment_type})>"
