"""
Routes API pour la gestion des alertes de présence
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.schemas import AttendanceAlert
from app.services.alert_service import AlertService

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("/student/{student_id}", response_model=List[AttendanceAlert])
async def get_student_alerts(
    student_id: str,
    unread_only: bool = Query(False, description="Afficher seulement les alertes non lues"),
    limit: int = Query(50, le=200, description="Nombre maximum d'alertes"),
    db: Session = Depends(get_db)
):
    """
    Récupérer les alertes d'un étudiant
    """
    try:
        alert_service = AlertService(db)
        alerts = alert_service.get_student_alerts(
            student_id=student_id,
            unread_only=unread_only,
            limit=limit
        )
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/{alert_id}/read")
async def mark_alert_as_read(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Marquer une alerte comme lue
    """
    try:
        alert_service = AlertService(db)
        success = alert_service.mark_alert_as_read(alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alerte non trouvée")
        
        return {"message": "Alerte marquée comme lue"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    resolved_by: str = Query(..., description="ID de l'utilisateur qui résout l'alerte"),
    db: Session = Depends(get_db)
):
    """
    Résoudre une alerte
    """
    try:
        alert_service = AlertService(db)
        success = alert_service.resolve_alert(alert_id, resolved_by)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alerte non trouvée")
        
        return {"message": "Alerte résolue"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/check-patterns/{student_id}")
async def check_student_patterns(
    student_id: str,
    course_id: int = Query(None, description="ID du cours (optionnel)"),
    db: Session = Depends(get_db)
):
    """
    Vérifier manuellement les patterns d'absence d'un étudiant
    """
    try:
        alert_service = AlertService(db)
        alerts = alert_service.check_absence_patterns(student_id, course_id)
        
        return {
            "message": f"{len(alerts)} nouvelles alertes créées",
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/daily-check")
async def run_daily_alert_check(
    db: Session = Depends(get_db)
):
    """
    Exécuter la vérification quotidienne des alertes
    """
    try:
        alert_service = AlertService(db)
        alerts = alert_service.check_daily_alerts()
        
        return {
            "message": f"Vérification quotidienne terminée",
            "new_alerts": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/pending/count")
async def get_pending_alerts_count(
    db: Session = Depends(get_db)
):
    """
    Compter les alertes en attente
    """
    try:
        alert_service = AlertService(db)
        count = alert_service.get_pending_alerts_count()
        
        return {"pending_alerts": count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
