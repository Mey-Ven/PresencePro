"""
Application principale du service de reconnaissance faciale
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.core.database import create_tables
from app.routes import face_recognition, camera
from app.models.schemas import ServiceHealth


# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Startup
    logger.info("🚀 Démarrage du Face Recognition Service...")
    
    # Créer les répertoires nécessaires
    os.makedirs(settings.faces_directory, exist_ok=True)
    os.makedirs(settings.temp_directory, exist_ok=True)
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    
    # Créer les tables de base de données
    create_tables()
    logger.info("📊 Tables de base de données créées/vérifiées")
    
    # Vérifier la disponibilité de la caméra
    try:
        import cv2
        camera = cv2.VideoCapture(settings.camera_index)
        camera_available = camera.isOpened()
        if camera_available:
            camera.release()
            logger.info("📹 Caméra détectée et disponible")
        else:
            logger.warning("⚠️ Caméra non disponible")
    except Exception as e:
        logger.error(f"❌ Erreur vérification caméra: {e}")
        camera_available = False
    
    logger.info("✅ Face Recognition Service démarré avec succès")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arrêt du Face Recognition Service...")


# Créer l'application FastAPI
app = FastAPI(
    title=settings.service_name,
    description="Service de reconnaissance faciale en temps réel pour PresencePro",
    version=settings.service_version,
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer selon l'environnement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(
    face_recognition.router,
    prefix="/api/v1/face-recognition",
    tags=["Face Recognition"]
)

app.include_router(
    camera.router,
    prefix="/api/v1/camera",
    tags=["Camera"]
)

# Servir les fichiers statiques (pour les images de visages)
if os.path.exists(settings.faces_directory):
    app.mount("/static/faces", StaticFiles(directory=settings.faces_directory), name="faces")


@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "docs": "/docs",
        "camera_stream": "/api/v1/camera/stream",
        "face_detection": "/api/v1/face-recognition/detect"
    }


@app.get("/health", response_model=ServiceHealth)
async def health_check():
    """Vérification de santé du service"""
    try:
        # Vérifier la base de données
        from app.core.database import SessionLocal
        from app.models.face import FaceEncoding, CameraSession
        
        db = SessionLocal()
        try:
            total_encodings = db.query(FaceEncoding).filter(FaceEncoding.is_active == True).count()
            active_sessions = db.query(CameraSession).filter(CameraSession.status == "active").count()
        finally:
            db.close()
        
        # Vérifier la caméra
        camera_available = False
        try:
            import cv2
            camera = cv2.VideoCapture(settings.camera_index)
            camera_available = camera.isOpened()
            if camera_available:
                camera.release()
        except:
            pass
        
        return ServiceHealth(
            status="healthy",
            service=settings.service_name,
            version=settings.service_version,
            camera_available=camera_available,
            total_encodings=total_encodings,
            active_sessions=active_sessions
        )
        
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


@app.get("/info")
async def service_info():
    """Informations détaillées du service"""
    try:
        import cv2
        import face_recognition
        import numpy as np
        
        # Informations sur les bibliothèques
        opencv_version = cv2.__version__
        numpy_version = np.__version__
        
        # Informations sur la caméra
        camera_info = {"available": False}
        try:
            camera = cv2.VideoCapture(settings.camera_index)
            if camera.isOpened():
                width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(camera.get(cv2.CAP_PROP_FPS))
                camera_info = {
                    "available": True,
                    "index": settings.camera_index,
                    "resolution": f"{width}x{height}",
                    "fps": fps
                }
                camera.release()
        except:
            pass
        
        return {
            "service": settings.service_name,
            "version": settings.service_version,
            "configuration": {
                "camera_index": settings.camera_index,
                "face_detection_model": settings.face_detection_model,
                "face_recognition_tolerance": settings.face_recognition_tolerance,
                "video_resolution": f"{settings.video_width}x{settings.video_height}",
                "video_fps": settings.video_fps
            },
            "libraries": {
                "opencv": opencv_version,
                "numpy": numpy_version,
                "face_recognition": "1.3.0"  # Version fixe
            },
            "camera": camera_info,
            "directories": {
                "faces": settings.faces_directory,
                "temp": settings.temp_directory
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur info service: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération informations")


@app.get("/test-camera")
async def test_camera():
    """Tester la caméra"""
    try:
        import cv2
        
        camera = cv2.VideoCapture(settings.camera_index)
        
        if not camera.isOpened():
            return {
                "success": False,
                "message": f"Impossible d'ouvrir la caméra {settings.camera_index}"
            }
        
        # Capturer une frame de test
        ret, frame = camera.read()
        camera.release()
        
        if ret:
            height, width = frame.shape[:2]
            return {
                "success": True,
                "message": "Caméra fonctionnelle",
                "resolution": f"{width}x{height}",
                "frame_captured": True
            }
        else:
            return {
                "success": False,
                "message": "Caméra ouverte mais impossible de capturer une frame"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur test caméra: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.service_port,
        reload=settings.debug
    )
