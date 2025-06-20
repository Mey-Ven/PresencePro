"""
Config Service - Service de gestion centralisée des configurations PresencePro
"""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
import structlog

from .config import settings
from .models import (
    ConfigRequest, ConfigResponse, ServiceListResponse,
    ConfigValidationRequest, ConfigValidationResponse,
    ConfigBackupResponse, ConfigDiffRequest, ConfigDiffResponse,
    HealthCheckResponse, ConfigTemplateResponse, ErrorResponse
)
from .storage import storage_backend
from .security import verify_api_key, verify_master_key, mask_sensitive_data
from .validators import config_validator

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

# Métriques Prometheus
CONFIG_REQUESTS = Counter(
    'config_requests_total',
    'Total number of config requests',
    ['service_name', 'operation', 'status']
)

CONFIG_REQUEST_DURATION = Histogram(
    'config_request_duration_seconds',
    'Config request duration in seconds',
    ['service_name', 'operation']
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    logger.info("Starting PresencePro Config Service")
    
    # Initialiser le stockage
    try:
        services = await storage_backend.list_services()
        logger.info(f"Config service started with {len(services)} services", services=services)
    except Exception as e:
        logger.error("Failed to initialize storage backend", error=str(e))
    
    yield
    
    logger.info("Shutting down PresencePro Config Service")


# Créer l'application FastAPI
app = FastAPI(
    title="PresencePro Config Service",
    description="Service de gestion centralisée des configurations pour tous les microservices PresencePro",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, restreindre aux domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Endpoint de santé du service"""
    return HealthCheckResponse(
        status="healthy",
        service="config-service",
        version="1.0.0",
        storage_backend=settings.config_storage_type,
        timestamp=datetime.utcnow()
    )


@app.get("/metrics")
async def metrics():
    """Endpoint pour les métriques Prometheus"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/services", response_model=ServiceListResponse)
async def list_services(service_name: str = Depends(verify_api_key)):
    """Lister tous les services avec des configurations"""
    try:
        with CONFIG_REQUEST_DURATION.labels(service_name=service_name, operation="list").time():
            services = await storage_backend.list_services()
            
            CONFIG_REQUESTS.labels(
                service_name=service_name,
                operation="list",
                status="success"
            ).inc()
            
            logger.info("Services listed", requester=service_name, count=len(services))
            
            return ServiceListResponse(
                services=services,
                total_count=len(services)
            )
    
    except Exception as e:
        CONFIG_REQUESTS.labels(
            service_name=service_name,
            operation="list",
            status="error"
        ).inc()
        
        logger.error("Failed to list services", requester=service_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list services"
        )


@app.get("/config/{target_service}", response_model=ConfigResponse)
async def get_config(target_service: str, service_name: str = Depends(verify_api_key)):
    """Récupérer la configuration d'un service"""
    try:
        with CONFIG_REQUEST_DURATION.labels(service_name=service_name, operation="get").time():
            # Vérifier si le service cible est supporté
            if target_service not in settings.supported_services:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service '{target_service}' not found"
                )
            
            config_data = await storage_backend.get_config(target_service)
            
            if config_data is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Configuration for '{target_service}' not found"
                )
            
            # Extraire les métadonnées
            metadata = config_data.pop('_metadata', None)
            
            CONFIG_REQUESTS.labels(
                service_name=service_name,
                operation="get",
                status="success"
            ).inc()
            
            logger.info(
                "Config retrieved",
                requester=service_name,
                target_service=target_service,
                config_keys=list(config_data.keys())
            )
            
            return ConfigResponse(
                service_name=target_service,
                config_data=config_data,
                metadata=metadata
            )
    
    except HTTPException:
        CONFIG_REQUESTS.labels(
            service_name=service_name,
            operation="get",
            status="not_found"
        ).inc()
        raise
    
    except Exception as e:
        CONFIG_REQUESTS.labels(
            service_name=service_name,
            operation="get",
            status="error"
        ).inc()
        
        logger.error(
            "Failed to get config",
            requester=service_name,
            target_service=target_service,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve configuration"
        )


@app.put("/config/{target_service}", response_model=ConfigResponse)
async def set_config(
    target_service: str,
    config_request: ConfigRequest,
    service_name: str = Depends(verify_master_key)
):
    """Sauvegarder la configuration d'un service (admin uniquement)"""
    try:
        with CONFIG_REQUEST_DURATION.labels(service_name=service_name, operation="set").time():
            # Vérifier si le service cible est supporté
            if target_service not in settings.supported_services:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service '{target_service}' not found"
                )
            
            # Valider la configuration
            is_valid, errors, warnings = config_validator.validate_config(
                target_service, 
                config_request.config_data
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Configuration validation failed: {', '.join(errors)}"
                )
            
            # Sauvegarder la configuration
            success = await storage_backend.set_config(target_service, config_request.config_data)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save configuration"
                )
            
            CONFIG_REQUESTS.labels(
                service_name=service_name,
                operation="set",
                status="success"
            ).inc()
            
            logger.info(
                "Config saved",
                requester=service_name,
                target_service=target_service,
                config_keys=list(config_request.config_data.keys()),
                warnings=warnings
            )
            
            return ConfigResponse(
                service_name=target_service,
                config_data=config_request.config_data,
                metadata={
                    "updated_at": datetime.utcnow().isoformat(),
                    "updated_by": service_name,
                    "warnings": warnings
                }
            )
    
    except HTTPException:
        CONFIG_REQUESTS.labels(
            service_name=service_name,
            operation="set",
            status="validation_error"
        ).inc()
        raise
    
    except Exception as e:
        CONFIG_REQUESTS.labels(
            service_name=service_name,
            operation="set",
            status="error"
        ).inc()
        
        logger.error(
            "Failed to set config",
            requester=service_name,
            target_service=target_service,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save configuration"
        )


