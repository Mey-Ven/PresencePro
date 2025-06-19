"""
Schémas Pydantic pour le service utilisateur
"""
from .user import (
    StudentBase, StudentCreate, StudentUpdate, Student,
    TeacherBase, TeacherCreate, TeacherUpdate, Teacher,
    ParentBase, ParentCreate, ParentUpdate, Parent,
    ParentStudentRelationBase, ParentStudentRelationCreate, ParentStudentRelation
)

__all__ = [
    "StudentBase", "StudentCreate", "StudentUpdate", "Student",
    "TeacherBase", "TeacherCreate", "TeacherUpdate", "Teacher", 
    "ParentBase", "ParentCreate", "ParentUpdate", "Parent",
    "ParentStudentRelationBase", "ParentStudentRelationCreate", "ParentStudentRelation"
]
