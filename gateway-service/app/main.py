"""
Gateway Service - Point d'entrée unique pour PresencePro
"""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import structlog

from .config import settings
from .auth import get_optional_user, check_route_access
from .proxy import proxy_service, check_all_services_health
from .middleware import (
    LoggingMiddleware, 
    MetricsMiddleware, 
    RateLimitMiddleware, 
    SecurityHeadersMiddleware,
    setup_redis_client
)

# Configuration du logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    logger.info("Starting PresencePro Gateway Service")
    
    # Initialiser Redis pour le rate limiting
    redis_client = await setup_redis_client()
    app.state.redis_client = redis_client
    
    # Vérifier la santé des services au démarrage
    try:
        health_status = await check_all_services_health()
        healthy_services = sum(1 for status in health_status.values() if status["healthy"])
        total_services = len(health_status)
        
        logger.info(
            "Services health check completed",
            healthy_services=healthy_services,
            total_services=total_services,
            health_status=health_status
        )
    except Exception as e:
        logger.error("Failed to check services health", error=str(e))
    
    yield
    
    # Nettoyage
    logger.info("Shutting down PresencePro Gateway Service")
    await proxy_service.close()
    
    if redis_client:
        await redis_client.close()


# Créer l'application FastAPI
app = FastAPI(
    title="PresencePro Gateway Service",
    description="Point d'entrée unique pour tous les microservices PresencePro",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajouter les middlewares dans l'ordre approprié
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)


@app.on_event("startup")
async def startup_event():
    """Événement de démarrage"""
    # Ajouter le middleware de rate limiting avec Redis
    if hasattr(app.state, 'redis_client') and app.state.redis_client:
        app.add_middleware(RateLimitMiddleware, redis_client=app.state.redis_client)


@app.get("/health")
async def health_check():
    """Endpoint de santé du gateway"""
    return {
        "status": "healthy",
        "service": "gateway-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health/services")
async def services_health_check():
    """Vérifier la santé de tous les services"""
    try:
        health_status = await check_all_services_health()
        
        # Calculer le statut global
        healthy_count = sum(1 for status in health_status.values() if status["healthy"])
        total_count = len(health_status)
        
        overall_status = "healthy" if healthy_count == total_count else "degraded"
        if healthy_count == 0:
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "healthy_services": healthy_count,
            "total_services": total_count,
            "services": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to check services health",
                "error": str(e)
            }
        )


@app.get("/metrics")
async def metrics():
    """Endpoint pour les métriques Prometheus"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/gateway/info")
async def gateway_info():
    """Informations sur le gateway"""
    return {
        "service": "gateway-service",
        "version": "1.0.0",
        "environment": settings.environment,
        "services": list(settings.service_routes.keys()),
        "public_routes": settings.public_routes,
        "admin_routes": settings.admin_only_routes,
        "teacher_routes": settings.teacher_routes
    }


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_handler(request: Request, path: str):
    """Handler principal pour proxifier toutes les requêtes"""
    
    # Obtenir l'utilisateur actuel (optionnel)
    user = await get_optional_user(request)
    
    # Vérifier l'accès à la route
    full_path = f"/{path}"
    if not check_route_access(full_path, request.method, user):
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentification requise",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé pour votre rôle"
            )
    
    # Proxifier la requête
    try:
        return await proxy_service.proxy_request(request, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Proxy handler error", path=path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du gateway"
        )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler pour les routes non trouvées"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Route non trouvée",
            "path": request.url.path,
            "method": request.method
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handler pour les erreurs internes"""
    logger.error("Internal server error", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erreur interne du serveur",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.gateway_host,
        port=settings.gateway_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
