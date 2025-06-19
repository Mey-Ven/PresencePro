"""
Tests pour les services métier
"""
import pytest
from datetime import date, time
from app.services.course_service import CourseService
from app.services.schedule_service import ScheduleService
from app.services.assignment_service import AssignmentService
from app.models.course import Course, Schedule, CourseAssignment, DayOfWeek, AssignmentType
from app.schemas.course import CourseCreate, ScheduleCreate, CourseAssignmentCreate


class TestCourseService:
    """Tests pour le service de gestion des cours"""
    
    def test_create_course(self, db_session, sample_course_data):
        """Test de création d'un cours"""
        service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        
        course = service.create_course(course_create)
        
        assert course.id is not None
        assert course.name == sample_course_data["name"]
        assert course.code == sample_course_data["code"]
        assert course.subject == sample_course_data["subject"]
    
    def test_create_course_duplicate_code(self, db_session, sample_course_data):
        """Test de création d'un cours avec code dupliqué"""
        service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        
        # Créer le premier cours
        service.create_course(course_create)
        
        # Tenter de créer un cours avec le même code
        with pytest.raises(ValueError, match="existe déjà"):
            service.create_course(course_create)
    
    def test_get_course(self, db_session, sample_course_data):
        """Test de récupération d'un cours"""
        service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        
        created_course = service.create_course(course_create)
        retrieved_course = service.get_course(created_course.id)
        
        assert retrieved_course is not None
        assert retrieved_course.id == created_course.id
        assert retrieved_course.name == created_course.name
    
    def test_get_course_not_found(self, db_session):
        """Test de récupération d'un cours inexistant"""
        service = CourseService(db_session)
        course = service.get_course(999)
        
        assert course is None
    
    def test_get_courses_with_filters(self, db_session):
        """Test de récupération des cours avec filtres"""
        service = CourseService(db_session)
        
        # Créer des cours avec différentes matières
        subjects = ["Mathématiques", "Physique", "Français"]
        for i, subject in enumerate(subjects):
            course_data = {
                "name": f"Course {i}",
                "code": f"TEST{i:03d}",
                "subject": subject,
                "level": "6ème",
                "academic_year": "2023-2024",
                "semester": "Semestre 1"
            }
            course_create = CourseCreate(**course_data)
            service.create_course(course_create)
        
        # Filtrer par matière
        math_courses = service.get_courses(subject="Mathématiques")
        assert len(math_courses) == 1
        assert math_courses[0].subject == "Mathématiques"
        
        # Filtrer par niveau
        all_courses = service.get_courses(level="6ème")
        assert len(all_courses) == 3
    
    def test_update_course(self, db_session, sample_course_data):
        """Test de mise à jour d'un cours"""
        service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        
        course = service.create_course(course_create)
        
        from app.schemas.course import CourseUpdate
        update_data = CourseUpdate(name="Updated Name", credits=5)
        updated_course = service.update_course(course.id, update_data)
        
        assert updated_course is not None
        assert updated_course.name == "Updated Name"
        assert updated_course.credits == 5
        assert updated_course.code == sample_course_data["code"]  # Inchangé
    
    def test_delete_course(self, db_session, sample_course_data):
        """Test de suppression d'un cours"""
        service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        
        course = service.create_course(course_create)
        course_id = course.id
        
        # Supprimer le cours
        result = service.delete_course(course_id)
        assert result is True
        
        # Vérifier que le cours n'existe plus
        deleted_course = service.get_course(course_id)
        assert deleted_course is None
    
    def test_search_courses(self, db_session):
        """Test de recherche de cours"""
        service = CourseService(db_session)
        
        # Créer des cours
        courses_data = [
            {"name": "Advanced Mathematics", "code": "MATH001", "subject": "Mathematics"},
            {"name": "Basic Physics", "code": "PHYS001", "subject": "Physics"},
            {"name": "Mathematical Analysis", "code": "MATH002", "subject": "Mathematics"}
        ]
        
        for course_data in courses_data:
            full_data = {
                "level": "6ème",
                "academic_year": "2023-2024",
                "semester": "Semestre 1",
                **course_data
            }
            course_create = CourseCreate(**full_data)
            service.create_course(course_create)
        
        # Rechercher par terme
        results = service.search_courses("Math")
        assert len(results) == 2
        
        results = service.search_courses("Physics")
        assert len(results) == 1


