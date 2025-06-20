"""
Service de proxy pour rediriger les requêtes vers les microservices
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, Tuple
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import StreamingResponse
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings
from .auth import get_user_context

logger = structlog.get_logger()


class ProxyService:
    """Service de proxy pour rediriger les requêtes"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.service_timeout),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        self.service_routes = settings.service_routes
    
    async def close(self):
        """Fermer le client HTTP"""
        await self.client.aclose()
    
    def find_target_service(self, path: str) -> Optional[str]:
        """Trouver le service cible pour une route donnée"""
        for route_prefix, service_url in self.service_routes.items():
            if path.startswith(route_prefix):
                return service_url
        return None
    
    def build_target_url(self, service_url: str, path: str) -> str:
        """Construire l'URL cible pour le service"""
        # Supprimer le slash final du service_url s'il existe
        service_url = service_url.rstrip('/')
        # S'assurer que le path commence par /
        if not path.startswith('/'):
            path = '/' + path
        return f"{service_url}{path}"
    
    def prepare_headers(self, request: Request, user: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Préparer les headers pour la requête proxy"""
        headers = {}
        
        # Copier les headers importants de la requête originale
        important_headers = [
            "content-type", "content-length", "accept", "accept-encoding",
            "accept-language", "user-agent", "x-forwarded-for", "x-real-ip"
        ]
        
        for header_name in important_headers:
            if header_name in request.headers:
                headers[header_name] = request.headers[header_name]
        
        # Ajouter les informations utilisateur
        user_headers = get_user_context(user)
        headers.update(user_headers)
        
        # Ajouter des headers de traçabilité
        headers["X-Gateway-Request-ID"] = request.headers.get("x-request-id", "unknown")
        headers["X-Forwarded-Host"] = request.headers.get("host", "unknown")
        headers["X-Forwarded-Proto"] = "http"  # ou https selon votre configuration
        
        return headers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def make_request(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str],
        content: bytes = None,
        params: Dict[str, Any] = None
    ) -> httpx.Response:
        """Faire une requête HTTP avec retry automatique"""
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                content=content,
                params=params
            )
            return response
        except httpx.TimeoutException:
            logger.error("Service timeout", url=url, method=method)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Service temporairement indisponible"
            )
        except httpx.ConnectError:
            logger.error("Service connection error", url=url, method=method)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service indisponible"
            )
        except Exception as e:
            logger.error("Proxy request failed", url=url, method=method, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Erreur de communication avec le service"
            )
    
    async def proxy_request(
        self, 
        request: Request, 
        user: Optional[Dict[str, Any]] = None
    ) -> Response:
        """Proxifier une requête vers le service approprié"""
        
        # Trouver le service cible
        target_service = self.find_target_service(request.url.path)
        if not target_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service non trouvé"
            )
        
        # Construire l'URL cible
        target_url = self.build_target_url(target_service, request.url.path)
        
        # Préparer les headers
        headers = self.prepare_headers(request, user)
        
        # Lire le contenu de la requête
        content = await request.body()
        
        # Préparer les paramètres de requête
        params = dict(request.query_params)
        
        logger.info(
            "Proxying request",
            method=request.method,
            path=request.url.path,
            target_url=target_url,
            user_id=user.get("user_id") if user else None
        )
        
        try:
            # Faire la requête vers le service cible
            response = await self.make_request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=content,
                params=params
            )
            
            # Préparer la réponse
            response_headers = {}
            
            # Copier certains headers de la réponse
            headers_to_copy = [
                "content-type", "content-length", "cache-control",
                "expires", "last-modified", "etag"
            ]
            
            for header_name in headers_to_copy:
                if header_name in response.headers:
                    response_headers[header_name] = response.headers[header_name]
            
            # Ajouter des headers de traçabilité
            response_headers["X-Gateway-Service"] = target_service
            response_headers["X-Gateway-Response-Time"] = str(response.elapsed.total_seconds())
            
            # Retourner la réponse
            if response.headers.get("content-type", "").startswith("application/json"):
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type="application/json"
                )
            else:
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=response_headers
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected proxy error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur interne du gateway"
            )


# Instance globale du service proxy
proxy_service = ProxyService()


async def health_check_service(service_name: str, service_url: str) -> Tuple[str, bool, Optional[str]]:
    """Vérifier la santé d'un service"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{service_url}/health")
            is_healthy = response.status_code == 200
            message = response.text if not is_healthy else None
            return service_name, is_healthy, message
    except Exception as e:
        return service_name, False, str(e)


async def check_all_services_health() -> Dict[str, Dict[str, Any]]:
    """Vérifier la santé de tous les services"""
    services = {
        "auth-service": settings.auth_service_url,
        "user-service": settings.user_service_url,
        "course-service": settings.course_service_url,
        "face-recognition-service": settings.face_recognition_service_url,
        "attendance-service": settings.attendance_service_url,
        "justification-service": settings.justification_service_url,
        "messaging-service": settings.messaging_service_url,
        "notification-service": settings.notification_service_url,
        "statistics-service": settings.statistics_service_url,
    }
    
    # Vérifier tous les services en parallèle
    tasks = [
        health_check_service(name, url) 
        for name, url in services.items()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    health_status = {}
    for result in results:
        if isinstance(result, Exception):
            continue
        
        service_name, is_healthy, message = result
        health_status[service_name] = {
            "healthy": is_healthy,
            "message": message,
            "url": services[service_name]
        }
    
    return health_status
