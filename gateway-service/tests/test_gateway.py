"""
Tests pour le Gateway Service
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.config import settings
from app.auth import auth_manager


@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(app)


@pytest.fixture
def admin_token():
    """Token JWT pour un administrateur"""
    payload = {
        "sub": "admin_user_id",
        "email": "admin@presencepro.com",
        "role": "admin",
        "permissions": ["read", "write", "admin"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return auth_manager.create_access_token(payload)


@pytest.fixture
def teacher_token():
    """Token JWT pour un enseignant"""
    payload = {
        "sub": "teacher_user_id",
        "email": "teacher@presencepro.com",
        "role": "teacher",
        "permissions": ["read", "write"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return auth_manager.create_access_token(payload)


@pytest.fixture
def student_token():
    """Token JWT pour un étudiant"""
    payload = {
        "sub": "student_user_id",
        "email": "student@presencepro.com",
        "role": "student",
        "permissions": ["read"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return auth_manager.create_access_token(payload)


def test_health_check(client):
    """Test du endpoint de santé"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "gateway-service"


def test_gateway_info(client):
    """Test des informations du gateway"""
    response = client.get("/gateway/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "gateway-service"
    assert "services" in data
    assert "public_routes" in data


def test_metrics_endpoint(client):
    """Test de l'endpoint des métriques"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "gateway_requests_total" in response.text


def test_public_route_access(client):
    """Test d'accès aux routes publiques sans authentification"""
    # Route de santé (publique)
    response = client.get("/health")
    assert response.status_code == 200


def test_protected_route_without_token(client):
    """Test d'accès à une route protégée sans token"""
    with patch('app.proxy.proxy_service.find_target_service') as mock_find:
        mock_find.return_value = "http://localhost:8002"
        
        response = client.get("/api/v1/users")
        assert response.status_code == 401


def test_protected_route_with_admin_token(client, admin_token):
    """Test d'accès à une route protégée avec token admin"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    with patch('app.proxy.proxy_service.proxy_request') as mock_proxy:
        mock_proxy.return_value = {"message": "success"}
        
        response = client.get("/api/v1/users", headers=headers)
        # Le mock devrait être appelé
        mock_proxy.assert_called_once()


def test_admin_only_route_with_teacher_token(client, teacher_token):
    """Test d'accès à une route admin avec token enseignant"""
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 403


def test_teacher_route_with_teacher_token(client, teacher_token):
    """Test d'accès à une route enseignant avec token enseignant"""
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    with patch('app.proxy.proxy_service.proxy_request') as mock_proxy:
        mock_proxy.return_value = {"message": "success"}
        
        response = client.get("/api/v1/attendance", headers=headers)
        mock_proxy.assert_called_once()


def test_invalid_token(client):
    """Test avec un token invalide"""
    headers = {"Authorization": "Bearer invalid_token"}
    
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 401


def test_expired_token(client):
    """Test avec un token expiré"""
    payload = {
        "sub": "user_id",
        "email": "user@test.com",
        "role": "admin",
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expiré
    }
    expired_token = auth_manager.create_access_token(payload)
    headers = {"Authorization": f"Bearer {expired_token}"}
    
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 401


def test_route_not_found(client):
    """Test pour une route qui n'existe pas"""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404


@patch('app.proxy.check_all_services_health')
def test_services_health_check(mock_health, client):
    """Test du check de santé des services"""
    mock_health.return_value = {
        "auth-service": {"healthy": True, "message": None, "url": "http://localhost:8001"},
        "user-service": {"healthy": False, "message": "Connection refused", "url": "http://localhost:8002"}
    }
    
    response = client.get("/health/services")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["healthy_services"] == 1
    assert data["total_services"] == 2


def test_cors_headers(client):
    """Test des headers CORS"""
    response = client.options("/health", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in response.headers


def test_security_headers(client):
    """Test des headers de sécurité"""
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"


def test_request_id_header(client):
    """Test de l'ajout de l'ID de requête"""
    response = client.get("/health")
    assert "X-Request-ID" in response.headers


class TestAuthManager:
    """Tests pour le gestionnaire d'authentification"""
    
    def test_create_and_verify_token(self):
        """Test de création et vérification de token"""
        payload = {
            "sub": "user_id",
            "email": "test@example.com",
            "role": "admin"
        }
        
        token = auth_manager.create_access_token(payload)
        assert isinstance(token, str)
        
        decoded = auth_manager.verify_token(token)
        assert decoded["sub"] == "user_id"
        assert decoded["email"] == "test@example.com"
        assert decoded["role"] == "admin"
    
    def test_extract_user_info(self):
        """Test d'extraction des informations utilisateur"""
        payload = {
            "sub": "user_id",
            "email": "test@example.com",
            "role": "admin",
            "permissions": ["read", "write"],
            "exp": datetime.utcnow().timestamp() + 3600
        }
        
        user_info = auth_manager.extract_user_info(payload)
        assert user_info["user_id"] == "user_id"
        assert user_info["email"] == "test@example.com"
        assert user_info["role"] == "admin"
        assert user_info["permissions"] == ["read", "write"]
    
    def test_check_token_expiry(self):
        """Test de vérification d'expiration"""
        # Token valide
        valid_payload = {"exp": datetime.utcnow().timestamp() + 3600}
        assert auth_manager.check_token_expiry(valid_payload) == True
        
        # Token expiré
        expired_payload = {"exp": datetime.utcnow().timestamp() - 3600}
        assert auth_manager.check_token_expiry(expired_payload) == False
        
        # Token sans expiration
        no_exp_payload = {}
        assert auth_manager.check_token_expiry(no_exp_payload) == False


if __name__ == "__main__":
    pytest.main([__file__])
