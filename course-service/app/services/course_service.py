"""
Service métier pour la gestion des cours
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date, datetime, timedelta # Added timedelta
from app.models.course import Course, CourseStatus, Schedule
from app.schemas.course import CourseCreate, CourseUpdate, CourseStats
import logging

logger = logging.getLogger(__name__)

# Placeholder function - needs proper implementation
def calculate_next_class_datetime(course_id: int, db: Session) -> Optional[datetime]:
    """Calcule la date et l'heure du prochain cours programmé. À IMPLÉMENTER."""
    # from sqlalchemy import and_
    # now = datetime.now()
    # next_schedule_entry = db.query(Schedule).filter(
    #     and_(
    #         Schedule.course_id == course_id,
    #         Schedule.start_time > now # Assumant que Schedule a start_time et potentiellement une date
    #         # Il faudrait peut-être combiner Schedule.date et Schedule.start_time si ce sont des champs séparés
    #         # ou si Schedule.start_time est un DATETIME complet.
    #     )
    # ).order_by(Schedule.start_time.asc()).first()
    #
    # if next_schedule_entry:
    #     return next_schedule_entry.start_time # ou la combinaison de date et heure

    logger.info(f"calculate_next_class_datetime pour course {course_id} (simulation).")
    # Simuler un prochain cours dans 2 jours à 10h
    return datetime.now() + timedelta(days=2, hours=10)


class CourseService:
    """Service pour la gestion des cours"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_course(self, course_data: CourseCreate) -> Course:
        """Créer un nouveau cours"""
        # Vérifier l'unicité du code
        existing_course = self.db.query(Course).filter(Course.code == course_data.code).first()
        if existing_course:
            raise ValueError(f"Un cours avec le code '{course_data.code}' existe déjà")
        
        course = Course(**course_data.model_dump())
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course
    
    def get_course(self, course_id: int) -> Optional[Course]:
        """Récupérer un cours par son ID"""
        return self.db.query(Course).filter(Course.id == course_id).first()
    
    def get_course_by_code(self, code: str) -> Optional[Course]:
        """Récupérer un cours par son code"""
        return self.db.query(Course).filter(Course.code == code).first()
    
    def get_courses(
        self,
        skip: int = 0,
        limit: int = 100,
        subject: Optional[str] = None,
        level: Optional[str] = None,
        academic_year: Optional[str] = None,
        semester: Optional[str] = None,
        status: Optional[CourseStatus] = None
    ) -> List[Course]:
        """Récupérer une liste de cours avec filtres"""
        query = self.db.query(Course)
        
        if subject:
            query = query.filter(Course.subject.ilike(f"%{subject}%"))
        if level:
            query = query.filter(Course.level == level)
        if academic_year:
            query = query.filter(Course.academic_year == academic_year)
        if semester:
            query = query.filter(Course.semester == semester)
        if status:
            query = query.filter(Course.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def count_courses(
        self,
        subject: Optional[str] = None,
        level: Optional[str] = None,
        academic_year: Optional[str] = None,
        semester: Optional[str] = None,
        status: Optional[CourseStatus] = None
    ) -> int:
        """Compter le nombre de cours avec filtres"""
        query = self.db.query(Course)
        
        if subject:
            query = query.filter(Course.subject.ilike(f"%{subject}%"))
        if level:
            query = query.filter(Course.level == level)
        if academic_year:
            query = query.filter(Course.academic_year == academic_year)
        if semester:
            query = query.filter(Course.semester == semester)
        if status:
            query = query.filter(Course.status == status)
        
        return query.count()
    
    def update_course(self, course_id: int, course_data: CourseUpdate) -> Optional[Course]:
        """Mettre à jour un cours"""
        course = self.get_course(course_id)
        if not course:
            return None
        
        update_data = course_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)
        
        self.db.commit()
        self.db.refresh(course)
        return course
    
    def delete_course(self, course_id: int) -> bool:
        """Supprimer un cours"""
        course = self.get_course(course_id)
        if not course:
            return False
        
        self.db.delete(course)
        self.db.commit()
        return True
    
    def search_courses(self, query: str, limit: int = 20) -> List[Course]:
        """Rechercher des cours par nom, code ou description"""
        search_filter = or_(
            Course.name.ilike(f"%{query}%"),
            Course.code.ilike(f"%{query}%"),
            Course.description.ilike(f"%{query}%"),
            Course.subject.ilike(f"%{query}%")
        )
        
        return self.db.query(Course).filter(search_filter).limit(limit).all()
    
    def get_courses_by_teacher(self, teacher_id: str) -> List[Course]:
        """Récupérer les cours d'un enseignant"""
        from app.models.course import CourseAssignment, AssignmentType
        
        return self.db.query(Course).join(CourseAssignment).filter(
            and_(
                CourseAssignment.user_id == teacher_id,
                CourseAssignment.assignment_type == AssignmentType.TEACHER,
                CourseAssignment.valid_from <= date.today(),
                or_(
                    CourseAssignment.valid_to.is_(None),
                    CourseAssignment.valid_to >= date.today()
                )
            )
        ).all()
    
    def get_courses_by_student(self, student_id: str) -> List[Course]:
        """Récupérer les cours d'un étudiant"""
        from app.models.course import CourseAssignment, AssignmentType
        
        return self.db.query(Course).join(CourseAssignment).filter(
            and_(
                CourseAssignment.user_id == student_id,
                CourseAssignment.assignment_type == AssignmentType.STUDENT,
                CourseAssignment.valid_from <= date.today(),
                or_(
                    CourseAssignment.valid_to.is_(None),
                    CourseAssignment.valid_to >= date.today()
                )
            )
        ).all()
    
    def get_course_stats(self, course_id: int) -> Optional[CourseStats]:
        """Récupérer les statistiques d'un cours"""
        from app.models.course import CourseAssignment, Schedule, AssignmentType
        
        course = self.get_course(course_id)
        if not course:
            return None
        
        # Compter les étudiants actifs
        total_students = self.db.query(CourseAssignment).filter(
            and_(
                CourseAssignment.course_id == course_id,
                CourseAssignment.assignment_type == AssignmentType.STUDENT,
                CourseAssignment.valid_from <= date.today(),
                or_(
                    CourseAssignment.valid_to.is_(None),
                    CourseAssignment.valid_to >= date.today()
                )
            )
        ).count()
        
        # Compter les enseignants actifs
        total_teachers = self.db.query(CourseAssignment).filter(
            and_(
                CourseAssignment.course_id == course_id,
                CourseAssignment.assignment_type == AssignmentType.TEACHER,
                CourseAssignment.valid_from <= date.today(),
                or_(
                    CourseAssignment.valid_to.is_(None),
                    CourseAssignment.valid_to >= date.today()
                )
            )
        ).count()
        
        # Compter les créneaux horaires
        total_schedules = self.db.query(Schedule).filter(
            and_(
                Schedule.course_id == course_id,
                Schedule.start_date <= date.today(),
                Schedule.end_date >= date.today()
            )
        ).count()
        
        next_class_datetime = calculate_next_class_datetime(course_id, self.db)

        return CourseStats(
            course_id=course_id,
            total_students=total_students,
            total_teachers=total_teachers,
            total_schedules=total_schedules,
            next_class=next_class_datetime
        )
