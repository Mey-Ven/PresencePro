"""
Tests pour les services métier
"""
import pytest
from app.services.student_service import StudentService
from app.services.teacher_service import TeacherService
from app.services.parent_service import ParentService
from app.schemas.user import StudentCreate, TeacherCreate, ParentCreate, ParentStudentRelationCreate


class TestStudentService:
    """Tests pour le service des étudiants"""
    
    def test_create_student(self, db_session, sample_student_data):
        """Test de création d'un étudiant"""
        service = StudentService(db_session)
        student_create = StudentCreate(**sample_student_data)
        
        student = service.create_student(student_create)
        
        assert student.user_id == sample_student_data["user_id"]
        assert student.student_number == sample_student_data["student_number"]
        assert student.first_name == sample_student_data["first_name"]
        assert student.last_name == sample_student_data["last_name"]
        assert student.email == sample_student_data["email"]
    
    def test_get_student_by_id(self, db_session, sample_student_data):
        """Test de récupération d'un étudiant par ID"""
        service = StudentService(db_session)
        student_create = StudentCreate(**sample_student_data)
        created_student = service.create_student(student_create)
        
        retrieved_student = service.get_student(created_student.id)
        
        assert retrieved_student is not None
        assert retrieved_student.id == created_student.id
        assert retrieved_student.user_id == sample_student_data["user_id"]
    
    def test_get_student_by_user_id(self, db_session, sample_student_data):
        """Test de récupération d'un étudiant par user_id"""
        service = StudentService(db_session)
        student_create = StudentCreate(**sample_student_data)
        created_student = service.create_student(student_create)
        
        retrieved_student = service.get_student_by_user_id(sample_student_data["user_id"])
        
        assert retrieved_student is not None
        assert retrieved_student.user_id == sample_student_data["user_id"]
    
    def test_get_students_with_pagination(self, db_session, sample_student_data):
        """Test de récupération avec pagination"""
        service = StudentService(db_session)
        
        # Créer plusieurs étudiants
        for i in range(5):
            data = sample_student_data.copy()
            data["user_id"] = f"student_{i}"
            data["student_number"] = f"STU{i:03d}"
            data["email"] = f"student{i}@example.com"
            student_create = StudentCreate(**data)
            service.create_student(student_create)
        
        # Test pagination
        students = service.get_students(skip=0, limit=3)
        assert len(students) == 3
        
        students = service.get_students(skip=3, limit=3)
        assert len(students) == 2
    
    def test_update_student(self, db_session, sample_student_data):
        """Test de mise à jour d'un étudiant"""
        service = StudentService(db_session)
        student_create = StudentCreate(**sample_student_data)
        created_student = service.create_student(student_create)
        
        from app.schemas.user import StudentUpdate
        update_data = StudentUpdate(first_name="Updated Name")
        updated_student = service.update_student(created_student.id, update_data)
        
        assert updated_student is not None
        assert updated_student.first_name == "Updated Name"
        assert updated_student.last_name == sample_student_data["last_name"]  # Inchangé
    
    def test_delete_student(self, db_session, sample_student_data):
        """Test de suppression d'un étudiant"""
        service = StudentService(db_session)
        student_create = StudentCreate(**sample_student_data)
        created_student = service.create_student(student_create)
        
        result = service.delete_student(created_student.id)
        assert result is True
        
        # Vérifier que l'étudiant n'existe plus
        deleted_student = service.get_student(created_student.id)
        assert deleted_student is None
    
    def test_search_students(self, db_session, sample_student_data):
        """Test de recherche d'étudiants"""
        service = StudentService(db_session)
        student_create = StudentCreate(**sample_student_data)
        service.create_student(student_create)
        
        # Recherche par prénom
        results = service.search_students(sample_student_data["first_name"])
        assert len(results) >= 1
        assert results[0].first_name == sample_student_data["first_name"]


