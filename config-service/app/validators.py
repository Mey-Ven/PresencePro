"""
Validateurs pour les configurations
"""
import re
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse
import structlog

from .config import settings

logger = structlog.get_logger()


class ConfigValidator:
    """Validateur de configurations pour les services"""
    
    def __init__(self):
        self.service_schemas = self._get_service_schemas()
    
    def _get_service_schemas(self) -> Dict[str, Dict]:
        """Définir les schémas de validation pour chaque service"""
        return {
            "auth-service": {
                "required": ["host", "port", "jwt_secret_key"],
                "optional": ["database_url", "jwt_algorithm", "jwt_access_token_expire_minutes"],
                "types": {
                    "host": str,
                    "port": int,
                    "jwt_secret_key": str,
                    "jwt_algorithm": str,
                    "jwt_access_token_expire_minutes": int
                },
                "constraints": {
                    "port": {"min": 1, "max": 65535},
                    "jwt_access_token_expire_minutes": {"min": 1, "max": 1440}
                }
            },
            "user-service": {
                "required": ["host", "port"],
                "optional": ["database_url", "auth_service_url", "max_file_size_mb"],
                "types": {
                    "host": str,
                    "port": int,
                    "database_url": str,
                    "auth_service_url": str,
                    "max_file_size_mb": int
                },
                "constraints": {
                    "port": {"min": 1, "max": 65535},
                    "max_file_size_mb": {"min": 1, "max": 100}
                }
            },
            "gateway-service": {
                "required": ["host", "port", "jwt_secret_key"],
                "optional": ["redis_url", "rate_limit_requests_per_minute", "cors_origins"],
                "types": {
                    "host": str,
                    "port": int,
                    "jwt_secret_key": str,
                    "redis_url": str,
                    "rate_limit_requests_per_minute": int,
                    "cors_origins": list
                },
                "constraints": {
                    "port": {"min": 1, "max": 65535},
                    "rate_limit_requests_per_minute": {"min": 1, "max": 10000}
                }
            },
            "config-service": {
                "required": ["host", "port"],
                "optional": ["config_storage_type", "config_base_path"],
                "types": {
                    "host": str,
                    "port": int,
                    "config_storage_type": str,
                    "config_base_path": str
                },
                "constraints": {
                    "port": {"min": 1, "max": 65535},
                    "config_storage_type": {"values": ["file", "consul", "redis"]}
                }
            }
        }
    
    def validate_config(self, service_name: str, config_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Valider une configuration de service
        
        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # Vérifier si le service est supporté
        if service_name not in settings.supported_services:
            errors.append(f"Service '{service_name}' is not supported")
            return False, errors, warnings
        
        # Obtenir le schéma de validation
        schema = self.service_schemas.get(service_name, {})
        
        if not schema:
            warnings.append(f"No validation schema defined for '{service_name}'")
            return True, errors, warnings
        
        # Vérifier les champs requis
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in config_data:
                errors.append(f"Required field '{field}' is missing")
        
        # Vérifier les types de données
        types = schema.get("types", {})
        for field, expected_type in types.items():
            if field in config_data:
                value = config_data[field]
                if not isinstance(value, expected_type):
                    errors.append(f"Field '{field}' should be of type {expected_type.__name__}, got {type(value).__name__}")
        
        # Vérifier les contraintes
        constraints = schema.get("constraints", {})
        for field, constraint in constraints.items():
            if field in config_data:
                value = config_data[field]
                
                # Contraintes numériques
                if "min" in constraint and value < constraint["min"]:
                    errors.append(f"Field '{field}' value {value} is below minimum {constraint['min']}")
                
                if "max" in constraint and value > constraint["max"]:
                    errors.append(f"Field '{field}' value {value} is above maximum {constraint['max']}")
                
                # Contraintes de valeurs
                if "values" in constraint and value not in constraint["values"]:
                    errors.append(f"Field '{field}' value '{value}' is not in allowed values: {constraint['values']}")
        
        # Validations spécifiques
        self._validate_urls(config_data, errors, warnings)
        self._validate_ports(config_data, errors, warnings)
        self._validate_security(config_data, errors, warnings)
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    def _validate_urls(self, config_data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Valider les URLs dans la configuration"""
        url_fields = [
            "database_url", "redis_url", "auth_service_url", 
            "notification_service_url", "face_recognition_service_url"
        ]
        
        for field in url_fields:
            if field in config_data:
                url = config_data[field]
                if isinstance(url, str):
                    try:
                        parsed = urlparse(url)
                        if not parsed.scheme:
                            errors.append(f"URL '{field}' is missing scheme (http/https/etc)")
                        if not parsed.netloc and parsed.scheme not in ['sqlite', 'file']:
                            errors.append(f"URL '{field}' is missing host")
                    except Exception:
                        errors.append(f"URL '{field}' is malformed")
    
    def _validate_ports(self, config_data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Valider les ports dans la configuration"""
        if "port" in config_data:
            port = config_data["port"]
            if isinstance(port, int):
                # Ports réservés
                if port < 1024:
                    warnings.append(f"Port {port} is in reserved range (< 1024)")
                
                # Ports communs qui pourraient entrer en conflit
                common_ports = {
                    80: "HTTP", 443: "HTTPS", 22: "SSH", 21: "FTP",
                    25: "SMTP", 53: "DNS", 3306: "MySQL", 5432: "PostgreSQL"
                }
                
                if port in common_ports:
                    warnings.append(f"Port {port} is commonly used for {common_ports[port]}")
    
    def _validate_security(self, config_data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Valider les aspects de sécurité"""
        # Vérifier les clés secrètes
        secret_fields = ["jwt_secret_key", "secret_key", "api_key", "encryption_key"]
        
        for field in secret_fields:
            if field in config_data:
                secret = config_data[field]
                if isinstance(secret, str):
                    if len(secret) < 16:
                        warnings.append(f"Secret '{field}' is too short (< 16 characters)")
                    
                    if secret in ["secret", "password", "key", "changeme", "default"]:
                        errors.append(f"Secret '{field}' uses a default/weak value")
                    
                    # Vérifier la complexité
                    if not re.search(r'[A-Za-z]', secret) or not re.search(r'[0-9]', secret):
                        warnings.append(f"Secret '{field}' should contain both letters and numbers")
        
        # Vérifier les mots de passe de base de données
        if "database_url" in config_data:
            db_url = config_data["database_url"]
            if isinstance(db_url, str) and "password" in db_url.lower():
                if "password@" in db_url or "password:" in db_url:
                    warnings.append("Database URL contains weak password")
    
    def get_config_template(self, service_name: str) -> Dict[str, Any]:
        """Obtenir un template de configuration pour un service"""
        if service_name not in settings.supported_services:
            return {}
        
        # Retourner la configuration par défaut comme template
        default_configs = settings.default_service_configs
        return default_configs.get(service_name, {})
    
    def get_required_fields(self, service_name: str) -> List[str]:
        """Obtenir les champs requis pour un service"""
        schema = self.service_schemas.get(service_name, {})
        return schema.get("required", [])
    
    def get_optional_fields(self, service_name: str) -> List[str]:
        """Obtenir les champs optionnels pour un service"""
        schema = self.service_schemas.get(service_name, {})
        return schema.get("optional", [])
    
    def compare_configs(self, config_a: Dict[str, Any], config_b: Dict[str, Any]) -> Dict[str, Any]:
        """Comparer deux configurations"""
        result = {
            "added": {},
            "removed": {},
            "modified": {},
            "unchanged": {}
        }
        
        all_keys = set(config_a.keys()) | set(config_b.keys())
        
        for key in all_keys:
            if key in config_a and key in config_b:
                if config_a[key] == config_b[key]:
                    result["unchanged"][key] = config_a[key]
                else:
                    result["modified"][key] = {
                        "old": config_a[key],
                        "new": config_b[key]
                    }
            elif key in config_a:
                result["removed"][key] = config_a[key]
            else:
                result["added"][key] = config_b[key]
        
        return result


# Instance globale du validateur
config_validator = ConfigValidator()
