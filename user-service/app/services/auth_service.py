"""
Service d'authentification pour communiquer avec le service auth
"""
import httpx
from typing import Optional, Dict, Any
from ..core.config import settings


class AuthService:
    """Service pour communiquer avec le service d'authentification"""
    
    def __init__(self):
        self.auth_url = settings.auth_service_url
        
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie un token JWT auprès du service d'authentification"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.auth_url}/verify-token",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None
    
    async def get_user_info(self, user_id: str, token: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un utilisateur"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.auth_url}/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None
    
    async def check_permission(self, token: str, required_role: str) -> bool:
        """Vérifie si l'utilisateur a les permissions requises"""
        user_info = await self.verify_token(token)
        if not user_info:
            return False
        
        user_role = user_info.get("role", "")
        
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
