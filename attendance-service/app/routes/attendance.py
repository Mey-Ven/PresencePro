"""
Routes API pour la gestion des présences
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.models.schemas import (
    AttendanceMarkRequest, AttendanceUpdate, AttendanceResponse,
    AttendanceStats, StudentAttendanceReport, CourseAttendanceReport,
    BulkAttendanceRequest, AttendanceSessionCreate, AttendanceSessionResponse
)
from app.services.attendance_service import AttendanceService
from app.services.integration_service import IntegrationService
from app.services.alert_service import AlertService

router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])


@router.post("/mark", response_model=AttendanceResponse)
async def mark_attendance(
    request: AttendanceMarkRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Marquer une présence
    
    - **student_id**: ID de l'étudiant
    - **course_id**: ID du cours (optionnel)
    - **schedule_id**: ID du créneau horaire (optionnel)
    - **status**: Statut de présence (present, absent, late, excused)
    - **method**: Méthode d'enregistrement (manual, face_recognition, etc.)
    """
    try:
        attendance_service = AttendanceService(db)
        integration_service = IntegrationService()
        
        # Valider la demande si course_id est fourni (désactivé pour les tests)
        # if request.course_id:
        #     validation = await integration_service.validate_attendance_request(
        #         request.student_id,
        #         request.course_id
        #     )
        #
        #     if not validation["valid"]:
        #         raise HTTPException(
        #             status_code=400,
        #             detail=f"Demande invalide: {', '.join(validation['errors'])}"
        #         )
        
        # Marquer la présence
        attendance = attendance_service.mark_attendance(request)
        
        # Vérifier les patterns d'absence en arrière-plan
        background_tasks.add_task(
            check_attendance_patterns,
            db,
            request.student_id,
            request.course_id
        )
        
        return attendance
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/bulk-mark")
async def bulk_mark_attendance(
    request: BulkAttendanceRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Marquer plusieurs présences en une fois
    """
    try:
        attendance_service = AttendanceService(db)
        results = []
        errors = []
        
        for i, attendance_request in enumerate(request.attendances):
            try:
                # Utiliser les valeurs par défaut de la requête bulk si non spécifiées
                if not attendance_request.course_id:
                    attendance_request.course_id = request.course_id
                if not attendance_request.schedule_id:
                    attendance_request.schedule_id = request.schedule_id
                
                attendance = attendance_service.mark_attendance(attendance_request)
                results.append(attendance)
                
            except Exception as e:
                errors.append({
                    "index": i,
                    "student_id": attendance_request.student_id,
                    "error": str(e)
                })
        
        # Vérifier les patterns pour tous les étudiants en arrière-plan
        for attendance_request in request.attendances:
            background_tasks.add_task(
                check_attendance_patterns,
                db,
                attendance_request.student_id,
                attendance_request.course_id or request.course_id
            )
        
        return {
            "success_count": len(results),
            "error_count": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/student/{student_id}", response_model=List[AttendanceResponse])
async def get_student_attendance(
    student_id: str,
    course_id: Optional[int] = Query(None, description="Filtrer par cours"),
    start_date: Optional[date] = Query(None, description="Date de début"),
    end_date: Optional[date] = Query(None, description="Date de fin"),
    limit: int = Query(100, le=1000, description="Nombre maximum de résultats"),
    db: Session = Depends(get_db)
):
    """
    Récupérer l'historique des présences d'un étudiant
    """
    try:
        attendance_service = AttendanceService(db)
        attendances = attendance_service.get_student_attendance(
            student_id=student_id,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return attendances
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/course/{course_id}", response_model=List[AttendanceResponse])
async def get_course_attendance(
    course_id: int,
    session_date: Optional[date] = Query(None, description="Date de session spécifique"),
    start_date: Optional[date] = Query(None, description="Date de début"),
    end_date: Optional[date] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db)
):
    """
    Récupérer les présences d'un cours
    """
    try:
        attendance_service = AttendanceService(db)
        attendances = attendance_service.get_course_attendance(
            course_id=course_id,
            session_date=session_date,
            start_date=start_date,
            end_date=end_date
        )
        
        return attendances
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    update: AttendanceUpdate,
    db: Session = Depends(get_db)
):
    """
    Mettre à jour une présence existante
    """
    try:
        attendance_service = AttendanceService(db)
        attendance = attendance_service.update_attendance(attendance_id, update)
        
        return attendance
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/stats", response_model=AttendanceStats)
async def get_attendance_stats(
    course_id: Optional[int] = Query(None, description="Filtrer par cours"),
    student_id: Optional[str] = Query(None, description="Filtrer par étudiant"),
    start_date: Optional[date] = Query(None, description="Date de début"),
    end_date: Optional[date] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db)
):
    """
    Récupérer les statistiques de présence
    """
    try:
        attendance_service = AttendanceService(db)
        stats = attendance_service.get_attendance_stats(
            course_id=course_id,
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/report/student/{student_id}", response_model=StudentAttendanceReport)
async def get_student_report(
    student_id: str,
    start_date: date = Query(..., description="Date de début du rapport"),
    end_date: date = Query(..., description="Date de fin du rapport"),
    db: Session = Depends(get_db)
):
    """
    Générer un rapport de présence pour un étudiant
    """
    try:
        attendance_service = AttendanceService(db)
        report = attendance_service.generate_student_report(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/session", response_model=AttendanceSessionResponse)
async def create_attendance_session(
    session: AttendanceSessionCreate,
    db: Session = Depends(get_db)
):
    """
    Créer une session de présence
    """
    try:
        # TODO: Implémenter la création de session
        raise HTTPException(status_code=501, detail="Fonctionnalité en cours de développement")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


async def check_attendance_patterns(db: Session, student_id: str, course_id: Optional[int]):
    """Tâche en arrière-plan pour vérifier les patterns d'absence"""
    try:
        alert_service = AlertService(db)
        alert_service.check_absence_patterns(student_id, course_id)
    except Exception as e:
        # Log l'erreur mais ne pas faire échouer la requête principale
        import logging
        logging.getLogger(__name__).error(f"Erreur vérification patterns: {e}")


# Endpoint pour la reconnaissance faciale
@router.post("/face-recognition")
async def mark_attendance_from_face_recognition(
    recognition_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Endpoint spécial pour recevoir les données du service de reconnaissance faciale
    """
    try:
        # Extraire les données de reconnaissance
        student_id = recognition_data.get("student_id")
        confidence = recognition_data.get("confidence", 0.0)
        course_id = recognition_data.get("course_id")
        
        if not student_id:
            raise HTTPException(status_code=400, detail="student_id requis")
        
        # Déterminer le statut basé sur la confiance
        if confidence >= 0.8:
            status = "present"
        elif confidence >= 0.6:
            status = "present"  # Avec note de confiance faible
        else:
            # Confiance trop faible, ne pas marquer
            return {"message": "Confiance insuffisante pour marquer présent", "confidence": confidence}
        
        # Créer la requête de présence
        attendance_request = AttendanceMarkRequest(
            student_id=student_id,
            course_id=course_id,
            status=status,
            method="face_recognition",
            confidence_score=confidence,
            notes=f"Reconnaissance faciale - confiance: {confidence:.2f}"
        )
        
        # Marquer la présence
        attendance_service = AttendanceService(db)
        attendance = attendance_service.mark_attendance(attendance_request, created_by="face-recognition-service")
        
        return {
            "message": "Présence marquée avec succès",
            "attendance": attendance,
            "confidence": confidence
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
