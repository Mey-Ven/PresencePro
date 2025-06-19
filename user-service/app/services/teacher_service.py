"""
Service métier pour la gestion des enseignants
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from ..models.user import Teacher
from ..schemas.user import TeacherCreate, TeacherUpdate


class TeacherService:
    """Service pour la gestion des enseignants"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_teacher(self, teacher_data: TeacherCreate) -> Teacher:
        """Crée un nouvel enseignant"""
        db_teacher = Teacher(**teacher_data.model_dump())
        self.db.add(db_teacher)
        self.db.commit()
        self.db.refresh(db_teacher)
        return db_teacher
    
    def get_teacher(self, teacher_id: int) -> Optional[Teacher]:
        """Récupère un enseignant par son ID"""
        return self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
    
    def get_teacher_by_user_id(self, user_id: str) -> Optional[Teacher]:
        """Récupère un enseignant par son user_id"""
        return self.db.query(Teacher).filter(Teacher.user_id == user_id).first()
    
    def get_teacher_by_employee_number(self, employee_number: str) -> Optional[Teacher]:
        """Récupère un enseignant par son numéro d'employé"""
        return self.db.query(Teacher).filter(Teacher.employee_number == employee_number).first()
    
    def get_teachers(self, skip: int = 0, limit: int = 100, department: Optional[str] = None) -> List[Teacher]:
        """Récupère une liste d'enseignants avec pagination"""
        query = self.db.query(Teacher)
        
        if department:
            query = query.filter(Teacher.department == department)
        
        return query.offset(skip).limit(limit).all()
    
    def update_teacher(self, teacher_id: int, teacher_data: TeacherUpdate) -> Optional[Teacher]:
        """Met à jour un enseignant"""
        db_teacher = self.get_teacher(teacher_id)
        if not db_teacher:
            return None
        
        update_data = teacher_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_teacher, field, value)
        
        self.db.commit()
        self.db.refresh(db_teacher)
        return db_teacher
    
    def delete_teacher(self, teacher_id: int) -> bool:
        """Supprime un enseignant"""
        db_teacher = self.get_teacher(teacher_id)
        if not db_teacher:
            return False
        
        self.db.delete(db_teacher)
        self.db.commit()
        return True
    
    def search_teachers(self, query: str, skip: int = 0, limit: int = 100) -> List[Teacher]:
        """Recherche des enseignants par nom, prénom, département ou matière"""
        search_filter = f"%{query}%"
        return self.db.query(Teacher).filter(
            and_(
                Teacher.is_active == True,
                (Teacher.first_name.ilike(search_filter) |
                 Teacher.last_name.ilike(search_filter) |
                 Teacher.employee_number.ilike(search_filter) |
                 Teacher.email.ilike(search_filter) |
                 Teacher.department.ilike(search_filter) |
                 Teacher.subject.ilike(search_filter))
            )
        ).offset(skip).limit(limit).all()
    
    def get_teachers_by_department(self, department: str) -> List[Teacher]:
        """Récupère tous les enseignants d'un département"""
        return self.db.query(Teacher).filter(
            and_(Teacher.department == department, Teacher.is_active == True)
        ).all()
    
    def get_teachers_by_subject(self, subject: str) -> List[Teacher]:
        """Récupère tous les enseignants d'une matière"""
        return self.db.query(Teacher).filter(
            and_(Teacher.subject == subject, Teacher.is_active == True)
        ).all()
