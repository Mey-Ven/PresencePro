"""
Application principale du service de statistiques PresencePro
"""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
import os

from app.core.config import settings
from app.core.database import init_database, check_database_connection
from app.routes import statistics, health

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
    logger.info("🚀 Démarrage du Statistics Service...")
    
    try:
        # Créer les répertoires nécessaires
        os.makedirs("logs", exist_ok=True)
        os.makedirs("exports/json", exist_ok=True)
        os.makedirs("exports/charts", exist_ok=True)
        
        # Initialiser la base de données
        init_database()
        logger.info("✅ Base de données initialisée")
        
        # TODO: Initialiser les données d'exemple si nécessaire
        if settings.mock_data_enabled:
            logger.info("📊 Génération de données d'exemple...")
            # await generate_sample_data()
        
        logger.info("✅ Statistics Service démarré avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur démarrage service: {e}")
        raise
    
    yield
    
    # Arrêt
    logger.info("🛑 Arrêt du Statistics Service...")
    
    try:
        # Nettoyage si nécessaire
        logger.info("✅ Service arrêté proprement")
        
    except Exception as e:
        logger.error(f"❌ Erreur arrêt service: {e}")


# Créer l'application FastAPI
app = FastAPI(
    title="PresencePro Statistics Service",
    description="""
    🎭 **Service de statistiques et d'analyse pour PresencePro**
    
    Ce microservice génère des statistiques avancées et des rapports d'analyse pour tous les aspects de la gestion des présences dans l'écosystème PresencePro.
    
    ## 🚀 **Fonctionnalités principales**
    
    ### 📊 **Statistiques individuelles**
    - Taux de présence par étudiant
    - Évolution des absences dans le temps
    - Comparaison avec la moyenne de classe
    - Tendances et prédictions
    - Classement et percentiles
    
    ### 🏫 **Statistiques de classe**
    - Moyennes et médianes de présence
    - Classement des étudiants
    - Comparaison entre cours
    - Identification des étudiants à risque
    - Tendances hebdomadaires et mensuelles
    
    ### 🌍 **Statistiques globales**
    - Vue d'ensemble de l'établissement
    - Comparaison entre classes
    - Tendances générales
    - Indicateurs de performance
    - Tableaux de bord exécutifs
    
    ### 📈 **Génération de graphiques**
    - Graphiques en ligne pour les tendances
    - Graphiques en barres pour les comparaisons
    - Graphiques en secteurs pour les répartitions
    - Cartes de chaleur pour les patterns
    - Histogrammes et box plots pour les distributions
    
    ### 📤 **Export de données**
    - Export JSON pour intégrations
    - Export CSV pour analyse externe
    - Export Excel avec formatage
    - Export PDF avec graphiques
    - Export d'images haute résolution
    
    ### ⚡ **Performance et cache**
    - Cache Redis pour les calculs coûteux
    - Requêtes optimisées avec index
    - Calculs asynchrones en arrière-plan
    - Pagination pour les gros volumes
    - Rate limiting pour la protection
    
    ## 🎯 **Types de statistiques**
    
    - **attendance_rate** : Taux de présence
    - **absence_count** : Nombre d'absences
    - **tardiness_count** : Nombre de retards
    - **justified_absences** : Absences justifiées
    - **unjustified_absences** : Absences non justifiées
    - **weekly_trends** : Tendances hebdomadaires
    - **monthly_trends** : Tendances mensuelles
    - **course_comparison** : Comparaison par cours
    - **student_ranking** : Classement des étudiants
    - **class_average** : Moyennes de classe
    
    ## 📊 **Types de graphiques**
    
    - **line_chart** : Graphiques en ligne
    - **bar_chart** : Graphiques en barres
    - **pie_chart** : Graphiques en secteurs
    - **heatmap** : Cartes de chaleur
    - **histogram** : Histogrammes
    - **box_plot** : Boîtes à moustaches
    - **scatter_plot** : Nuages de points
    - **area_chart** : Graphiques en aires
    
    ## 🔗 **Intégration PresencePro**
    
    Le service s'intègre avec :
    - **attendance-service** : Données de présence
    - **user-service** : Informations utilisateurs
    - **course-service** : Données des cours
    - **justification-service** : Justifications d'absence
    - **auth-service** : Authentification et permissions
    
    ## 📈 **Cas d'usage**
    
    ### **Pour les enseignants**
    - Suivi individuel des étudiants
    - Identification des étudiants en difficulté
    - Rapports de classe personnalisés
    - Comparaison entre cours
    
    ### **Pour les administrateurs**
    - Tableaux de bord exécutifs
    - Comparaison entre classes
    - Tendances de l'établissement
    - Rapports de performance
    
    ### **Pour les parents**
    - Suivi de leur enfant
    - Comparaison avec la classe
    - Évolution dans le temps
    - Alertes et notifications
    
    ### **Pour les étudiants**
    - Auto-évaluation
    - Objectifs de présence
    - Comparaison anonyme
    - Motivation et gamification
    
    ---
    
    **🎭 PresencePro Statistics Service** - Intelligence analytique pour l'éducation
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

# Servir les fichiers statiques (exports)
if os.path.exists(settings.export_dir):
    app.mount("/exports", StaticFiles(directory=settings.export_dir), name="exports")

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


# Gestionnaire d'erreurs HTTP
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire d'erreurs HTTP"""
    logger.warning(f"Erreur HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# Inclure les routes
app.include_router(health.router)
app.include_router(statistics.router)


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