class TestScheduleService:
    """Tests pour le service de gestion des emplois du temps"""
    
    def test_create_schedule(self, db_session, sample_course_data, sample_schedule_data):
        """Test de création d'un emploi du temps"""
        # Créer d'abord un cours
        course_service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        course = course_service.create_course(course_create)
        
        # Créer l'emploi du temps
        schedule_service = ScheduleService(db_session)
        sample_schedule_data["course_id"] = course.id
        schedule_create = ScheduleCreate(**sample_schedule_data)
        
        schedule = schedule_service.create_schedule(schedule_create)
        
        assert schedule.id is not None
        assert schedule.course_id == course.id
        assert schedule.day_of_week == sample_schedule_data["day_of_week"]
        assert schedule.room == sample_schedule_data["room"]
    
    def test_create_schedule_invalid_course(self, db_session, sample_schedule_data):
        """Test de création d'un emploi du temps avec cours inexistant"""
        schedule_service = ScheduleService(db_session)
        sample_schedule_data["course_id"] = 999  # Cours inexistant
        schedule_create = ScheduleCreate(**sample_schedule_data)
        
        with pytest.raises(ValueError, match="n'existe pas"):
            schedule_service.create_schedule(schedule_create)
    
    def test_get_schedules_by_day(self, db_session, sample_course_data, sample_schedule_data):
        """Test de récupération des emplois du temps par jour"""
        # Créer un cours et un emploi du temps
        course_service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        course = course_service.create_course(course_create)
        
        schedule_service = ScheduleService(db_session)
        sample_schedule_data["course_id"] = course.id
        schedule_create = ScheduleCreate(**sample_schedule_data)
        schedule_service.create_schedule(schedule_create)
        
        # Récupérer les emplois du temps du lundi
        schedules = schedule_service.get_schedules_by_day(DayOfWeek.MONDAY)
        assert len(schedules) == 1
        assert schedules[0].day_of_week == DayOfWeek.MONDAY


class TestAssignmentService:
    """Tests pour le service de gestion des attributions"""
    
    def test_create_assignment(self, db_session, sample_course_data, sample_assignment_data):
        """Test de création d'une attribution"""
        # Créer d'abord un cours
        course_service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        course = course_service.create_course(course_create)
        
        # Créer l'attribution
        assignment_service = AssignmentService(db_session)
        sample_assignment_data["course_id"] = course.id
        assignment_create = CourseAssignmentCreate(**sample_assignment_data)
        
        assignment = assignment_service.create_assignment(assignment_create)
        
        assert assignment.id is not None
        assert assignment.course_id == course.id
        assert assignment.user_id == sample_assignment_data["user_id"]
        assert assignment.assignment_type == sample_assignment_data["assignment_type"]
    
    def test_create_assignment_invalid_course(self, db_session, sample_assignment_data):
        """Test de création d'une attribution avec cours inexistant"""
        assignment_service = AssignmentService(db_session)
        sample_assignment_data["course_id"] = 999  # Cours inexistant
        assignment_create = CourseAssignmentCreate(**sample_assignment_data)
        
        with pytest.raises(ValueError, match="n'existe pas"):
            assignment_service.create_assignment(assignment_create)
    
    def test_get_assignments_by_course(self, db_session, sample_course_data, sample_assignment_data):
        """Test de récupération des attributions par cours"""
        # Créer un cours et une attribution
        course_service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        course = course_service.create_course(course_create)
        
        assignment_service = AssignmentService(db_session)
        sample_assignment_data["course_id"] = course.id
        assignment_create = CourseAssignmentCreate(**sample_assignment_data)
        assignment_service.create_assignment(assignment_create)
        
        # Récupérer les attributions du cours
        assignments = assignment_service.get_assignments_by_course(course.id)
        assert len(assignments) == 1
        assert assignments[0].course_id == course.id
    
    def test_get_teachers_by_course(self, db_session, sample_course_data):
        """Test de récupération des enseignants d'un cours"""
        # Créer un cours
        course_service = CourseService(db_session)
        course_create = CourseCreate(**sample_course_data)
        course = course_service.create_course(course_create)
        
        # Créer des attributions d'enseignants
        assignment_service = AssignmentService(db_session)
        for i in range(2):
            assignment_data = {
                "course_id": course.id,
                "user_id": f"teacher{i+1}",
                "assignment_type": AssignmentType.TEACHER,
                "is_primary": i == 0,
                "valid_from": date(2023, 9, 1),
                "valid_to": date(2024, 6, 30)
            }
            assignment_create = CourseAssignmentCreate(**assignment_data)
            assignment_service.create_assignment(assignment_create)
        
        # Récupérer les enseignants
        teachers = assignment_service.get_teachers_by_course(course.id)
        assert len(teachers) == 2
        assert all(t.assignment_type == AssignmentType.TEACHER for t in teachers)
