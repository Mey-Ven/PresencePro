"""
Système d'authentification et d'autorisation pour le service de cours
"""
import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.core.config import settings

# Schéma de sécurité Bearer Token
security = HTTPBearer()


class AuthService:
    """Service d'authentification avec le service auth externe"""
    
    def __init__(self):
        self.auth_service_url = settings.auth_service_url
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifier un token JWT auprès du service d'authentification"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_service_url}/verify-token",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            print(f"Erreur lors de la vérification du token: {e}")
            return None
    
    async def check_permission(self, token: str, required_role: str) -> bool:
        """Vérifier les permissions d'un utilisateur"""
        user_info = await self.verify_token(token)
        if not user_info:
            return False
        
        user_role = user_info.get("role", "").lower()
        required_role = required_role.lower()
        
        # Hiérarchie des rôles
        role_hierarchy = {
            "admin": 4,
            "teacher": 3,
            "parent": 2,
            "student": 1
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level


# Instance globale du service d'authentification
auth_service = AuthService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Récupérer l'utilisateur actuel à partir du token"""
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
    """Décorateur pour exiger un rôle minimum"""
    async def role_checker(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        token = credentials.credentials
        user_info = await auth_service.verify_token(token)

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré",
                headers={"WWW-Authenticate": "Bearer"},
            )

        has_permission = await auth_service.check_permission(token, required_role)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissions insuffisantes. Rôle requis: {required_role}",
            )

        return user_info

    return role_checker


# Dépendances pour les différents rôles
def require_admin():
    """Exiger le rôle admin"""
    return require_role("admin")


def require_teacher():
    """Exiger le rôle teacher ou supérieur"""
    return require_role("teacher")


def require_parent():
    """Exiger le rôle parent ou supérieur"""
    return require_role("parent")


def require_student():
    """Exiger le rôle student ou supérieur"""
    return require_role("student")


def get_user_id(user: Dict[str, Any]) -> str:
    """Extraire l'ID utilisateur des informations utilisateur"""
    return user.get("id", user.get("username", ""))
