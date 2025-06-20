"""
Modèles Pydantic pour le Config Service
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ConfigRequest(BaseModel):
    """Modèle pour les requêtes de configuration"""
    config_data: Dict[str, Any] = Field(..., description="Données de configuration")
    encrypt_sensitive: bool = Field(default=True, description="Chiffrer les données sensibles")
    
    class Config:
        json_schema_extra = {
            "example": {
                "config_data": {
                    "host": "0.0.0.0",
                    "port": 8001,
                    "database_url": "sqlite:///./app.db",
                    "jwt_secret_key": "secret-key"
                },
                "encrypt_sensitive": True
            }
        }


class ConfigResponse(BaseModel):
    """Modèle pour les réponses de configuration"""
    service_name: str = Field(..., description="Nom du service")
    config_data: Dict[str, Any] = Field(..., description="Données de configuration")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Métadonnées de configuration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "auth-service",
                "config_data": {
                    "host": "0.0.0.0",
                    "port": 8001,
                    "database_url": "sqlite:///./auth.db"
                },
                "metadata": {
                    "updated_at": "2024-01-01T12:00:00",
                    "version": 1
                }
            }
        }


class ServiceListResponse(BaseModel):
    """Modèle pour la liste des services"""
    services: List[str] = Field(..., description="Liste des services")
    total_count: int = Field(..., description="Nombre total de services")
    
    class Config:
        json_schema_extra = {
            "example": {
                "services": ["auth-service", "user-service", "gateway-service"],
                "total_count": 3
            }
        }


class ConfigValidationRequest(BaseModel):
    """Modèle pour la validation de configuration"""
    service_name: str = Field(..., description="Nom du service")
    config_data: Dict[str, Any] = Field(..., description="Configuration à valider")
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "auth-service",
                "config_data": {
                    "host": "0.0.0.0",
                    "port": 8001
                }
            }
        }


class ConfigValidationResponse(BaseModel):
    """Modèle pour la réponse de validation"""
    is_valid: bool = Field(..., description="Configuration valide")
    errors: List[str] = Field(default=[], description="Liste des erreurs")
    warnings: List[str] = Field(default=[], description="Liste des avertissements")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "errors": [],
                "warnings": ["Port 8001 might conflict with other services"]
            }
        }


class ConfigBackupResponse(BaseModel):
    """Modèle pour la réponse de sauvegarde"""
    success: bool = Field(..., description="Sauvegarde réussie")
    backup_path: Optional[str] = Field(None, description="Chemin de la sauvegarde")
    timestamp: datetime = Field(..., description="Horodatage de la sauvegarde")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "backup_path": "./backups/auth-service_20240101_120000.json",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class ConfigDiffRequest(BaseModel):
    """Modèle pour comparer des configurations"""
    service_name: str = Field(..., description="Nom du service")
    config_a: Dict[str, Any] = Field(..., description="Première configuration")
    config_b: Dict[str, Any] = Field(..., description="Deuxième configuration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "auth-service",
                "config_a": {"port": 8001, "debug": False},
                "config_b": {"port": 8002, "debug": True}
            }
        }


class ConfigDiffResponse(BaseModel):
    """Modèle pour la réponse de comparaison"""
    added: Dict[str, Any] = Field(default={}, description="Clés ajoutées")
    removed: Dict[str, Any] = Field(default={}, description="Clés supprimées")
    modified: Dict[str, Dict[str, Any]] = Field(default={}, description="Clés modifiées")
    unchanged: Dict[str, Any] = Field(default={}, description="Clés inchangées")
    
    class Config:
        json_schema_extra = {
            "example": {
                "added": {},
                "removed": {},
                "modified": {
                    "port": {"old": 8001, "new": 8002},
                    "debug": {"old": False, "new": True}
                },
                "unchanged": {}
            }
        }


class HealthCheckResponse(BaseModel):
    """Modèle pour la réponse de santé"""
    status: str = Field(..., description="Statut du service")
    service: str = Field(..., description="Nom du service")
    version: str = Field(..., description="Version du service")
    storage_backend: str = Field(..., description="Backend de stockage utilisé")
    timestamp: datetime = Field(..., description="Horodatage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "config-service",
                "version": "1.0.0",
                "storage_backend": "file",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class ConfigTemplateResponse(BaseModel):
    """Modèle pour les templates de configuration"""
    service_name: str = Field(..., description="Nom du service")
    template: Dict[str, Any] = Field(..., description="Template de configuration")
    description: str = Field(..., description="Description du template")
    required_fields: List[str] = Field(..., description="Champs obligatoires")
    optional_fields: List[str] = Field(..., description="Champs optionnels")
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "auth-service",
                "template": {
                    "host": "0.0.0.0",
                    "port": 8001,
                    "database_url": "sqlite:///./auth.db"
                },
                "description": "Configuration pour le service d'authentification",
                "required_fields": ["host", "port"],
                "optional_fields": ["database_url"]
            }
        }


class ErrorResponse(BaseModel):
    """Modèle pour les réponses d'erreur"""
    error: str = Field(..., description="Message d'erreur")
    detail: Optional[str] = Field(None, description="Détails de l'erreur")
    timestamp: datetime = Field(..., description="Horodatage de l'erreur")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Service not found",
                "detail": "The service 'unknown-service' is not supported",
                "timestamp": "2024-01-01T12:00:00"
            }
        }
