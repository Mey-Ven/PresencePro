"""
Service d'authentification JWT pour le messaging service
"""
import jwt
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.core.config import settings
from app.models.message import UserRole

logger = logging.getLogger(__name__)

# Schéma de sécurité
security = HTTPBearer()


class AuthService:
    """Service d'authentification"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.auth_service_url = settings.auth_service_url
        self.user_service_url = settings.user_service_url
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Créer un token JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifier un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Vérifier l'expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return None
            
            return payload
            
        except jwt.PyJWTError as e:
            logger.warning(f"Erreur vérification token: {e}")
            return None
    
    async def verify_token_with_auth_service(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifier un token avec le service d'authentification"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_service_url}/api/v1/auth/verify-token",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Token invalide selon auth-service: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur vérification token avec auth-service: {e}")
            # Fallback sur la vérification locale
            return self.verify_token(token)
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un utilisateur"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.user_service_url}/api/v1/users/{user_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Utilisateur {user_id} non trouvé")
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur récupération utilisateur: {e}")
            return None
    
    async def authenticate_user(self, credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """Authentifier un utilisateur avec ses credentials"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token d'authentification requis"
            )
        
        # Vérifier le token
        payload = await self.verify_token_with_auth_service(credentials.credentials)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré"
            )
        
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide: user_id manquant"
            )
        
        # Récupérer les informations utilisateur
        user_info = await self.get_user_info(user_id)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé"
            )
        
        return {
            "user_id": user_id,
            "username": user_info.get("username", user_id),
            "display_name": user_info.get("display_name", user_info.get("username", user_id)),
            "role": user_info.get("role", "student"),
            "email": user_info.get("email"),
            "avatar_url": user_info.get("avatar_url")
        }
    
    async def authenticate_websocket_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Authentifier un token pour WebSocket"""
        try:
            # Vérifier le token
            payload = await self.verify_token_with_auth_service(token)
            
            if not payload:
                return None
            
            user_id = payload.get("sub") or payload.get("user_id")
            if not user_id:
                return None
            
            # Récupérer les informations utilisateur
            user_info = await self.get_user_info(user_id)
            if not user_info:
                return None
            
            return {
                "user_id": user_id,
                "username": user_info.get("username", user_id),
                "display_name": user_info.get("display_name", user_info.get("username", user_id)),
                "role": user_info.get("role", "student"),
                "email": user_info.get("email"),
                "avatar_url": user_info.get("avatar_url")
            }
            
        except Exception as e:
            logger.error(f"Erreur authentification WebSocket: {e}")
            return None
    
    def check_permission(self, user_role: str, required_roles: list) -> bool:
        """Vérifier les permissions d'un utilisateur"""
        if not required_roles:
            return True
        
        # Hiérarchie des rôles
        role_hierarchy = {
            "student": 1,
            "parent": 2,
            "teacher": 3,
            "admin": 4
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = min(role_hierarchy.get(role, 5) for role in required_roles)
        
        return user_level >= required_level
    
    def can_message_user(self, sender_role: str, recipient_role: str) -> bool:
        """Vérifier si un utilisateur peut envoyer un message à un autre"""
        # Règles de messagerie
        messaging_rules = {
            "student": ["parent", "teacher", "admin"],  # Étudiants peuvent écrire aux parents, profs, admins
            "parent": ["student", "teacher", "admin"],  # Parents peuvent écrire aux étudiants, profs, admins
            "teacher": ["student", "parent", "teacher", "admin"],  # Profs peuvent écrire à tous
            "admin": ["student", "parent", "teacher", "admin"]  # Admins peuvent écrire à tous
        }
        
        allowed_recipients = messaging_rules.get(sender_role, [])
        return recipient_role in allowed_recipients
    
    async def get_user_conversations_permissions(self, user_id: str, user_role: str) -> Dict[str, Any]:
        """Récupérer les permissions de conversation d'un utilisateur"""
        permissions = {
            "can_create_conversations": True,
            "can_create_group_conversations": user_role in ["teacher", "admin"],
            "can_moderate_conversations": user_role in ["teacher", "admin"],
            "can_delete_messages": user_role in ["admin"],
            "max_participants_per_conversation": 10 if user_role in ["teacher", "admin"] else 2,
            "allowed_recipient_roles": []
        }
        
        # Définir les rôles autorisés selon le rôle de l'utilisateur
        if user_role == "student":
            permissions["allowed_recipient_roles"] = ["parent", "teacher", "admin"]
        elif user_role == "parent":
            permissions["allowed_recipient_roles"] = ["student", "teacher", "admin"]
        elif user_role == "teacher":
            permissions["allowed_recipient_roles"] = ["student", "parent", "teacher", "admin"]
        elif user_role == "admin":
            permissions["allowed_recipient_roles"] = ["student", "parent", "teacher", "admin"]
        
        return permissions


# Instance globale du service d'authentification
auth_service = AuthService()


# Dépendances FastAPI

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dépendance pour obtenir l'utilisateur actuel"""
    return await auth_service.authenticate_user(credentials)


async def get_current_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dépendance pour vérifier que l'utilisateur est admin"""
    if current_user["role"] not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions administrateur requises"
        )
    return current_user


async def get_current_teacher_or_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dépendance pour vérifier que l'utilisateur est enseignant ou admin"""
    if current_user["role"] not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions enseignant ou administrateur requises"
        )
    return current_user
