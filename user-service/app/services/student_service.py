"""
Service métier pour la gestion des étudiants
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from ..models.user import Student, ParentStudentRelation
from ..schemas.user import StudentCreate, StudentUpdate


class StudentService:
    """Service pour la gestion des étudiants"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_student(self, student_data: StudentCreate) -> Student:
        """Crée un nouvel étudiant"""
        db_student = Student(**student_data.model_dump())
        self.db.add(db_student)
        self.db.commit()
        self.db.refresh(db_student)
        return db_student
    
    def get_student(self, student_id: int) -> Optional[Student]:
        """Récupère un étudiant par son ID"""
        return self.db.query(Student).filter(Student.id == student_id).first()
    
    def get_student_by_user_id(self, user_id: str) -> Optional[Student]:
        """Récupère un étudiant par son user_id"""
        return self.db.query(Student).filter(Student.user_id == user_id).first()
    
    def get_student_by_number(self, student_number: str) -> Optional[Student]:
        """Récupère un étudiant par son numéro"""
        return self.db.query(Student).filter(Student.student_number == student_number).first()
    
    def get_students(self, skip: int = 0, limit: int = 100, class_name: Optional[str] = None) -> List[Student]:
        """Récupère une liste d'étudiants avec pagination"""
        query = self.db.query(Student)
        
        if class_name:
            query = query.filter(Student.class_name == class_name)
        
        return query.offset(skip).limit(limit).all()
    
    def update_student(self, student_id: int, student_data: StudentUpdate) -> Optional[Student]:
        """Met à jour un étudiant"""
        db_student = self.get_student(student_id)
        if not db_student:
            return None
        
        update_data = student_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_student, field, value)
        
        self.db.commit()
        self.db.refresh(db_student)
        return db_student
    
    def delete_student(self, student_id: int) -> bool:
        """Supprime un étudiant"""
        db_student = self.get_student(student_id)
        if not db_student:
            return False
        
        # Supprimer les relations parent-élève
        self.db.query(ParentStudentRelation).filter(
            ParentStudentRelation.student_id == student_id
        ).delete()
        
        self.db.delete(db_student)
        self.db.commit()
        return True
    
    def get_students_by_parent(self, parent_id: int) -> List[Student]:
        """Récupère les étudiants liés à un parent"""
        return self.db.query(Student).join(
            ParentStudentRelation,
            Student.id == ParentStudentRelation.student_id
        ).filter(ParentStudentRelation.parent_id == parent_id).all()
    
    def search_students(self, query: str, skip: int = 0, limit: int = 100) -> List[Student]:
        """Recherche des étudiants par nom, prénom ou numéro"""
        search_filter = f"%{query}%"
        return self.db.query(Student).filter(
            and_(
                Student.is_active == True,
                (Student.first_name.ilike(search_filter) |
                 Student.last_name.ilike(search_filter) |
                 Student.student_number.ilike(search_filter) |
                 Student.email.ilike(search_filter))
            )
        ).offset(skip).limit(limit).all()
