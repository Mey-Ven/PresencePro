"""
Application principale du service de notifications PresencePro
"""
import logging
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from app.core.config import settings
from app.core.database import init_database, check_database_connection, get_database_stats
from app.services.event_listener import event_listener
from app.services.template_service import template_service

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application"""
    # Démarrage
    logger.info("🚀 Démarrage du Notification Service...")
    
    try:
        # Initialiser la base de données
        init_database()
        logger.info("✅ Base de données initialisée")
        
        # Initialiser les templates par défaut
        await template_service.initialize_default_templates()
        logger.info("✅ Templates par défaut initialisés")
        
        # Démarrer l'écoute des événements en arrière-plan
        asyncio.create_task(start_event_listener())
        logger.info("✅ Écoute d'événements démarrée")
        
        logger.info("✅ Notification Service démarré avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur démarrage service: {e}")
        raise
    
    yield
    
    # Arrêt
    logger.info("🛑 Arrêt du Notification Service...")
    
    try:
        # Arrêter l'écoute des événements
        await event_listener.stop_listening()
        await event_listener.disconnect()
        logger.info("✅ Écoute d'événements arrêtée")
        
    except Exception as e:
        logger.error(f"❌ Erreur arrêt service: {e}")


async def start_event_listener():
    """Démarrer l'écoute des événements en arrière-plan"""
    try:
        await event_listener.start_listening()
    except Exception as e:
        logger.error(f"❌ Erreur écoute événements: {e}")


# Créer l'application FastAPI
app = FastAPI(
    title="PresencePro Notification Service",
    description="""
    🎭 **Service de notifications asynchrones pour PresencePro**
    
    Ce microservice gère l'envoi de notifications par email, SMS et push pour tous les événements de l'écosystème PresencePro.
    
    ## 🚀 **Fonctionnalités principales**
    
    ### 📧 **Notifications par email**
    - Envoi via SMTP ou SendGrid
    - Templates personnalisables avec Jinja2
    - Support HTML avec CSS inline
    - Gestion des pièces jointes
    - Retry automatique en cas d'échec
    
    ### 📱 **Notifications SMS et Push**
    - SMS via Twilio
    - Push notifications via Firebase
    - Gestion des tokens d'appareils
    - Notifications en lot
    
    ### ⚡ **Traitement asynchrone**
    - Tâches Celery avec Redis
    - Queues séparées par type de notification
    - Retry intelligent avec backoff exponentiel
    - Monitoring des tâches en temps réel
    
    ### 🎯 **Événements supportés**
    - Absence détectée
    - Justification soumise/approuvée/rejetée
    - Message reçu
    - Approbation parentale requise
    - Validation administrative requise
    - Rapports quotidiens/hebdomadaires
    
    ### 🔧 **Gestion des templates**
    - Templates par type d'événement et canal
    - Support multilingue (FR/EN)
    - Variables dynamiques
    - Prévisualisation et test
    
    ### 👤 **Préférences utilisateur**
    - Configuration par canal (email/SMS/push)
    - Heures de silence
    - Fréquence des notifications
    - Langue préférée
    
    ## 🔗 **Intégration PresencePro**
    
    Le service écoute les événements de :
    - **attendance-service** : Détection d'absences
    - **justification-service** : Workflow de justifications
    - **messaging-service** : Nouveaux messages
    - **auth-service** : Authentification et permissions
    - **user-service** : Informations utilisateurs
    
    ## 📊 **Monitoring**
    
    - Health checks complets
    - Métriques Prometheus
    - Logs structurés
    - Statistiques d'envoi
    - Queue monitoring
    
    ---
    
    **🎭 PresencePro Notification Service** - Notifications intelligentes pour l'éducation
    """,
    version=settings.service_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logger les requêtes HTTP"""
    start_time = datetime.now(timezone.utc)
    
    # Traiter la requête
    response = await call_next(request)
    
    # Calculer le temps de traitement
    process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Logger la requête
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # Ajouter le temps de traitement dans les headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'erreurs global"""
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erreur interne du serveur",
            "error_type": type(exc).__name__,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# Routes de base

@app.get("/")
async def root():
    """Page d'accueil du service"""
    return {
        "service": "notification-service",
        "version": settings.service_version,
        "status": "running",
        "description": "Service de notifications asynchrones pour PresencePro",
        "documentation": "/docs",
        "health": "/health",
        "celery_monitoring": "/celery",
        "timestamp": datetime.now(timezone.utc)
    }


@app.get("/health")
async def health_check():
    """Vérification de santé du service"""
    try:
        # Vérifier la base de données
        db_healthy = check_database_connection()
        
        # Vérifier Redis
        redis_healthy = False
        try:
            await event_listener.connect()
            redis_healthy = True
        except:
            pass
        
        # Vérifier Celery
        from app.core.celery_app import celery_app
        celery_healthy = False
        celery_workers = 0
        try:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            if stats:
                celery_healthy = True
                celery_workers = len(stats)
        except:
            pass
        
        # Statistiques de base de données
        db_stats = get_database_stats()
        
        # Informations sur la queue
        queue_info = await event_listener.get_queue_info()
        
        # État général
        is_healthy = db_healthy and redis_healthy
        
        health_status = {
            "service": "notification-service",
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now(timezone.utc),
            "version": settings.service_version,
            "checks": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "details": db_stats
                },
                "redis": {
                    "status": "healthy" if redis_healthy else "unhealthy",
                    "details": queue_info
                },
                "celery": {
                    "status": "healthy" if celery_healthy else "unhealthy",
                    "workers": celery_workers
                },
                "event_listener": {
                    "status": "running" if event_listener.is_listening else "stopped"
                }
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Erreur vérification santé: {e}")
        return {
            "service": "notification-service",
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc),
            "error": str(e)
        }


