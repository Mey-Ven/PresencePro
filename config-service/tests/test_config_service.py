"""
Tests pour le Config Service
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.config import settings
from app.security import security_manager


@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(app)


@pytest.fixture
def master_api_key():
    """Clé API maître pour les tests"""
    return settings.master_api_key


@pytest.fixture
def service_api_key():
    """Clé API de service pour les tests"""
    return "auth-key"  # Définie dans SERVICE_API_KEYS


@pytest.fixture
def sample_config():
    """Configuration d'exemple pour les tests"""
    return {
        "host": "0.0.0.0",
        "port": 8001,
        "database_url": "sqlite:///./test.db",
        "jwt_secret_key": "test-secret-key-123456",
        "jwt_algorithm": "HS256"
    }


def test_health_check(client):
    """Test du endpoint de santé"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "config-service"
    assert data["storage_backend"] == settings.config_storage_type


def test_list_services_without_api_key(client):
    """Test de la liste des services sans clé API"""
    response = client.get("/services")
    assert response.status_code == 401


def test_list_services_with_invalid_api_key(client):
    """Test de la liste des services avec clé API invalide"""
    headers = {settings.api_key_header: "invalid-key"}
    response = client.get("/services", headers=headers)
    assert response.status_code == 403


def test_list_services_with_valid_api_key(client, service_api_key):
    """Test de la liste des services avec clé API valide"""
    headers = {settings.api_key_header: service_api_key}
    
    with patch('app.storage.storage_backend.list_services') as mock_list:
        mock_list.return_value = ["auth-service", "user-service", "gateway-service"]
        
        response = client.get("/services", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert "total_count" in data
        assert data["total_count"] == 3


def test_get_config_without_api_key(client):
    """Test de récupération de config sans clé API"""
    response = client.get("/config/auth-service")
    assert response.status_code == 401


def test_get_config_for_unknown_service(client, service_api_key):
    """Test de récupération de config pour un service inconnu"""
    headers = {settings.api_key_header: service_api_key}
    response = client.get("/config/unknown-service", headers=headers)
    assert response.status_code == 404


def test_get_config_success(client, service_api_key, sample_config):
    """Test de récupération de config réussie"""
    headers = {settings.api_key_header: service_api_key}
    
    with patch('app.storage.storage_backend.get_config') as mock_get:
        mock_get.return_value = sample_config
        
        response = client.get("/config/auth-service", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["service_name"] == "auth-service"
        assert "config_data" in data


def test_set_config_without_master_key(client, service_api_key, sample_config):
    """Test de sauvegarde de config sans clé maître"""
    headers = {settings.api_key_header: service_api_key}
    payload = {"config_data": sample_config}
    
    response = client.put("/config/auth-service", headers=headers, json=payload)
    assert response.status_code == 403


def test_set_config_with_master_key(client, master_api_key, sample_config):
    """Test de sauvegarde de config avec clé maître"""
    headers = {settings.api_key_header: master_api_key}
    payload = {"config_data": sample_config}
    
    with patch('app.storage.storage_backend.set_config') as mock_set:
        mock_set.return_value = True
        
        response = client.put("/config/auth-service", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["service_name"] == "auth-service"


def test_set_config_validation_failure(client, master_api_key):
    """Test de sauvegarde avec validation échouée"""
    headers = {settings.api_key_header: master_api_key}
    invalid_config = {"port": "invalid_port"}  # Port doit être un entier
    payload = {"config_data": invalid_config}
    
    response = client.put("/config/auth-service", headers=headers, json=payload)
    assert response.status_code == 400


def test_delete_config_without_master_key(client, service_api_key):
    """Test de suppression de config sans clé maître"""
    headers = {settings.api_key_header: service_api_key}
    
    response = client.delete("/config/auth-service", headers=headers)
    assert response.status_code == 403


def test_delete_config_with_master_key(client, master_api_key):
    """Test de suppression de config avec clé maître"""
    headers = {settings.api_key_header: master_api_key}
    
    with patch('app.storage.storage_backend.delete_config') as mock_delete:
        mock_delete.return_value = True
        
        response = client.delete("/config/auth-service", headers=headers)
        assert response.status_code == 200


def test_validate_config(client, service_api_key, sample_config):
    """Test de validation de configuration"""
    headers = {settings.api_key_header: service_api_key}
    payload = {
        "service_name": "auth-service",
        "config_data": sample_config
    }
    
    response = client.post("/validate", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "is_valid" in data
    assert "errors" in data
    assert "warnings" in data


def test_get_config_template(client, service_api_key):
    """Test de récupération de template"""
    headers = {settings.api_key_header: service_api_key}
    
    response = client.get("/template/auth-service", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "auth-service"
    assert "template" in data
    assert "required_fields" in data
    assert "optional_fields" in data


def test_backup_config(client, master_api_key):
    """Test de sauvegarde de configuration"""
    headers = {settings.api_key_header: master_api_key}
    
    with patch('app.storage.storage_backend.backup_config') as mock_backup:
        mock_backup.return_value = True
        
        response = client.post("/backup/auth-service", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "timestamp" in data


def test_compare_configs(client, service_api_key):
    """Test de comparaison de configurations"""
    headers = {settings.api_key_header: service_api_key}
    payload = {
        "service_name": "auth-service",
        "config_a": {"port": 8001, "debug": False},
        "config_b": {"port": 8002, "debug": True, "new_field": "value"}
    }
    
    response = client.post("/diff", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "added" in data
    assert "removed" in data
    assert "modified" in data
    assert "unchanged" in data


def test_metrics_endpoint(client):
    """Test de l'endpoint des métriques"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "config_requests_total" in response.text


class TestSecurityManager:
    """Tests pour le gestionnaire de sécurité"""
    
    def test_encrypt_decrypt_data(self):
        """Test de chiffrement/déchiffrement"""
        original_data = "sensitive-password-123"
        
        encrypted = security_manager.encrypt_data(original_data)
        assert encrypted != original_data
        
        decrypted = security_manager.decrypt_data(encrypted)
        assert decrypted == original_data
    
    def test_encrypt_config(self):
        """Test de chiffrement de configuration"""
        config = {
            "host": "localhost",
            "password": "secret123",
            "jwt_secret_key": "jwt-secret",
            "normal_field": "value"
        }
        
        encrypted_config = security_manager.encrypt_config(config)
        
        # Les champs sensibles doivent être chiffrés
        assert encrypted_config["password"] != config["password"]
        assert encrypted_config["jwt_secret_key"] != config["jwt_secret_key"]
        assert encrypted_config["password_encrypted"] is True
        assert encrypted_config["jwt_secret_key_encrypted"] is True
        
        # Les champs normaux ne doivent pas être modifiés
        assert encrypted_config["host"] == config["host"]
        assert encrypted_config["normal_field"] == config["normal_field"]
    
    def test_verify_api_key(self):
        """Test de vérification de clé API"""
        # Clé maître
        assert security_manager.verify_api_key(settings.master_api_key) is True
        
        # Clé de service valide
        assert security_manager.verify_api_key("auth-key") is True
        
        # Clé invalide
        assert security_manager.verify_api_key("invalid-key") is False
    
    def test_get_service_from_api_key(self):
        """Test d'identification du service par clé API"""
        # Clé maître
        assert security_manager.get_service_from_api_key(settings.master_api_key) == "master"
        
        # Clé de service
        assert security_manager.get_service_from_api_key("auth-key") == "auth-service"
        
        # Clé inconnue
        assert security_manager.get_service_from_api_key("unknown-key") is None


if __name__ == "__main__":
    pytest.main([__file__])
