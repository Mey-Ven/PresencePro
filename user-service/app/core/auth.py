"""
Utilitaires d'authentification et d'autorisation
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from ..services.auth_service import auth_service

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Récupère l'utilisateur actuel à partir du token JWT"""
    token = credentials.credentials
    user_info = await auth_service.verify_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info


def require_role(required_role: str):
    """Décorateur pour vérifier les rôles requis"""
    async def role_checker(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        token = credentials.credentials
        has_permission = await auth_service.check_permission(token, required_role)

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle {required_role} requis"
            )

        user_info = await auth_service.verify_token(token)
        return user_info

    return role_checker


# Dépendances pour les différents rôles
require_admin = require_role("admin")
require_teacher = require_role("teacher")
require_parent = require_role("parent")