@app.get("/info")
async def service_info():
    """Informations détaillées sur le service"""
    try:
        # Statistiques de base de données
        db_stats = get_database_stats()
        
        # Informations Celery
        from app.core.celery_app import celery_app
        celery_info = {}
        try:
            inspect = celery_app.control.inspect()
            celery_info = {
                "active_tasks": inspect.active(),
                "scheduled_tasks": inspect.scheduled(),
                "reserved_tasks": inspect.reserved(),
                "stats": inspect.stats()
            }
        except:
            celery_info = {"error": "Celery non disponible"}
        
        # Configuration du service
        service_config = {
            "email_provider": "sendgrid" if settings.use_sendgrid else "smtp",
            "sms_enabled": settings.sms_enabled,
            "push_enabled": settings.push_notifications_enabled,
            "max_retry_attempts": settings.max_retry_attempts,
            "batch_size": settings.batch_size,
            "supported_languages": settings.supported_languages,
            "notification_types": list(settings.notification_types.keys()),
            "notification_channels": list(settings.notification_channels.keys())
        }
        
        info = {
            "service": {
                "name": settings.service_name,
                "version": settings.service_version,
                "port": settings.service_port,
                "debug": settings.debug
            },
            "database": {
                "type": "SQLite" if "sqlite" in settings.database_url else "PostgreSQL",
                "stats": db_stats
            },
            "celery": celery_info,
            "configuration": service_config,
            "features": {
                "email_notifications": True,
                "sms_notifications": settings.sms_enabled,
                "push_notifications": settings.push_notifications_enabled,
                "webhook_support": True,
                "template_system": True,
                "user_preferences": True,
                "retry_mechanism": True,
                "batch_processing": True,
                "event_listening": True
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


# Endpoint pour tester l'envoi d'événements (développement uniquement)
@app.post("/test/event")
async def test_event(event_data: dict):
    """Tester l'envoi d'un événement (développement uniquement)"""
    if not settings.debug:
        return {"error": "Endpoint disponible uniquement en mode debug"}
    
    try:
        await event_listener.publish_event(event_data)
        return {"success": True, "message": "Événement publié pour test"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Point d'entrée pour le développement
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Démarrage du serveur de développement sur le port {settings.service_port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.service_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
