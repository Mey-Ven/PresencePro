"""
Routes de santé et d'information du service
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging
from datetime import datetime, timezone

from app.core.config import settings
from app.core.database import ping_database, get_database_stats
from app.services.auth_service import get_current_admin
from app.websockets.connection_manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health & Info"])


@router.get("/health")
async def health_check():
    """
    Vérification de santé du service de messagerie
    
    Retourne l'état de santé du service et de ses dépendances
    """
    try:
        # Vérifier la base de données
        db_healthy = await ping_database()
        
        # Vérifier les statistiques de base
        db_stats = await get_database_stats()
        
        # Statistiques WebSocket
        ws_stats = connection_manager.get_connection_stats()
        
        # État général
        is_healthy = db_healthy
        
        health_status = {
            "service": "messaging-service",
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now(timezone.utc),
            "version": settings.service_version,
            "checks": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "details": {
                        "connected": db_healthy,
                        "messages_count": db_stats.get("messages_count", 0),
                        "conversations_count": db_stats.get("conversations_count", 0),
                        "users_count": db_stats.get("users_count", 0)
                    }
                },
                "websocket": {
                    "status": "healthy",
                    "details": ws_stats
                }
            },
            "uptime_seconds": 0,  # TODO: Calculer le temps de fonctionnement
            "memory_usage": "N/A"  # TODO: Ajouter les métriques de mémoire
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Erreur vérification santé: {e}")
        return {
            "service": "messaging-service",
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc),
            "error": str(e)
        }


@router.get("/info")
async def service_info():
    """
    Informations détaillées sur le service de messagerie
    """
    try:
        # Statistiques de base de données
        db_stats = await get_database_stats()
        
        # Statistiques WebSocket
        ws_stats = connection_manager.get_connection_stats()
        
        # Configuration du service
        service_config = {
            "max_message_length": settings.max_message_length,
            "max_messages_per_conversation": settings.max_messages_per_conversation,
            "message_retention_days": settings.message_retention_days,
            "websocket_ping_interval": settings.websocket_ping_interval,
            "max_connections_per_user": settings.max_connections_per_user,
            "rate_limit_messages_per_minute": settings.rate_limit_messages_per_minute,
            "max_file_size": f"{settings.max_file_size / 1024 / 1024:.1f} MB",
            "allowed_file_types": settings.allowed_file_types
        }
        
        # Vérifier la connectivité avec les autres services
        external_services = await check_external_services()
        
        info = {
            "service": {
                "name": settings.service_name,
                "version": settings.service_version,
                "port": settings.service_port,
                "debug": settings.debug
            },
            "database": {
                "type": "MongoDB",
                "database_name": db_stats.get("database_name", settings.mongodb_database),
                "collections": db_stats.get("collections", 0),
                "total_messages": db_stats.get("messages_count", 0),
                "total_conversations": db_stats.get("conversations_count", 0),
                "total_users": db_stats.get("users_count", 0),
                "data_size_mb": round(db_stats.get("data_size", 0) / 1024 / 1024, 2),
                "storage_size_mb": round(db_stats.get("storage_size", 0) / 1024 / 1024, 2)
            },
            "websocket": {
                "total_connections": ws_stats["total_connections"],
                "authenticated_connections": ws_stats["authenticated_connections"],
                "users_online": ws_stats["users_online"],
                "active_conversations": ws_stats["active_conversations"],
                "typing_users": ws_stats["typing_users"]
            },
            "configuration": service_config,
            "external_services": external_services,
            "features": {
                "real_time_messaging": True,
                "message_history": True,
                "typing_indicators": True,
                "read_receipts": True,
                "file_attachments": False,  # TODO: Implémenter
                "group_conversations": True,
                "message_search": False,  # TODO: Implémenter
                "message_encryption": False  # TODO: Implémenter
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


@router.get("/admin/stats")
async def admin_stats(
    current_user: Dict[str, Any] = Depends(get_current_admin)
):
    """
    Statistiques détaillées pour les administrateurs
    """
    try:
        # Statistiques de base de données
        db_stats = await get_database_stats()
        
        # Statistiques WebSocket
        ws_stats = connection_manager.get_connection_stats()
        
        # TODO: Ajouter plus de statistiques détaillées
        # - Messages par jour/semaine/mois
        # - Utilisateurs les plus actifs
        # - Conversations les plus actives
        # - Temps de réponse moyen
        
        admin_stats = {
            "database": db_stats,
            "websocket": ws_stats,
            "performance": {
                "average_response_time_ms": 0,  # TODO: Implémenter
                "messages_per_minute": 0,  # TODO: Implémenter
                "peak_concurrent_users": 0  # TODO: Implémenter
            },
            "usage": {
                "daily_active_users": 0,  # TODO: Implémenter
                "weekly_active_users": 0,  # TODO: Implémenter
                "monthly_active_users": 0,  # TODO: Implémenter
                "total_messages_today": 0,  # TODO: Implémenter
                "total_messages_this_week": 0,  # TODO: Implémenter
                "total_messages_this_month": 0  # TODO: Implémenter
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        return admin_stats
        
    except Exception as e:
        logger.error(f"Erreur récupération stats admin: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        }


async def check_external_services() -> Dict[str, Dict[str, Any]]:
    """Vérifier la connectivité avec les services externes"""
    import httpx
    
    services = {
        "auth-service": settings.auth_service_url,
        "user-service": settings.user_service_url
    }
    
    results = {}
    
    for service_name, service_url in services.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                
                if response.status_code == 200:
                    results[service_name] = {
                        "status": "available",
                        "url": service_url,
                        "response_time_ms": response.elapsed.total_seconds() * 1000
                    }
                else:
                    results[service_name] = {
                        "status": "unavailable",
                        "url": service_url,
                        "error": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            results[service_name] = {
                "status": "unavailable",
                "url": service_url,
                "error": str(e)
            }
    
    # Compter les services disponibles
    available_count = sum(1 for service in results.values() if service["status"] == "available")
    total_count = len(results)
    
    results["summary"] = {
        "available": available_count,
        "total": total_count,
        "status": "healthy" if available_count == total_count else "degraded"
    }
    
    return results
