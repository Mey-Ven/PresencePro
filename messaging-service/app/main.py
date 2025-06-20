"""
Application principale du service de messagerie PresencePro
"""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
from datetime import datetime, timezone

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.routes import messages, health
from app.websockets import websocket_routes

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
    logger.info("🚀 Démarrage du Messaging Service...")
    
    try:
        # Connexion à MongoDB
        await connect_to_mongo()
        logger.info("✅ Connexion MongoDB établie")
        
        # TODO: Initialiser d'autres services si nécessaire
        
        logger.info("✅ Messaging Service démarré avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur démarrage service: {e}")
        raise
    
    yield
    
    # Arrêt
    logger.info("🛑 Arrêt du Messaging Service...")
    
    try:
        # Fermer la connexion MongoDB
        await close_mongo_connection()
        logger.info("✅ Connexion MongoDB fermée")
        
    except Exception as e:
        logger.error(f"❌ Erreur arrêt service: {e}")


# Créer l'application FastAPI
app = FastAPI(
    title="PresencePro Messaging Service",
    description="""
    🎭 **Service de messagerie en temps réel pour PresencePro**
    
    Ce microservice fournit une messagerie interne entre parents et administrateurs avec :
    
    ## 🚀 **Fonctionnalités principales**
    
    ### 📱 **Messagerie en temps réel**
    - Messages instantanés via WebSockets
    - Notifications de frappe en temps réel
    - Accusés de réception et de lecture
    - Statuts de connexion des utilisateurs
    
    ### 💬 **Gestion des conversations**
    - Conversations directes entre utilisateurs
    - Conversations de groupe (pour les enseignants/admins)
    - Historique complet des messages
    - Recherche dans les conversations
    
    ### 🔐 **Sécurité et authentification**
    - Authentification JWT intégrée
    - Permissions basées sur les rôles
    - Validation des autorisations de messagerie
    - Chiffrement des communications WebSocket
    
    ### 📊 **Fonctionnalités avancées**
    - Statistiques de messagerie
    - Modération des messages
    - Archivage des conversations
    - Notifications push (à venir)
    
    ## 🔗 **Intégration PresencePro**
    
    Le service s'intègre parfaitement avec :
    - **auth-service** : Authentification et autorisation
    - **user-service** : Gestion des utilisateurs et relations
    - **attendance-service** : Notifications d'absence
    - **justification-service** : Communication sur les justifications
    
    ## 🌐 **Endpoints disponibles**
    
    ### REST API
    - `/api/v1/messages/*` : Gestion des messages
    - `/health` : Vérification de santé
    - `/info` : Informations du service
    
    ### WebSocket
    - `/ws` : Connexion WebSocket principale
    - `/ws/conversation/{id}` : Connexion à une conversation spécifique
    
    ## 📱 **Utilisation WebSocket**
    
    ```javascript
    // Connexion WebSocket
    const ws = new WebSocket('ws://localhost:8007/ws?token=YOUR_JWT_TOKEN');
    
    // Envoyer un message
    ws.send(JSON.stringify({
        type: 'message',
        conversation_id: 'conv_123',
        content: 'Bonjour !',
        message_type: 'text'
    }));
    ```
    
    ---
    
    **🎭 PresencePro Messaging Service** - Communication en temps réel pour l'éducation
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

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # En production, spécifier les hôtes autorisés
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


# Inclure les routes
app.include_router(health.router)
app.include_router(messages.router)
app.include_router(websocket_routes.router)


# Route racine
@app.get("/")
async def root():
    """Page d'accueil du service"""
    return {
        "service": "messaging-service",
        "version": settings.service_version,
        "status": "running",
        "description": "Service de messagerie en temps réel pour PresencePro",
        "documentation": "/docs",
        "websocket": "/ws",
        "health": "/health",
        "info": "/info",
        "timestamp": datetime.now(timezone.utc)
    }


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
