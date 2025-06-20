"""
Middleware pour le Gateway Service
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import structlog
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge

from .config import settings

logger = structlog.get_logger()

# Métriques Prometheus
REQUEST_COUNT = Counter(
    'gateway_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'gateway_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'gateway_active_connections',
    'Number of active connections'
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour le logging des requêtes"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Générer un ID unique pour la requête
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Ajouter l'ID à l'en-tête
        if "x-request-id" not in request.headers:
            request.headers.__dict__["_list"].append(
                (b"x-request-id", request_id.encode())
            )
        
        start_time = time.time()
        
        # Logger la requête entrante
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        try:
            response = await call_next(request)
            
            # Calculer la durée
            duration = time.time() - start_time
            
            # Logger la réponse
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            # Ajouter l'ID de requête à la réponse
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration=duration
            )
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware pour les métriques Prometheus"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Incrémenter les connexions actives
        ACTIVE_CONNECTIONS.inc()
        
        try:
            response = await call_next(request)
            
            # Calculer la durée
            duration = time.time() - start_time
            
            # Enregistrer les métriques
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
            
        finally:
            # Décrémenter les connexions actives
            ACTIVE_CONNECTIONS.dec()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware pour le rate limiting"""
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client
        self.requests_per_minute = settings.rate_limit_requests_per_minute
        self.burst_limit = settings.rate_limit_burst
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Si Redis n'est pas disponible, passer sans rate limiting
        if not self.redis_client:
            return await call_next(request)
        
        # Identifier le client (IP + User-Agent pour plus de précision)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        client_id = f"{client_ip}:{hash(user_agent)}"
        
        # Clés Redis pour le rate limiting
        minute_key = f"rate_limit:minute:{client_id}:{int(time.time() // 60)}"
        burst_key = f"rate_limit:burst:{client_id}"
        
        try:
            # Vérifier le rate limiting par minute
            minute_count = await self.redis_client.incr(minute_key)
            if minute_count == 1:
                await self.redis_client.expire(minute_key, 60)
            
            if minute_count > self.requests_per_minute:
                logger.warning(
                    "Rate limit exceeded (minute)",
                    client_id=client_id,
                    count=minute_count,
                    limit=self.requests_per_minute
                )
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": "60"}
                )
            
            # Vérifier le burst limiting
            burst_count = await self.redis_client.incr(burst_key)
            if burst_count == 1:
                await self.redis_client.expire(burst_key, 10)  # Fenêtre de 10 secondes
            
            if burst_count > self.burst_limit:
                logger.warning(
                    "Rate limit exceeded (burst)",
                    client_id=client_id,
                    count=burst_count,
                    limit=self.burst_limit
                )
                return Response(
                    content="Rate limit exceeded (too many requests)",
                    status_code=429,
                    headers={"Retry-After": "10"}
                )
            
        except Exception as e:
            logger.error("Rate limiting error", error=str(e))
            # En cas d'erreur Redis, continuer sans rate limiting
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware pour ajouter des headers de sécurité"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Ajouter des headers de sécurité
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


async def setup_redis_client():
    """Configurer le client Redis pour le rate limiting"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        # Tester la connexion
        await redis_client.ping()
        logger.info("Redis connection established")
        return redis_client
    except Exception as e:
        logger.warning("Redis connection failed, rate limiting disabled", error=str(e))
        return None