class TestTeacherService:
    """Tests pour le service des enseignants"""
    
    def test_create_teacher(self, db_session, sample_teacher_data):
        """Test de création d'un enseignant"""
        service = TeacherService(db_session)
        teacher_create = TeacherCreate(**sample_teacher_data)
        
        teacher = service.create_teacher(teacher_create)
        
        assert teacher.user_id == sample_teacher_data["user_id"]
        assert teacher.employee_number == sample_teacher_data["employee_number"]
        assert teacher.first_name == sample_teacher_data["first_name"]
        assert teacher.department == sample_teacher_data["department"]
    
    def test_get_teachers_by_department(self, db_session, sample_teacher_data):
        """Test de récupération par département"""
        service = TeacherService(db_session)
        teacher_create = TeacherCreate(**sample_teacher_data)
        service.create_teacher(teacher_create)
        
        teachers = service.get_teachers_by_department(sample_teacher_data["department"])
        assert len(teachers) >= 1
        assert teachers[0].department == sample_teacher_data["department"]
    
    def test_search_teachers(self, db_session, sample_teacher_data):
        """Test de recherche d'enseignants"""
        service = TeacherService(db_session)
        teacher_create = TeacherCreate(**sample_teacher_data)
        service.create_teacher(teacher_create)
        
        # Recherche par département
        results = service.search_teachers(sample_teacher_data["department"])
        assert len(results) >= 1
        assert results[0].department == sample_teacher_data["department"]


class TestParentService:
    """Tests pour le service des parents"""
    
    def test_create_parent(self, db_session, sample_parent_data):
        """Test de création d'un parent"""
        service = ParentService(db_session)
        parent_create = ParentCreate(**sample_parent_data)
        
        parent = service.create_parent(parent_create)
        
        assert parent.user_id == sample_parent_data["user_id"]
        assert parent.first_name == sample_parent_data["first_name"]
        assert parent.profession == sample_parent_data["profession"]
    
    def test_create_parent_student_relation(self, db_session, sample_parent_data, sample_student_data):
        """Test de création d'une relation parent-élève"""
        parent_service = ParentService(db_session)
        student_service = StudentService(db_session)
        
        # Créer un parent et un étudiant
        parent_create = ParentCreate(**sample_parent_data)
        parent = parent_service.create_parent(parent_create)
        
        student_create = StudentCreate(**sample_student_data)
        student = student_service.create_student(student_create)
        
        # Créer la relation
        relation_data = ParentStudentRelationCreate(
            parent_id=parent.id,
            student_id=student.id,
            relationship_type="père",
            is_primary_contact=True
        )
        relation = parent_service.create_parent_student_relation(relation_data)
        
        assert relation.parent_id == parent.id
        assert relation.student_id == student.id
        assert relation.relationship_type == "père"
        assert relation.is_primary_contact is True
    
    def test_get_parents_by_student(self, db_session, sample_parent_data, sample_student_data):
        """Test de récupération des parents d'un élève"""
        parent_service = ParentService(db_session)
        student_service = StudentService(db_session)
        
        # Créer un parent et un étudiant
        parent_create = ParentCreate(**sample_parent_data)
        parent = parent_service.create_parent(parent_create)
        
        student_create = StudentCreate(**sample_student_data)
        student = student_service.create_student(student_create)
        
        # Créer la relation
        relation_data = ParentStudentRelationCreate(
            parent_id=parent.id,
            student_id=student.id,
            relationship_type="père"
        )
        parent_service.create_parent_student_relation(relation_data)
        
        # Récupérer les parents de l'élève
        parents = parent_service.get_parents_by_student(student.id)
        assert len(parents) == 1
        assert parents[0].id == parent.id
    
    def test_relation_exists(self, db_session, sample_parent_data, sample_student_data):
        """Test de vérification d'existence d'une relation"""
        parent_service = ParentService(db_session)
        student_service = StudentService(db_session)
        
        # Créer un parent et un étudiant
        parent_create = ParentCreate(**sample_parent_data)
        parent = parent_service.create_parent(parent_create)
        
        student_create = StudentCreate(**sample_student_data)
        student = student_service.create_student(student_create)
        
        # Vérifier qu'aucune relation n'existe
        assert parent_service.relation_exists(parent.id, student.id) is False
        
        # Créer la relation
        relation_data = ParentStudentRelationCreate(
            parent_id=parent.id,
            student_id=student.id,
            relationship_type="père"
        )
        parent_service.create_parent_student_relation(relation_data)
        
        # Vérifier que la relation existe maintenant
        assert parent_service.relation_exists(parent.id, student.id) is True