@app.delete("/config/{target_service}")
async def delete_config(target_service: str, service_name: str = Depends(verify_master_key)):
    """Supprimer la configuration d'un service (admin uniquement)"""
    try:
        with CONFIG_REQUEST_DURATION.labels(service_name=service_name, operation="delete").time():
            if target_service not in settings.supported_services:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service '{target_service}' not found"
                )
            
            success = await storage_backend.delete_config(target_service)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Configuration for '{target_service}' not found"
                )
            
            CONFIG_REQUESTS.labels(
                service_name=service_name,
                operation="delete",
                status="success"
            ).inc()
            
            logger.info(
                "Config deleted",
                requester=service_name,
                target_service=target_service
            )
            
            return {"message": f"Configuration for '{target_service}' deleted successfully"}
    
    except HTTPException:
        CONFIG_REQUESTS.labels(
            service_name=service_name,
            operation="delete",
            status="not_found"
        ).inc()
        raise
    
    except Exception as e:
        CONFIG_REQUESTS.labels(
            service_name=service_name,
            operation="delete",
            status="error"
        ).inc()
        
        logger.error(
            "Failed to delete config",
            requester=service_name,
            target_service=target_service,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete configuration"
        )


@app.post("/validate", response_model=ConfigValidationResponse)
async def validate_config(
    validation_request: ConfigValidationRequest,
    service_name: str = Depends(verify_api_key)
):
    """Valider une configuration sans la sauvegarder"""
    try:
        is_valid, errors, warnings = config_validator.validate_config(
            validation_request.service_name,
            validation_request.config_data
        )

        logger.info(
            "Config validated",
            requester=service_name,
            target_service=validation_request.service_name,
            is_valid=is_valid,
            errors_count=len(errors),
            warnings_count=len(warnings)
        )

        return ConfigValidationResponse(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )

    except Exception as e:
        logger.error(
            "Failed to validate config",
            requester=service_name,
            target_service=validation_request.service_name,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate configuration"
        )


@app.get("/template/{target_service}", response_model=ConfigTemplateResponse)
async def get_config_template(target_service: str, service_name: str = Depends(verify_api_key)):
    """Obtenir un template de configuration pour un service"""
    try:
        if target_service not in settings.supported_services:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{target_service}' not found"
            )

        template = config_validator.get_config_template(target_service)
        required_fields = config_validator.get_required_fields(target_service)
        optional_fields = config_validator.get_optional_fields(target_service)

        logger.info(
            "Template retrieved",
            requester=service_name,
            target_service=target_service
        )

        return ConfigTemplateResponse(
            service_name=target_service,
            template=template,
            description=f"Configuration template for {target_service}",
            required_fields=required_fields,
            optional_fields=optional_fields
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Failed to get template",
            requester=service_name,
            target_service=target_service,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve template"
        )


@app.post("/backup/{target_service}", response_model=ConfigBackupResponse)
async def backup_config(target_service: str, service_name: str = Depends(verify_master_key)):
    """Créer une sauvegarde de la configuration d'un service"""
    try:
        if target_service not in settings.supported_services:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{target_service}' not found"
            )

        success = await storage_backend.backup_config(target_service)
        timestamp = datetime.utcnow()

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create backup"
            )

        backup_path = None
        if settings.config_storage_type == "file":
            backup_path = f"{settings.backup_path}/{target_service}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        logger.info(
            "Config backup created",
            requester=service_name,
            target_service=target_service,
            backup_path=backup_path
        )

        return ConfigBackupResponse(
            success=success,
            backup_path=backup_path,
            timestamp=timestamp
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Failed to backup config",
            requester=service_name,
            target_service=target_service,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create backup"
        )


@app.post("/diff", response_model=ConfigDiffResponse)
async def compare_configs(
    diff_request: ConfigDiffRequest,
    service_name: str = Depends(verify_api_key)
):
    """Comparer deux configurations"""
    try:
        diff_result = config_validator.compare_configs(
            diff_request.config_a,
            diff_request.config_b
        )

        logger.info(
            "Config comparison completed",
            requester=service_name,
            target_service=diff_request.service_name,
            changes_count=len(diff_result["added"]) + len(diff_result["removed"]) + len(diff_result["modified"])
        )

        return ConfigDiffResponse(**diff_result)

    except Exception as e:
        logger.error(
            "Failed to compare configs",
            requester=service_name,
            target_service=diff_request.service_name,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare configurations"
        )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler pour les routes non trouvées"""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Route not found",
            detail=f"The requested endpoint {request.url.path} was not found",
            timestamp=datetime.utcnow()
        ).dict()
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handler pour les erreurs internes"""
    logger.error("Internal server error", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred",
            timestamp=datetime.utcnow()
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.config_host,
        port=settings.config_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
