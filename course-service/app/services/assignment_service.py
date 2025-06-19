"""
Service métier pour la gestion des attributions de cours
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date
from app.models.course import CourseAssignment, Course, AssignmentType
from app.schemas.course import CourseAssignmentCreate, CourseAssignmentUpdate


class AssignmentService:
    """Service pour la gestion des attributions de cours"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_assignment(self, assignment_data: CourseAssignmentCreate) -> CourseAssignment:
        """Créer une nouvelle attribution de cours"""
        # Vérifier que le cours existe
        course = self.db.query(Course).filter(Course.id == assignment_data.course_id).first()
        if not course:
            raise ValueError(f"Le cours avec l'ID {assignment_data.course_id} n'existe pas")
        
        # Vérifier que l'utilisateur n'est pas déjà assigné au cours pour la même période
        existing_assignment = self._check_existing_assignment(
            assignment_data.course_id,
            assignment_data.user_id,
            assignment_data.assignment_type,
            assignment_data.valid_from,
            assignment_data.valid_to
        )
        
        if existing_assignment:
            raise ValueError(f"L'utilisateur {assignment_data.user_id} est déjà assigné à ce cours pour cette période")
        
        # Vérifier la capacité maximale pour les étudiants
        if assignment_data.assignment_type == AssignmentType.STUDENT:
            current_students = self.get_active_students_count(assignment_data.course_id)
            if current_students >= course.max_students:
                raise ValueError(f"Le cours a atteint sa capacité maximale de {course.max_students} étudiants")
        
        assignment = CourseAssignment(**assignment_data.model_dump())
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def get_assignment(self, assignment_id: int) -> Optional[CourseAssignment]:
        """Récupérer une attribution par son ID"""
        return self.db.query(CourseAssignment).filter(CourseAssignment.id == assignment_id).first()
    
    def get_assignments_by_course(self, course_id: int, active_only: bool = True) -> List[CourseAssignment]:
        """Récupérer toutes les attributions d'un cours"""
        query = self.db.query(CourseAssignment).filter(CourseAssignment.course_id == course_id)
        
        if active_only:
            today = date.today()
            query = query.filter(
                and_(
                    CourseAssignment.valid_from <= today,
                    or_(
                        CourseAssignment.valid_to.is_(None),
                        CourseAssignment.valid_to >= today
                    )
                )
            )
        
        return query.all()
    
    def get_assignments_by_user(self, user_id: str, active_only: bool = True) -> List[CourseAssignment]:
        """Récupérer toutes les attributions d'un utilisateur"""
        query = self.db.query(CourseAssignment).filter(CourseAssignment.user_id == user_id)
        
        if active_only:
            today = date.today()
            query = query.filter(
                and_(
                    CourseAssignment.valid_from <= today,
                    or_(
                        CourseAssignment.valid_to.is_(None),
                        CourseAssignment.valid_to >= today
                    )
                )
            )
        
        return query.all()
    
    def get_teachers_by_course(self, course_id: int) -> List[CourseAssignment]:
        """Récupérer les enseignants d'un cours"""
        today = date.today()
        return self.db.query(CourseAssignment).filter(
            and_(
                CourseAssignment.course_id == course_id,
                CourseAssignment.assignment_type == AssignmentType.TEACHER,
                CourseAssignment.valid_from <= today,
                or_(
                    CourseAssignment.valid_to.is_(None),
                    CourseAssignment.valid_to >= today
                )
            )
        ).all()
    
    def get_students_by_course(self, course_id: int) -> List[CourseAssignment]:
        """Récupérer les étudiants d'un cours"""
        today = date.today()
        return self.db.query(CourseAssignment).filter(
            and_(
                CourseAssignment.course_id == course_id,
                CourseAssignment.assignment_type == AssignmentType.STUDENT,
                CourseAssignment.valid_from <= today,
                or_(
                    CourseAssignment.valid_to.is_(None),
                    CourseAssignment.valid_to >= today
                )
            )
        ).all()
    
    def get_active_students_count(self, course_id: int) -> int:
        """Compter le nombre d'étudiants actifs dans un cours"""
        today = date.today()
        return self.db.query(CourseAssignment).filter(
            and_(
                CourseAssignment.course_id == course_id,
                CourseAssignment.assignment_type == AssignmentType.STUDENT,
                CourseAssignment.valid_from <= today,
                or_(
                    CourseAssignment.valid_to.is_(None),
                    CourseAssignment.valid_to >= today
                )
            )
        ).count()
    
    def update_assignment(self, assignment_id: int, assignment_data: CourseAssignmentUpdate) -> Optional[CourseAssignment]:
        """Mettre à jour une attribution"""
        assignment = self.get_assignment(assignment_id)
        if not assignment:
            return None
        
        update_data = assignment_data.model_dump(exclude_unset=True)
        
        # Vérifier les conflits si les dates changent
        if 'valid_from' in update_data or 'valid_to' in update_data:
            valid_from = update_data.get('valid_from', assignment.valid_from)
            valid_to = update_data.get('valid_to', assignment.valid_to)
            
            existing_assignment = self._check_existing_assignment(
                assignment.course_id,
                assignment.user_id,
                assignment.assignment_type,
                valid_from,
                valid_to,
                exclude_id=assignment_id
            )
            
            if existing_assignment:
                raise ValueError(f"Conflit détecté avec l'attribution ID {existing_assignment.id}")
        
        for field, value in update_data.items():
            setattr(assignment, field, value)
        
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def delete_assignment(self, assignment_id: int) -> bool:
        """Supprimer une attribution"""
        assignment = self.get_assignment(assignment_id)
        if not assignment:
            return False
        
        self.db.delete(assignment)
        self.db.commit()
        return True
    
    def assign_multiple_users(self, course_id: int, assignments: List[CourseAssignmentCreate]) -> List[CourseAssignment]:
        """Assigner plusieurs utilisateurs à un cours"""
        created_assignments = []
        
        try:
            for assignment_data in assignments:
                assignment_data.course_id = course_id
                assignment = self.create_assignment(assignment_data)
                created_assignments.append(assignment)
            
            return created_assignments
        
        except Exception as e:
            # En cas d'erreur, annuler toutes les créations
            self.db.rollback()
            raise e
    
    def remove_user_from_course(self, course_id: int, user_id: str) -> bool:
        """Retirer un utilisateur d'un cours (marquer comme terminé)"""
        today = date.today()
        
        # Trouver les attributions actives
        active_assignments = self.db.query(CourseAssignment).filter(
            and_(
                CourseAssignment.course_id == course_id,
                CourseAssignment.user_id == user_id,
                CourseAssignment.valid_from <= today,
                or_(
                    CourseAssignment.valid_to.is_(None),
                    CourseAssignment.valid_to >= today
                )
            )
        ).all()
        
        if not active_assignments:
            return False
        
        # Marquer comme terminé aujourd'hui
        for assignment in active_assignments:
            assignment.valid_to = today
        
        self.db.commit()
        return True
    
    def _check_existing_assignment(
        self,
        course_id: int,
        user_id: str,
        assignment_type: AssignmentType,
        valid_from: date,
        valid_to: Optional[date],
        exclude_id: int = None
    ) -> Optional[CourseAssignment]:
        """Vérifier s'il existe déjà une attribution pour cette période"""
        query = self.db.query(CourseAssignment).filter(
            and_(
                CourseAssignment.course_id == course_id,
                CourseAssignment.user_id == user_id,
                CourseAssignment.assignment_type == assignment_type,
                # Vérification du chevauchement des dates
                or_(
                    and_(
                        CourseAssignment.valid_from <= valid_from,
                        or_(
                            CourseAssignment.valid_to.is_(None),
                            CourseAssignment.valid_to >= valid_from
                        )
                    ),
                    and_(
                        valid_to.is_(None) if valid_to is None else CourseAssignment.valid_from <= valid_to,
                        CourseAssignment.valid_from >= valid_from
                    ) if valid_to else CourseAssignment.valid_from >= valid_from
                )
            )
        )
        
        if exclude_id:
            query = query.filter(CourseAssignment.id != exclude_id)
        
        return query.first()
