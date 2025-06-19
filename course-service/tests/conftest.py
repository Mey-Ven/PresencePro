"""
Configuration des tests pour le service de cours
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch

from app.main import app
from app.core.database import get_db, Base

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_courses.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dépendance de base de données pour les tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Fixture pour la session de base de données de test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture pour le client de test FastAPI"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_auth_service():
    """Mock du service d'authentification"""
    with patch('app.core.auth.auth_service') as mock:
        # Configuration par défaut pour un admin
        async def mock_verify_token(token):
            return {
                "id": "admin",
                "username": "admin",
                "role": "admin",
                "email": "admin@presencepro.com"
            }
        
        async def mock_check_permission(token, role):
            return True
        
        mock.verify_token = mock_verify_token
        mock.check_permission = mock_check_permission
        yield mock


@pytest.fixture
def mock_auth_teacher():
    """Mock du service d'authentification pour un enseignant"""
    with patch('app.core.auth.auth_service') as mock:
        async def mock_verify_token(token):
            return {
                "id": "teacher1",
                "username": "teacher1",
                "role": "teacher",
                "email": "teacher1@presencepro.com"
            }
        
        async def mock_check_permission(token, role):
            return role in ["teacher", "parent", "student"]
        
        mock.verify_token = mock_verify_token
        mock.check_permission = mock_check_permission
        yield mock


@pytest.fixture
def mock_auth_student():
    """Mock du service d'authentification pour un étudiant"""
    with patch('app.core.auth.auth_service') as mock:
        async def mock_verify_token(token):
            return {
                "id": "student1",
                "username": "student1",
                "role": "student",
                "email": "student1@presencepro.com"
            }
        
        async def mock_check_permission(token, role):
            return role == "student"
        
        mock.verify_token = mock_verify_token
        mock.check_permission = mock_check_permission
        yield mock


@pytest.fixture
def sample_course_data():
    """Données d'exemple pour un cours"""
    return {
        "name": "Test Course",
        "code": "TEST001",
        "description": "A test course",
        "subject": "Test Subject",
        "level": "6ème",
        "credits": 3,
        "max_students": 25,
        "academic_year": "2023-2024",
        "semester": "Semestre 1"
    }


@pytest.fixture
def sample_schedule_data():
    """Données d'exemple pour un emploi du temps"""
    from datetime import time, date
    from app.models.course import DayOfWeek
    
    return {
        "course_id": 1,
        "day_of_week": DayOfWeek.MONDAY,
        "start_time": time(8, 0),
        "end_time": time(9, 30),
        "room": "A101",
        "building": "Building A",
        "start_date": date(2023, 9, 1),
        "end_date": date(2024, 6, 30)
    }


@pytest.fixture
def sample_assignment_data():
    """Données d'exemple pour une attribution"""
    from datetime import date
    from app.models.course import AssignmentType
    
    return {
        "course_id": 1,
        "user_id": "teacher1",
        "assignment_type": AssignmentType.TEACHER,
        "is_primary": True,
        "valid_from": date(2023, 9, 1),
        "valid_to": date(2024, 6, 30)
    }
