"""
Service métier pour la gestion des parents et relations parent-élève
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from ..models.user import Parent, Student, ParentStudentRelation
from ..schemas.user import ParentCreate, ParentUpdate, ParentStudentRelationCreate


class ParentService:
    """Service pour la gestion des parents"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_parent(self, parent_data: ParentCreate) -> Parent:
        """Crée un nouveau parent"""
        db_parent = Parent(**parent_data.model_dump())
        self.db.add(db_parent)
        self.db.commit()
        self.db.refresh(db_parent)
        return db_parent
    
    def get_parent(self, parent_id: int) -> Optional[Parent]:
        """Récupère un parent par son ID"""
        return self.db.query(Parent).filter(Parent.id == parent_id).first()
    
    def get_parent_by_user_id(self, user_id: str) -> Optional[Parent]:
        """Récupère un parent par son user_id"""
        return self.db.query(Parent).filter(Parent.user_id == user_id).first()
    
    def get_parents(self, skip: int = 0, limit: int = 100) -> List[Parent]:
        """Récupère une liste de parents avec pagination"""
        return self.db.query(Parent).offset(skip).limit(limit).all()
    
    def update_parent(self, parent_id: int, parent_data: ParentUpdate) -> Optional[Parent]:
        """Met à jour un parent"""
        db_parent = self.get_parent(parent_id)
        if not db_parent:
            return None
        
        update_data = parent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_parent, field, value)
        
        self.db.commit()
        self.db.refresh(db_parent)
        return db_parent
    
    def delete_parent(self, parent_id: int) -> bool:
        """Supprime un parent"""
        db_parent = self.get_parent(parent_id)
        if not db_parent:
            return False
        
        # Supprimer les relations parent-élève
        self.db.query(ParentStudentRelation).filter(
            ParentStudentRelation.parent_id == parent_id
        ).delete()
        
        self.db.delete(db_parent)
        self.db.commit()
        return True
    
    def search_parents(self, query: str, skip: int = 0, limit: int = 100) -> List[Parent]:
        """Recherche des parents par nom, prénom ou email"""
        search_filter = f"%{query}%"
        return self.db.query(Parent).filter(
            and_(
                Parent.is_active == True,
                (Parent.first_name.ilike(search_filter) |
                 Parent.last_name.ilike(search_filter) |
                 Parent.email.ilike(search_filter))
            )
        ).offset(skip).limit(limit).all()
    
    # Gestion des relations parent-élève
    def create_parent_student_relation(self, relation_data: ParentStudentRelationCreate) -> ParentStudentRelation:
        """Crée une relation parent-élève"""
        db_relation = ParentStudentRelation(**relation_data.model_dump())
        self.db.add(db_relation)
        self.db.commit()
        self.db.refresh(db_relation)
        return db_relation
    
    def get_parent_student_relation(self, relation_id: int) -> Optional[ParentStudentRelation]:
        """Récupère une relation parent-élève par son ID"""
        return self.db.query(ParentStudentRelation).filter(
            ParentStudentRelation.id == relation_id
        ).first()
    
    def get_relations_by_parent(self, parent_id: int) -> List[ParentStudentRelation]:
        """Récupère toutes les relations d'un parent"""
        return self.db.query(ParentStudentRelation).filter(
            ParentStudentRelation.parent_id == parent_id
        ).all()
    
    def get_relations_by_student(self, student_id: int) -> List[ParentStudentRelation]:
        """Récupère toutes les relations d'un élève"""
        return self.db.query(ParentStudentRelation).filter(
            ParentStudentRelation.student_id == student_id
        ).all()
    
    def get_parents_by_student(self, student_id: int) -> List[Parent]:
        """Récupère tous les parents d'un élève"""
        return self.db.query(Parent).join(
            ParentStudentRelation,
            Parent.id == ParentStudentRelation.parent_id
        ).filter(ParentStudentRelation.student_id == student_id).all()
    
    def delete_parent_student_relation(self, relation_id: int) -> bool:
        """Supprime une relation parent-élève"""
        db_relation = self.get_parent_student_relation(relation_id)
        if not db_relation:
            return False
        
        self.db.delete(db_relation)
        self.db.commit()
        return True
    
    def relation_exists(self, parent_id: int, student_id: int) -> bool:
        """Vérifie si une relation parent-élève existe déjà"""
        return self.db.query(ParentStudentRelation).filter(
            and_(
                ParentStudentRelation.parent_id == parent_id,
                ParentStudentRelation.student_id == student_id
            )
        ).first() is not None
