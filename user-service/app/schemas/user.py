"""
Schémas Pydantic pour les utilisateurs
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Schémas pour les étudiants
class StudentBase(BaseModel):
    """Schéma de base pour un étudiant"""
    student_number: str = Field(..., min_length=1, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None
    address: Optional[str] = None
    class_name: Optional[str] = Field(None, max_length=50)
    academic_year: Optional[str] = Field(None, max_length=20)
    is_active: bool = True


class StudentCreate(StudentBase):
    """Schéma pour créer un étudiant"""
    user_id: str = Field(..., min_length=1, max_length=50)


class StudentUpdate(BaseModel):
    """Schéma pour mettre à jour un étudiant"""
    student_number: Optional[str] = Field(None, min_length=1, max_length=20)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None
    address: Optional[str] = None
    class_name: Optional[str] = Field(None, max_length=50)
    academic_year: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class Student(StudentBase):
    """Schéma complet d'un étudiant"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schémas pour les enseignants
class TeacherBase(BaseModel):
    """Schéma de base pour un enseignant"""
    employee_number: str = Field(..., min_length=1, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    subject: Optional[str] = Field(None, max_length=100)
    hire_date: Optional[datetime] = None
    is_active: bool = True


class TeacherCreate(TeacherBase):
    """Schéma pour créer un enseignant"""
    user_id: str = Field(..., min_length=1, max_length=50)


class TeacherUpdate(BaseModel):
    """Schéma pour mettre à jour un enseignant"""
    employee_number: Optional[str] = Field(None, min_length=1, max_length=20)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    subject: Optional[str] = Field(None, max_length=100)
    hire_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class Teacher(TeacherBase):
    """Schéma complet d'un enseignant"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schémas pour les parents
class ParentBase(BaseModel):
    """Schéma de base pour un parent"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    profession: Optional[str] = Field(None, max_length=100)
    emergency_contact: bool = False
    is_active: bool = True


class ParentCreate(ParentBase):
    """Schéma pour créer un parent"""
    user_id: str = Field(..., min_length=1, max_length=50)


class ParentUpdate(BaseModel):
    """Schéma pour mettre à jour un parent"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    profession: Optional[str] = Field(None, max_length=100)
    emergency_contact: Optional[bool] = None
    is_active: Optional[bool] = None


class Parent(ParentBase):
    """Schéma complet d'un parent"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schémas pour les relations parent-élève
class ParentStudentRelationBase(BaseModel):
    """Schéma de base pour une relation parent-élève"""
    relationship_type: str = Field(..., min_length=1, max_length=50)
    is_primary_contact: bool = False
    is_emergency_contact: bool = False


class ParentStudentRelationCreate(ParentStudentRelationBase):
    """Schéma pour créer une relation parent-élève"""
    parent_id: int
    student_id: int


class ParentStudentRelation(ParentStudentRelationBase):
    """Schéma complet d'une relation parent-élève"""
    id: int
    parent_id: int
    student_id: int
    created_at: datetime

    class Config:
        from_attributes = True
