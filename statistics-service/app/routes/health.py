"""
Routes de santé et d'information du service
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.core.database import (
    get_database, check_database_connection, check_redis_connection, 
    get_database_stats
)
from app.models.statistics import HealthCheck, LastCalculation # Assuming LastCalculation model for this
from app.core.config import settings
from typing import Optional # For type hinting

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

SERVICE_START_TIME = datetime.now(timezone.utc)

# Placeholder functions - these need proper implementation
def get_last_calculation_time(db: Session) -> Optional[datetime]:
    """Récupère l'heure de la dernière calculation de statistiques. À IMPLÉMENTER."""
    # last_calc = db.query(LastCalculation).order_by(LastCalculation.timestamp.desc()).first()
    # return last_calc.timestamp if last_calc else None
    logger.info("get_last_calculation_time appelée (simulation).")
    return datetime.now(timezone.utc) - timedelta(minutes=5) # Simulated time

def get_cache_hit_rate() -> float:
    """Calcule le taux de hit du cache. À IMPLÉMENTER."""
    # hits = redis_client.get("cache_hits") or 0
    # misses = redis_client.get("cache_misses") or 0
    # if (hits + misses) == 0: return 0.0
    # return hits / (hits + misses)
    logger.info("get_cache_hit_rate appelée (simulation).")
    return 0.75 # Simulated rate

CALCULATION_COUNTERS = {
    "student_stats": 0,
    "class_stats": 0,
    "global_stats": 0,
    "charts_generated": 0,
    "exports_created": 0,
}

def increment_calculation_count(calc_type: str):
    """Incrémente le compteur pour un type de calcul. Sera appelé par le service de statistiques."""
    if calc_type in CALCULATION_COUNTERS:
        CALCULATION_COUNTERS[calc_type] += 1

def get_calculation_count(calc_type: str) -> int:
    """Récupère le compteur pour un type de calcul."""
    logger.info(f"get_calculation_count pour {calc_type} appelée (simulation).")
    return CALCULATION_COUNTERS.get(calc_type, -1) # Return -1 if type unknown for some reason


@router.get("/")
async def root():
    """Page d'accueil du service"""
    return {
        "service": "statistics-service",
        "version": settings.service_version,
        "status": "running",
        "description": "Service de statistiques et d'analyse pour PresencePro",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "student_stats": "/stats/student/{id}",
            "class_stats": "/stats/class/{id}",
            "global_stats": "/stats/global",
            "charts": "/stats/charts/generate",
            "exports": "/stats/export"
        },
        "timestamp": datetime.now(timezone.utc)
    }


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_database)):
    """Vérification de santé du service"""
    try:
        # Vérifier la base de données
        db_healthy = check_database_connection()
        
        # Vérifier Redis
        redis_healthy = check_redis_connection()
        
        # Statistiques de base de données
        db_stats = get_database_stats()
        
        # Vérifier la taille du cache
        cache_size = 0
        if redis_healthy:
            try:
                from app.core.database import redis_client
                if redis_client:
                    cache_size = redis_client.dbsize()
            except:
                pass
        
        # État général
        is_healthy = db_healthy
        
        health_status = HealthCheck(
            service="statistics-service",
            status="healthy" if is_healthy else "unhealthy",
            timestamp=datetime.now(timezone.utc),
            database_connected=db_healthy,
            redis_connected=redis_healthy,
            cache_size=cache_size,
            last_calculation=get_last_calculation_time(db)
        )
        
        return health_status
        
    except Exception as e:
        logger.error(f"Erreur vérification santé: {e}")
        return HealthCheck(
            service="statistics-service",
            status="unhealthy",
            timestamp=datetime.now(timezone.utc),
            database_connected=False,
            redis_connected=False,
            cache_size=0,
            last_calculation=None
        )


