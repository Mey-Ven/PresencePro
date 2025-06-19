"""
Application principale du service de cours PresencePro
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import courses, schedules, assignments

# Création de l'application FastAPI
app = FastAPI(
    title="PresencePro Course Service",
    description="Service de gestion des cours et emplois du temps pour PresencePro",
    version=settings.service_version,
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

# Inclusion des routes
app.include_router(courses.router)
app.include_router(schedules.router)
app.include_router(assignments.router)


@app.get("/")
def root():
    """Endpoint racine du service"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Endpoint de vérification de santé"""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True
    )
