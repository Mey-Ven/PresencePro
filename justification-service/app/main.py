"""
Application principale du service de justifications PresencePro
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables, engine
from app.routes.justifications import router as justifications_router
from app.services.integration_service import IntegrationService


# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Démarrage
    logger.info("🚀 Démarrage du Justification Service...")
    
    # Créer les tables de base de données
    try:
        create_tables()
        logger.info("📊 Tables de base de données créées/vérifiées")
    except Exception as e:
        logger.error(f"❌ Erreur création tables: {e}")
    
    # Tester la connectivité avec les autres services
    integration_service = IntegrationService()
    services_status = {}
    
    for service_name in ["auth", "user", "course", "attendance"]:
        try:
            is_available = integration_service.is_service_available(service_name)
            services_status[service_name] = "✅" if is_available else "❌"
        except Exception as e:
            services_status[service_name] = "❌"
            logger.warning(f"Service {service_name} non disponible: {e}")
    
    available_count = sum(1 for status in services_status.values() if status == "✅")
    logger.info(f"🔗 Services disponibles: {available_count}/4")
    
    for service, status in services_status.items():
        logger.info(f"   {status} {service}-service")
    
    if available_count == 0:
        logger.warning("⚠️  Aucun service externe disponible - Le service fonctionnera en mode autonome")
    
    logger.info("✅ Justification Service démarré avec succès")
    
    yield
    
    # Arrêt
    logger.info("🛑 Arrêt du Justification Service...")


# Créer l'application FastAPI
app = FastAPI(
    title="PresencePro Justification Service",
    description="""
    Service de gestion des justifications d'absence pour PresencePro.
    
    ## Fonctionnalités
    
    * **Soumission de justifications** par les étudiants
    * **Approbation parentale** avec workflow configurable
    * **Validation administrative** par les enseignants/administrateurs
    * **Gestion de documents** avec upload de pièces justificatives
    * **Intégration** avec les autres services PresencePro
    * **Notifications** automatiques par email
    
    ## Workflow
    
    1. **Étudiant** crée une justification d'absence
    2. **Soumission** pour approbation
    3. **Parents** approuvent ou rejettent (optionnel)
    4. **Administration** valide ou rejette
    5. **Notification** automatique du service de présences
    """,
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(
    justifications_router,
    prefix="/api/v1/justifications",
    tags=["justifications"]
)


@app.get("/")
async def root():
    """Point d'entrée principal du service"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "create_justification": "/api/v1/justifications/create",
            "submit_justification": "/api/v1/justifications/{id}/submit",
            "parent_approval": "/api/v1/justifications/{id}/approve-parent",
            "admin_validation": "/api/v1/justifications/{id}/validate-admin",
            "get_justification": "/api/v1/justifications/{id}",
            "student_justifications": "/api/v1/justifications/student/{id}",
            "pending_approvals": "/api/v1/justifications/pending/approvals",
            "pending_validations": "/api/v1/justifications/pending/validations",
            "justification_status": "/api/v1/justifications/status/{id}",
            "upload_document": "/api/v1/justifications/{id}/documents",
            "get_documents": "/api/v1/justifications/{id}/documents"
        }
    }


@app.get("/health")
async def health_check():
    """Vérification de santé du service"""
    try:
        from sqlalchemy import text
        from app.core.database import SessionLocal
        from app.models.justification import Justification
        import os
        
        # Test de connexion à la base de données
        db_connected = False
        total_justifications = 0
        pending_approvals = 0
        pending_validations = 0
        
        try:
            db = SessionLocal()
            # Test de connexion
            db.execute(text("SELECT 1"))
            db_connected = True
            
            # Statistiques
            total_justifications = db.query(Justification).count()
            pending_approvals = db.query(Justification).filter(
                Justification.status == "parent_pending"
            ).count()
            pending_validations = db.query(Justification).filter(
                Justification.status == "admin_pending"
            ).count()
            
            db.close()
        except Exception as e:
            logger.error(f"Erreur health check DB: {e}")
        
        # Test du répertoire d'upload
        upload_writable = False
        try:
            upload_dir = settings.upload_dir
            os.makedirs(upload_dir, exist_ok=True)
            test_file = os.path.join(upload_dir, "test_write.tmp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            upload_writable = True
        except Exception as e:
            logger.error(f"Erreur test upload: {e}")
        
        status = "healthy" if db_connected and upload_writable else "unhealthy"
        
        return {
            "status": status,
            "service": settings.service_name,
            "version": settings.service_version,
            "database_connected": db_connected,
            "total_justifications": total_justifications,
            "pending_approvals": pending_approvals,
            "pending_validations": pending_validations,
            "upload_directory_writable": upload_writable
        }
        
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return {
            "status": "unhealthy",
            "service": settings.service_name,
            "version": settings.service_version,
            "error": str(e)
        }


@app.get("/info")
async def service_info():
    """Informations détaillées du service"""
    try:
        from app.services.integration_service import IntegrationService
        
        integration_service = IntegrationService()
        
        # Statut des services externes
        external_services = {}
        for service_name in ["auth", "user", "course", "attendance"]:
            external_services[service_name] = integration_service.is_service_available(service_name)
        
        return {
            "service": {
                "name": settings.service_name,
                "version": settings.service_version,
                "port": settings.service_port,
                "debug": settings.debug
            },
            "database": {
                "url": settings.database_url.split("@")[-1] if "@" in settings.database_url else settings.database_url,
                "pool_size": settings.database_pool_size
            },
            "configuration": {
                "max_justification_days": settings.max_justification_days,
                "auto_expire_days": settings.auto_expire_days,
                "require_parent_approval": settings.require_parent_approval,
                "require_admin_validation": settings.require_admin_validation,
                "max_file_size_mb": round(settings.max_file_size / 1024 / 1024, 2),
                "allowed_file_types": settings.allowed_file_types
            },
            "external_services": external_services,
            "features": [
                "Création de justifications",
                "Workflow d'approbation parentale",
                "Validation administrative",
                "Gestion de documents",
                "Intégration avec attendance-service",
                "Notifications automatiques",
                "Historique des modifications"
            ]
        }
        
    except Exception as e:
        logger.error(f"Erreur info service: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération informations: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.service_port,
        reload=settings.debug
    )
