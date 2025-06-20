"""
Routes pour les statistiques
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

from app.core.database import get_database
from app.services.statistics_service import statistics_service
from app.services.chart_service import chart_service
from app.models.statistics import (
    StatisticsRequest, StatisticsResponse, ChartRequest, ChartResponse,
    ExportRequest, ExportResponse, StudentStatsResponse, ClassStatsResponse,
    GlobalStatsResponse, StatisticType, ChartType, ExportFormat
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/student/{student_id}", response_model=StudentStatsResponse)
async def get_student_statistics(
    student_id: str,
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    statistics: Optional[List[StatisticType]] = Query(None, description="Types de statistiques"),
    include_trends: bool = Query(True, description="Inclure les tendances"),
    include_comparisons: bool = Query(True, description="Inclure les comparaisons"),
    use_cache: bool = Query(True, description="Utiliser le cache"),
    db: Session = Depends(get_database)
):
    """
    Obtenir les statistiques pour un étudiant spécifique
    
    - **student_id**: ID de l'étudiant
    - **start_date**: Date de début de la période (par défaut: 30 jours avant aujourd'hui)
    - **end_date**: Date de fin de la période (par défaut: aujourd'hui)
    - **statistics**: Types de statistiques à inclure
    - **include_trends**: Inclure les tendances hebdomadaires
    - **include_comparisons**: Inclure les comparaisons avec la classe
    """
    try:
        # Dates par défaut
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=settings.default_period_days)
        
        # Validation des dates
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="La date de début doit être antérieure à la date de fin")
        
        if (end_date - start_date).days > settings.max_period_days:
            raise HTTPException(
                status_code=400, 
                detail=f"La période ne peut pas dépasser {settings.max_period_days} jours"
            )
        
        # Types de statistiques par défaut
        if not statistics:
            statistics = [StatisticType.ATTENDANCE_RATE, StatisticType.ABSENCE_COUNT]
        
        if include_trends:
            statistics.append(StatisticType.WEEKLY_TRENDS)
        
        if include_comparisons:
            statistics.append(StatisticType.STUDENT_RANKING)
        
        # Calculer les statistiques
        stats_data = await statistics_service.get_student_statistics(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            statistics=statistics,
            use_cache=use_cache
        )
        
        logger.info(f"Statistiques calculées pour l'étudiant {student_id}")
        
        return StudentStatsResponse(**stats_data)
        
    except Exception as e:
        logger.error(f"Erreur calcul statistiques étudiant {student_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/class/{class_id}", response_model=ClassStatsResponse)
async def get_class_statistics(
    class_id: str,
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    statistics: Optional[List[StatisticType]] = Query(None, description="Types de statistiques"),
    include_rankings: bool = Query(True, description="Inclure le classement des étudiants"),
    include_trends: bool = Query(True, description="Inclure les tendances"),
    use_cache: bool = Query(True, description="Utiliser le cache"),
    db: Session = Depends(get_database)
):
    """
    Obtenir les statistiques pour une classe spécifique
    
    - **class_id**: ID de la classe
    - **start_date**: Date de début de la période
    - **end_date**: Date de fin de la période
    - **statistics**: Types de statistiques à inclure
    - **include_rankings**: Inclure le classement des étudiants
    - **include_trends**: Inclure les tendances hebdomadaires
    """
    try:
        # Dates par défaut
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=settings.default_period_days)
        
        # Validation des dates
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="La date de début doit être antérieure à la date de fin")
        
        # Types de statistiques par défaut
        if not statistics:
            statistics = [StatisticType.CLASS_AVERAGE, StatisticType.ATTENDANCE_RATE]
        
        if include_rankings:
            statistics.append(StatisticType.STUDENT_RANKING)
        
        if include_trends:
            statistics.append(StatisticType.WEEKLY_TRENDS)
        
        # Calculer les statistiques
        stats_data = await statistics_service.get_class_statistics(
            class_id=class_id,
            start_date=start_date,
            end_date=end_date,
            statistics=statistics,
            use_cache=use_cache
        )
        
        logger.info(f"Statistiques calculées pour la classe {class_id}")
        
        return ClassStatsResponse(**stats_data)
        
    except Exception as e:
        logger.error(f"Erreur calcul statistiques classe {class_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/global", response_model=GlobalStatsResponse)
async def get_global_statistics(
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    statistics: Optional[List[StatisticType]] = Query(None, description="Types de statistiques"),
    include_trends: bool = Query(True, description="Inclure les tendances mensuelles"),
    include_rankings: bool = Query(True, description="Inclure le classement des classes"),
    use_cache: bool = Query(True, description="Utiliser le cache"),
    db: Session = Depends(get_database)
):
    """
    Obtenir les statistiques globales de l'établissement
    
    - **start_date**: Date de début de la période
    - **end_date**: Date de fin de la période
    - **statistics**: Types de statistiques à inclure
    - **include_trends**: Inclure les tendances mensuelles
    - **include_rankings**: Inclure le classement des classes
    """
    try:
        # Dates par défaut
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=settings.default_period_days)
        
        # Validation des dates
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="La date de début doit être antérieure à la date de fin")
        
        # Types de statistiques par défaut
        if not statistics:
            statistics = [StatisticType.ATTENDANCE_RATE, StatisticType.CLASS_AVERAGE]
        
        if include_trends:
            statistics.append(StatisticType.MONTHLY_TRENDS)
        
        if include_rankings:
            statistics.append(StatisticType.STUDENT_RANKING)
        
        # Calculer les statistiques
        stats_data = await statistics_service.get_global_statistics(
            start_date=start_date,
            end_date=end_date,
            statistics=statistics,
            use_cache=use_cache
        )
        
        logger.info("Statistiques globales calculées")
        
        return GlobalStatsResponse(**stats_data)
        
    except Exception as e:
        logger.error(f"Erreur calcul statistiques globales: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/charts/generate", response_model=ChartResponse)
async def generate_chart(
    chart_request: ChartRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database)
):
    """
    Générer un graphique à partir de données statistiques
    
    - **chart_type**: Type de graphique (line_chart, bar_chart, pie_chart, etc.)
    - **data_source**: Source des données (student_stats, class_stats, global_stats)
    - **title**: Titre du graphique
    - **export_format**: Format d'export (png, svg, pdf)
    """
    try:
        # Récupérer les données selon la source
        if chart_request.data_source.startswith("student_"):
            # Extraire l'ID étudiant de la source
            student_id = chart_request.data_source.split("_")[1]
            stats_data = await statistics_service.get_student_statistics(
                student_id=student_id,
                start_date=date.today() - timedelta(days=30),
                end_date=date.today(),
                statistics=[StatisticType.WEEKLY_TRENDS, StatisticType.COURSE_COMPARISON]
            )
        elif chart_request.data_source.startswith("class_"):
            # Extraire l'ID classe de la source
            class_id = chart_request.data_source.split("_")[1]
            stats_data = await statistics_service.get_class_statistics(
                class_id=class_id,
                start_date=date.today() - timedelta(days=30),
                end_date=date.today(),
                statistics=[StatisticType.WEEKLY_TRENDS, StatisticType.STUDENT_RANKING]
            )
        else:
            # Statistiques globales
            stats_data = await statistics_service.get_global_statistics(
                start_date=date.today() - timedelta(days=30),
                end_date=date.today(),
                statistics=[StatisticType.MONTHLY_TRENDS, StatisticType.CLASS_AVERAGE]
            )
        
        # Générer le graphique approprié
        if chart_request.chart_type == ChartType.LINE_CHART:
            chart_result = await chart_service.generate_attendance_trend_chart(stats_data)
        elif chart_request.chart_type == ChartType.BAR_CHART:
            chart_result = await chart_service.generate_course_comparison_chart(stats_data)
        elif chart_request.chart_type == ChartType.PIE_CHART:
            chart_result = await chart_service.generate_attendance_distribution_chart(stats_data)
        else:
            # Graphique générique
            chart_data = {
                "x": list(range(10)),
                "y": [i * 2 for i in range(10)],
                "name": "Données exemple"
            }
            chart_result = await chart_service.generate_chart(
                chart_request.chart_type,
                chart_data,
                chart_request.title,
                chart_request.x_axis_label,
                chart_request.y_axis_label,
                chart_request.export_format
            )
        
        logger.info(f"Graphique généré: {chart_result['chart_id']}")
        
        return ChartResponse(**chart_result)
        
    except Exception as e:
        logger.error(f"Erreur génération graphique: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/{chart_id}")
async def get_chart_file(chart_id: str):
    """
    Télécharger un fichier graphique généré
    
    - **chart_id**: ID du graphique à télécharger
    """
    try:
        # Chercher le fichier dans le répertoire d'export
        import glob
        chart_files = glob.glob(f"{settings.export_dir}/charts/chart_{chart_id}.*")
        
        if not chart_files:
            raise HTTPException(status_code=404, detail="Graphique non trouvé")
        
        file_path = chart_files[0]
        filename = file_path.split("/")[-1]
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        logger.error(f"Erreur téléchargement graphique {chart_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export", response_model=ExportResponse)
async def export_statistics(
    export_request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database)
):
    """
    Exporter des statistiques dans différents formats
    
    - **data_type**: Type de données à exporter
    - **format**: Format d'export (json, csv, xlsx, pdf)
    - **entity_type**: Type d'entité (student, class, global)
    - **entity_id**: ID de l'entité (si applicable)
    """
    try:
        # Implémenter l'export de données
        export_result = await statistics_service.export_data(
            export_request=export_request,
            db=db,
            background_tasks=background_tasks # Passer les tâches de fond si l'export est long
        )
        
        logger.info(f"Export de données demandé: ID {export_result.get('export_id')}")

        # La fonction de service devrait retourner les informations nécessaires pour ExportResponse
        return ExportResponse(**export_result)

    except Exception as e:
        logger.error(f"Erreur export statistiques: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache")
async def clear_statistics_cache(
    pattern: Optional[str] = Query(None, description="Pattern de cache à supprimer"),
    db: Session = Depends(get_database)
):
    """
    Vider le cache des statistiques
    
    - **pattern**: Pattern spécifique à supprimer (optionnel)
    """
    try:
        cleared_count = await statistics_service.invalidate_cache(pattern)
        
        logger.info(f"Cache vidé: {cleared_count} entrées supprimées")
        
        return {
            "message": "Cache vidé avec succès",
            "cleared_entries": cleared_count,
            "pattern": pattern or "all"
        }
        
    except Exception as e:
        logger.error(f"Erreur vidage cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
