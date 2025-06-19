"""
Configuration des tests pour le service utilisateur
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch

from app.main import app
from app.core.database import get_db, Base
from app.models.user import Student, Teacher, Parent, ParentStudentRelation
from app.schemas.user import StudentCreate, TeacherCreate, ParentCreate

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dépendance de base de données pour les tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override de la dépendance
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Fixture pour la boucle d'événements asyncio"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Fixture pour une session de base de données de test"""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    # Créer une session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Nettoyer après chaque test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture pour le client de test FastAPI"""
    with TestClient(app) as test_client:
        yield test_client


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
def mock_auth_parent():
    """Mock du service d'authentification pour un parent"""
    with patch('app.core.auth.auth_service') as mock:
        async def mock_verify_token(token):
            return {
                "id": "parent1",
                "username": "parent1",
                "role": "parent",
                "email": "parent1@presencepro.com"
            }

        async def mock_check_permission(token, role):
            return role in ["parent", "student"]

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
def sample_student_data():
    """Données d'exemple pour un étudiant"""
    return {
        "user_id": "student_test",
        "student_number": "STU999",
        "first_name": "Test",
        "last_name": "Student",
        "email": "test.student@example.com",
        "phone": "0123456789",
        "class_name": "Test Class",
        "academic_year": "2023-2024",
        "is_active": True
    }


@pytest.fixture
def sample_teacher_data():
    """Données d'exemple pour un enseignant"""
    return {
        "user_id": "teacher_test",
        "employee_number": "EMP999",
        "first_name": "Test",
        "last_name": "Teacher",
        "email": "test.teacher@example.com",
        "phone": "0123456789",
        "department": "Test Department",
        "subject": "Test Subject",
        "is_active": True
    }


@pytest.fixture
def sample_parent_data():
    """Données d'exemple pour un parent"""
    return {
        "user_id": "parent_test",
        "first_name": "Test",
        "last_name": "Parent",
        "email": "test.parent@example.com",
        "phone": "0123456789",
        "profession": "Test Profession",
        "emergency_contact": True,
        "is_active": True
    }
