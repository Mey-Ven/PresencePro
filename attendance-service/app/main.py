"""
Application principale du service de gestion des présences
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.core.config import settings
from app.core.database import get_db, create_tables
from app.routes import attendance, alerts, reports
from app.services.alert_service import AlertService
from app.services.integration_service import IntegrationService
from app.models.schemas import ServiceHealth

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="PresencePro Attendance Service",
    description="Microservice de gestion des présences et absences",
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(attendance.router)
app.include_router(alerts.router)
app.include_router(reports.router)


@app.on_event("startup")
async def startup_event():
    """Événements de démarrage"""
    logger.info("🚀 Démarrage du Attendance Service...")
    
    try:
        # Créer les tables de base de données
        create_tables()
        logger.info("📊 Tables de base de données créées/vérifiées")
        
        # Vérifier la connectivité avec les autres services
        integration_service = IntegrationService()
        
        services_status = {
            "auth": integration_service.is_service_available("auth"),
            "user": integration_service.is_service_available("user"),
            "course": integration_service.is_service_available("course"),
            "face_recognition": integration_service.is_service_available("face_recognition")
        }
        
        available_services = sum(services_status.values())
        logger.info(f"🔗 Services disponibles: {available_services}/4")
        
        for service, available in services_status.items():
            status = "✅" if available else "❌"
            logger.info(f"   {status} {service}-service")
        
        logger.info("✅ Attendance Service démarré avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Événements d'arrêt"""
    logger.info("🛑 Arrêt du Attendance Service...")


@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "mark_attendance": "/api/v1/attendance/mark",
            "student_attendance": "/api/v1/attendance/student/{id}",
            "course_attendance": "/api/v1/attendance/course/{id}",
            "student_report": "/api/v1/reports/student/{id}",
            "course_report": "/api/v1/reports/course/{id}",
            "alerts": "/api/v1/alerts/student/{id}",
            "export": "/api/v1/reports/export"
        }
    }


@app.get("/health", response_model=ServiceHealth)
async def health_check(db: Session = Depends(get_db)):
    """Vérification de santé du service"""
    try:
        # Tester la connexion à la base de données
        db.execute("SELECT 1")
        database_connected = True
        
        # Compter les présences
        from app.models.attendance import Attendance, AttendanceSession, AttendanceAlert
        total_attendances = db.query(Attendance).count()
        
        # Compter les sessions actives
        active_sessions = db.query(AttendanceSession).filter(
            AttendanceSession.is_active == True
        ).count()
        
        # Compter les alertes en attente
        alert_service = AlertService(db)
        pending_alerts = alert_service.get_pending_alerts_count()
        
        return ServiceHealth(
            status="healthy",
            service=settings.service_name,
            version=settings.service_version,
            database_connected=database_connected,
            total_attendances=total_attendances,
            active_sessions=active_sessions,
            pending_alerts=pending_alerts
        )
        
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return ServiceHealth(
            status="unhealthy",
            service=settings.service_name,
            version=settings.service_version,
            database_connected=False,
            total_attendances=0,
            active_sessions=0,
            pending_alerts=0
        )


@app.get("/info")
async def service_info():
    """Informations détaillées du service"""
    integration_service = IntegrationService()
    
    return {
        "service": {
            "name": settings.service_name,
            "version": settings.service_version,
            "port": settings.service_port,
            "debug": settings.debug
        },
        "database": {
            "url": settings.database_url.replace("password", "***"),
            "pool_size": settings.database_pool_size
        },
        "integration": {
            "auth_service": settings.auth_service_url,
            "user_service": settings.user_service_url,
            "course_service": settings.course_service_url,
            "face_recognition_service": settings.face_recognition_service_url
        },
        "configuration": {
            "grace_period_minutes": settings.attendance_grace_period_minutes,
            "late_threshold_minutes": settings.late_threshold_minutes,
            "auto_mark_absent_hours": settings.auto_mark_absent_hours,
            "timezone": settings.default_timezone
        },
        "services_status": {
            "auth": integration_service.is_service_available("auth"),
            "user": integration_service.is_service_available("user"),
            "course": integration_service.is_service_available("course"),
            "face_recognition": integration_service.is_service_available("face_recognition")
        },
        "timestamp": datetime.now().isoformat()
    }


# Endpoint pour recevoir les notifications du service de reconnaissance faciale
@app.post("/api/v1/webhooks/face-recognition")
async def face_recognition_webhook(
    notification: dict,
    db: Session = Depends(get_db)
):
    """
    Webhook pour recevoir les notifications du service de reconnaissance faciale
    """
    try:
        logger.info(f"Notification reçue du service de reconnaissance faciale: {notification}")
        
        # Traiter la notification selon le type
        notification_type = notification.get("type")
        
        if notification_type == "face_recognized":
            # Marquer automatiquement la présence
            from app.services.attendance_service import AttendanceService
            from app.models.schemas import AttendanceMarkRequest
            
            attendance_service = AttendanceService(db)
            
            request = AttendanceMarkRequest(
                student_id=notification.get("student_id"),
                course_id=notification.get("course_id"),
                status="present",
                method="face_recognition",
                confidence_score=notification.get("confidence"),
                notes=f"Reconnaissance automatique - {notification.get('timestamp')}"
            )
            
            attendance = attendance_service.mark_attendance(request, created_by="face-recognition-service")
            
            return {
                "message": "Présence marquée automatiquement",
                "attendance_id": attendance.id,
                "status": "success"
            }
        
        elif notification_type == "face_detection_failed":
            # Log l'échec de détection
            logger.warning(f"Échec de détection pour {notification.get('student_id')}")
            
            return {
                "message": "Échec de détection enregistré",
                "status": "logged"
            }
        
        else:
            logger.warning(f"Type de notification non reconnu: {notification_type}")
            return {
                "message": "Type de notification non reconnu",
                "status": "ignored"
            }
        
    except Exception as e:
        logger.error(f"Erreur traitement webhook reconnaissance faciale: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.service_port,
        reload=settings.debug
    )