@router.get("/info")
async def service_info(db: Session = Depends(get_database)):
    """Informations détaillées sur le service"""
    try:
        # Statistiques de base de données
        db_stats = get_database_stats()
        
        # Configuration du service
        service_config = {
            "database_type": "PostgreSQL" if "postgresql" in settings.database_url else "SQLite",
            "cache_enabled": settings.cache_enabled,
            "cache_ttl": settings.cache_ttl,
            "default_period_days": settings.default_period_days,
            "max_period_days": settings.max_period_days,
            "chart_formats": list(settings.available_charts.keys()),
            "export_formats": settings.export_formats,
            "aggregation_periods": settings.aggregation_periods
        }
        
        # Fonctionnalités disponibles
        features = {
            "statistics_calculation": True,
            "chart_generation": settings.features.get("chart_generation", True),
            "data_export": settings.features.get("data_export", True),
            "cache_system": settings.cache_enabled,
            "real_time_stats": settings.features.get("real_time_stats", True),
            "advanced_analytics": settings.features.get("advanced_analytics", True),
            "custom_reports": settings.features.get("custom_reports", True)
        }
        
        # Statistiques des types de données
        available_statistics = list(settings.available_stats.keys())
        available_chart_types = list(settings.available_charts.keys())
        
        info = {
            "service": {
                "name": settings.service_name,
                "version": settings.service_version,
                "port": settings.service_port,
                "debug": settings.debug
            },
            "database": {
                "type": service_config["database_type"],
                "stats": db_stats,
                "url_masked": settings.database_url.split("@")[-1] if "@" in settings.database_url else "local"
            },
            "cache": {
                "enabled": settings.cache_enabled,
                "type": "Redis" if settings.cache_enabled else "None",
                "ttl_seconds": settings.cache_ttl,
                "connected": check_redis_connection()
            },
            "configuration": service_config,
            "features": features,
            "capabilities": {
                "statistics_types": available_statistics,
                "chart_types": available_chart_types,
                "export_formats": settings.export_formats,
                "aggregation_periods": settings.aggregation_periods,
                "max_period_days": settings.max_period_days
            },
            "integration": {
                "auth_service": settings.auth_service_url,
                "user_service": settings.user_service_url,
                "course_service": settings.course_service_url,
                "attendance_service": settings.attendance_service_url,
                "justification_service": settings.justification_service_url
            },
            "performance": {
                "max_concurrent_requests": settings.max_concurrent_requests,
                "query_timeout_seconds": settings.query_timeout_seconds,
                "batch_size": settings.batch_size,
                "rate_limit_per_minute": settings.rate_limit_per_minute
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        return info
        
    except Exception as e:
        logger.error(f"Erreur récupération info service: {e}")
        return {
            "service": settings.service_name,
            "version": settings.service_version,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        }


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_database)):
    """Métriques du service pour monitoring"""
    try:
        # Statistiques de base de données
        db_stats = get_database_stats()
        
        # Métriques de cache
        cache_metrics = {
            "enabled": settings.cache_enabled,
            "connected": check_redis_connection(),
            "size": 0,
            "hit_rate": 0.0
        }
        
        if settings.cache_enabled and check_redis_connection():
            try:
                from app.core.database import redis_client
                if redis_client:
                    cache_metrics["size"] = redis_client.dbsize()
                    cache_metrics["hit_rate"] = get_cache_hit_rate()
            except:
                pass
        
        # Métriques de performance
        performance_metrics = {
            "database_response_time_ms": -1,  # TODO: Mesurer (nécessite instrumentation)
            "cache_response_time_ms": -1,     # TODO: Mesurer (nécessite instrumentation)
            "average_calculation_time_ms": -1, # TODO: Mesurer (nécessite instrumentation)
            "concurrent_requests": -1          # TODO: Compter (via ASGI server ou middleware)
        }
        
        current_uptime = (datetime.now(timezone.utc) - SERVICE_START_TIME).total_seconds()

        metrics = {
            "service_info": {
                "name": settings.service_name,
                "version": settings.service_version,
                "uptime_seconds": current_uptime,
                "status": "healthy" # Simplifié, pourrait dépendre d'autres facteurs
            },
            "database": db_stats,
            "cache": cache_metrics,
            "performance": performance_metrics,
            "requests": {
                "total": -1,           # TODO: Compter les requêtes (via middleware)
                "successful": -1,      # TODO: Compter les succès (via middleware)
                "failed": -1,          # TODO: Compter les échecs (via middleware)
                "rate_per_minute": -1  # TODO: Calculer le taux (via middleware)
            },
            "calculations": {
                "student_stats": get_calculation_count("student_stats"),
                "class_stats": get_calculation_count("class_stats"),
                "global_stats": get_calculation_count("global_stats"),
                "charts_generated": get_calculation_count("charts_generated"),
                "exports_created": get_calculation_count("exports_created")
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Erreur récupération métriques: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        }


@router.get("/status")
async def get_service_status():
    """Statut simple du service"""
    try:
        db_healthy = check_database_connection()
        redis_healthy = check_redis_connection()
        
        status = "healthy" if db_healthy else "unhealthy"
        
        return {
            "status": status,
            "database": "connected" if db_healthy else "disconnected",
            "cache": "connected" if redis_healthy else "disconnected",
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        }
