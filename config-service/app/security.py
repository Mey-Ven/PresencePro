"""
Gestion de la sécurité et du chiffrement
"""
import base64
import hashlib
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi import HTTPException, status, Depends, Request
import structlog

from .config import settings

logger = structlog.get_logger()


class SecurityManager:
    """Gestionnaire de sécurité pour le chiffrement et l'authentification"""
    
    def __init__(self):
        self.encryption_key = self._derive_key(settings.config_encryption_key)
        self.cipher_suite = Fernet(self.encryption_key)
        self.service_api_keys = settings.service_api_keys_dict
        self.master_api_key = settings.master_api_key
    
    def _derive_key(self, password: str) -> bytes:
        """Dériver une clé de chiffrement à partir d'un mot de passe"""
        password_bytes = password.encode()
        salt = b'presencepro_config_salt'  # En production, utiliser un salt aléatoire
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Chiffrer des données sensibles"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error("Encryption failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur de chiffrement"
            )
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Déchiffrer des données"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur de déchiffrement"
            )
    
    def encrypt_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Chiffrer les données sensibles dans une configuration"""
        sensitive_keys = [
            'password', 'secret', 'key', 'token', 'api_key',
            'database_url', 'smtp_password', 'jwt_secret_key'
        ]
        
        encrypted_config = config_data.copy()
        
        for key, value in config_data.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                if isinstance(value, str) and value:
                    encrypted_config[key] = self.encrypt_data(value)
                    encrypted_config[f"{key}_encrypted"] = True
        
        return encrypted_config
    
    def decrypt_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Déchiffrer les données sensibles dans une configuration"""
        decrypted_config = config_data.copy()
        
        for key, value in config_data.items():
            if key.endswith('_encrypted') and value is True:
                original_key = key.replace('_encrypted', '')
                if original_key in config_data:
                    try:
                        decrypted_config[original_key] = self.decrypt_data(config_data[original_key])
                        del decrypted_config[key]  # Supprimer le flag de chiffrement
                    except Exception as e:
                        logger.warning(f"Failed to decrypt {original_key}", error=str(e))
        
        return decrypted_config
    
    def verify_api_key(self, api_key: str, service_name: Optional[str] = None) -> bool:
        """Vérifier une clé API"""
        # Vérifier la clé maître
        if api_key == self.master_api_key:
            return True
        
        # Vérifier les clés de service spécifiques
        if service_name and service_name in self.service_api_keys:
            return api_key == self.service_api_keys[service_name]
        
        # Vérifier si la clé correspond à n'importe quel service
        return api_key in self.service_api_keys.values()
    
    def get_service_from_api_key(self, api_key: str) -> Optional[str]:
        """Obtenir le nom du service à partir de sa clé API"""
        if api_key == self.master_api_key:
            return "master"
        
        for service, key in self.service_api_keys.items():
            if api_key == key:
                return service
        
        return None
    
    def hash_data(self, data: str) -> str:
        """Créer un hash des données pour la vérification d'intégrité"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self, data: str, expected_hash: str) -> bool:
        """Vérifier l'intégrité des données avec un hash"""
        return self.hash_data(data) == expected_hash


# Instance globale
security_manager = SecurityManager()


async def verify_api_key(request: Request) -> str:
    """Middleware pour vérifier la clé API"""
    api_key = request.headers.get(settings.api_key_header)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante",
            headers={settings.api_key_header: "Required"}
        )
    
    if not security_manager.verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API invalide"
        )
    
    # Ajouter le service identifié à la requête
    service_name = security_manager.get_service_from_api_key(api_key)
    request.state.service_name = service_name
    
    logger.info(
        "API key verified",
        service=service_name,
        endpoint=request.url.path
    )
    
    return service_name


async def verify_master_key(request: Request) -> str:
    """Middleware pour vérifier la clé maître (admin uniquement)"""
    api_key = request.headers.get(settings.api_key_header)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante"
        )
    
    if api_key != security_manager.master_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur requis"
        )
    
    request.state.service_name = "master"
    return "master"


def mask_sensitive_data(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Masquer les données sensibles pour les logs"""
    sensitive_keys = [
        'password', 'secret', 'key', 'token', 'api_key',
        'database_url', 'smtp_password', 'jwt_secret_key'
    ]
    
    masked_config = config_data.copy()
    
    for key, value in config_data.items():
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            if isinstance(value, str) and len(value) > 4:
                masked_config[key] = value[:2] + "*" * (len(value) - 4) + value[-2:]
            else:
                masked_config[key] = "***"
    
    return masked_config
