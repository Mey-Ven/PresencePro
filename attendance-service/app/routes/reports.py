"""
Routes API pour les rapports et exports de présence
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import io
import pandas as pd

from app.core.database import get_db
from app.models.schemas import (
    StudentAttendanceReport, CourseAttendanceReport,
    AttendanceExportRequest, AttendanceStats
)
from app.services.attendance_service import AttendanceService
from app.services.integration_service import IntegrationService

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/student/{student_id}", response_model=StudentAttendanceReport)
async def get_student_report(
    student_id: str,
    start_date: date = Query(..., description="Date de début"),
    end_date: date = Query(..., description="Date de fin"),
    db: Session = Depends(get_db)
):
    """
    Générer un rapport détaillé pour un étudiant
    """
    try:
        attendance_service = AttendanceService(db)
        integration_service = IntegrationService()
        
        # Vérifier que l'étudiant existe
        student_info = await integration_service.get_user_info(student_id)
        if not student_info:
            raise HTTPException(status_code=404, detail="Étudiant non trouvé")
        
        report = attendance_service.generate_student_report(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Enrichir avec les informations de l'étudiant
        report.student_name = f"{student_info.get('first_name', '')} {student_info.get('last_name', '')}"
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/course/{course_id}")
async def get_course_report(
    course_id: int,
    start_date: date = Query(..., description="Date de début"),
    end_date: date = Query(..., description="Date de fin"),
    db: Session = Depends(get_db)
):
    """
    Générer un rapport détaillé pour un cours
    """
    try:
        attendance_service = AttendanceService(db)
        integration_service = IntegrationService()
        
        # Vérifier que le cours existe
        course_info = await integration_service.get_course_info(course_id)
        if not course_info:
            raise HTTPException(status_code=404, detail="Cours non trouvé")
        
        # Récupérer les présences du cours
        attendances = attendance_service.get_course_attendance(
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Calculer les statistiques
        stats = attendance_service.get_attendance_stats(
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Récupérer la liste des étudiants
        students = await integration_service.get_course_students(course_id)
        
        # Analyser les étudiants avec problèmes
        low_attendance_students = []
        frequent_late_students = []
        
        for student in students:
            student_id = student.get("user_id")
            if not student_id:
                continue
                
            student_stats = attendance_service.get_attendance_stats(
                course_id=course_id,
                student_id=student_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if student_stats.attendance_rate < 0.7:  # Moins de 70%
                low_attendance_students.append({
                    "student_id": student_id,
                    "student_name": f"{student.get('first_name', '')} {student.get('last_name', '')}",
                    "attendance_rate": student_stats.attendance_rate,
                    "total_sessions": student_stats.total_sessions,
                    "missed_sessions": student_stats.absent_count
                })
            
            if student_stats.punctuality_rate < 0.8 and student_stats.late_count > 2:  # Moins de 80% et plus de 2 retards
                frequent_late_students.append({
                    "student_id": student_id,
                    "student_name": f"{student.get('first_name', '')} {student.get('last_name', '')}",
                    "punctuality_rate": student_stats.punctuality_rate,
                    "late_count": student_stats.late_count
                })
        
        report = CourseAttendanceReport(
            course_id=course_id,
            course_name=course_info.get("name"),
            period_start=start_date,
            period_end=end_date,
            total_sessions=stats.total_sessions,
            total_students=len(students),
            average_attendance_rate=stats.attendance_rate,
            low_attendance_students=low_attendance_students,
            frequent_late_students=frequent_late_students
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/export")
async def export_attendance_data(
    export_request: AttendanceExportRequest,
    db: Session = Depends(get_db)
):
    """
    Exporter les données de présence
    """
    try:
        attendance_service = AttendanceService(db)
        
        # Récupérer les données selon les filtres
        if export_request.student_id:
            attendances = attendance_service.get_student_attendance(
                student_id=export_request.student_id,
                course_id=export_request.course_id,
                start_date=export_request.start_date,
                end_date=export_request.end_date,
                limit=10000
            )
        elif export_request.course_id:
            attendances = attendance_service.get_course_attendance(
                course_id=export_request.course_id,
                start_date=export_request.start_date,
                end_date=export_request.end_date
            )
        else:
            raise HTTPException(status_code=400, detail="student_id ou course_id requis")
        
        if not attendances:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée")
        
        # Convertir en DataFrame
        data = []
        for att in attendances:
            data.append({
                "ID": att.id,
                "Étudiant": att.student_id,
                "Cours": att.course_id,
                "Statut": att.status,
                "Méthode": att.method,
                "Date/Heure": att.marked_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Confiance": att.confidence_score,
                "Localisation": att.location,
                "Notes": att.notes,
                "Validé": "Oui" if att.is_validated else "Non"
            })
        
        df = pd.DataFrame(data)
        
        # Générer le fichier selon le format
        if export_request.format == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Présences', index=False)
                
                if export_request.include_stats:
                    # Ajouter une feuille de statistiques
                    stats = attendance_service.get_attendance_stats(
                        course_id=export_request.course_id,
                        student_id=export_request.student_id,
                        start_date=export_request.start_date,
                        end_date=export_request.end_date
                    )
                    
                    stats_data = pd.DataFrame([{
                        "Total sessions": stats.total_sessions,
                        "Total présences": stats.total_attendances,
                        "Présents": stats.present_count,
                        "Absents": stats.absent_count,
                        "En retard": stats.late_count,
                        "Excusés": stats.excused_count,
                        "Taux de présence": f"{stats.attendance_rate:.1%}",
                        "Taux de ponctualité": f"{stats.punctuality_rate:.1%}"
                    }])
                    
                    stats_data.to_excel(writer, sheet_name='Statistiques', index=False)
            
            output.seek(0)
            
            return StreamingResponse(
                io.BytesIO(output.read()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=presences.xlsx"}
            )
            
        elif export_request.format == "csv":
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8')
            output.seek(0)
            
            return StreamingResponse(
                io.StringIO(output.getvalue()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=presences.csv"}
            )
            
        else:
            raise HTTPException(status_code=400, detail="Format non supporté")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    course_id: Optional[int] = Query(None, description="Filtrer par cours"),
    start_date: Optional[date] = Query(None, description="Date de début"),
    end_date: Optional[date] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db)
):
    """
    Récupérer les statistiques pour le tableau de bord
    """
    try:
        attendance_service = AttendanceService(db)
        
        # Statistiques globales
        global_stats = attendance_service.get_attendance_stats(
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Statistiques par jour (derniers 7 jours)
        from datetime import datetime, timedelta
        daily_stats = []
        
        end_date_calc = end_date or datetime.now().date()
        start_date_calc = start_date or (end_date_calc - timedelta(days=7))
        
        current_date = start_date_calc
        while current_date <= end_date_calc:
            day_stats = attendance_service.get_attendance_stats(
                course_id=course_id,
                start_date=current_date,
                end_date=current_date
            )
            
            daily_stats.append({
                "date": current_date.isoformat(),
                "total_attendances": day_stats.total_attendances,
                "present_count": day_stats.present_count,
                "absent_count": day_stats.absent_count,
                "late_count": day_stats.late_count,
                "attendance_rate": day_stats.attendance_rate
            })
            
            current_date += timedelta(days=1)
        
        return {
            "global_stats": global_stats,
            "daily_stats": daily_stats,
            "period": {
                "start_date": start_date_calc.isoformat(),
                "end_date": end_date_calc.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
