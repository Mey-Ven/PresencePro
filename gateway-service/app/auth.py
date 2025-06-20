"""
Gestion de l'authentification et autorisation
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from .config import settings

logger = structlog.get_logger()
security = HTTPBearer()


class AuthManager:
    """Gestionnaire d'authentification et d'autorisation"""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Créer un token JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Vérifier et décoder un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.InvalidTokenError as e:
            logger.error("JWT verification failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def extract_user_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extraire les informations utilisateur du payload JWT"""
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "permissions": payload.get("permissions", []),
            "exp": payload.get("exp")
        }
    
    def check_token_expiry(self, payload: Dict[str, Any]) -> bool:
        """Vérifier si le token a expiré"""
        exp = payload.get("exp")
        if exp is None:
            return False
        
        return datetime.utcnow().timestamp() < exp


# Instance globale
auth_manager = AuthManager()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Obtenir l'utilisateur actuel à partir du token JWT"""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    
    if not auth_manager.check_token_expiry(payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_info = auth_manager.extract_user_info(payload)
    
    if user_info["user_id"] is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info


async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """Obtenir l'utilisateur actuel de manière optionnelle (pour les routes publiques)"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = auth_manager.verify_token(token)
        
        if not auth_manager.check_token_expiry(payload):
            return None
        
        return auth_manager.extract_user_info(payload)
    except Exception:
        return None


def require_role(allowed_roles: List[str]):
    """Décorateur pour vérifier les rôles requis"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôles requis: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


def require_permission(required_permission: str):
    """Décorateur pour vérifier les permissions requises"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission requise: {required_permission}"
            )
        return current_user
    return permission_checker


# Dépendances pour les rôles spécifiques
require_admin = require_role(["admin"])
require_teacher_or_admin = require_role(["teacher", "admin"])
require_student_or_above = require_role(["student", "teacher", "admin"])


def check_route_access(path: str, method: str, user: Optional[Dict[str, Any]]) -> bool:
    """Vérifier l'accès à une route selon le rôle de l'utilisateur"""
    
    # Routes publiques
    if any(path.startswith(route) for route in settings.public_routes):
        return True
    
    # Si pas d'utilisateur pour une route protégée
    if user is None:
        return False
    
    user_role = user.get("role")
    
    # Admin a accès à tout
    if user_role == "admin":
        return True
    
    # Routes réservées aux admins
    if any(path.startswith(route) for route in settings.admin_only_routes):
        return user_role == "admin"
    
    # Routes accessibles aux enseignants
    if any(path.startswith(route) for route in settings.teacher_routes):
        return user_role in ["teacher", "admin"]
    
    # Routes générales (authentifiées)
    return user_role in ["student", "parent", "teacher", "admin"]


def get_user_context(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Obtenir le contexte utilisateur pour les headers de proxy"""
    if user is None:
        return {}
    
    return {
        "X-User-ID": str(user.get("user_id", "")),
        "X-User-Email": user.get("email", ""),
        "X-User-Role": user.get("role", ""),
        "X-User-Permissions": ",".join(user.get("permissions", [])),
    }
