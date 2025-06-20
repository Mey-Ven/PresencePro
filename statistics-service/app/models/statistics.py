"""
Modèles de données pour les statistiques
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date
from enum import Enum

from app.core.database import Base


class StatisticType(str, Enum):
    """Types de statistiques"""
    ATTENDANCE_RATE = "attendance_rate"
    ABSENCE_COUNT = "absence_count"
    TARDINESS_COUNT = "tardiness_count"
    JUSTIFIED_ABSENCES = "justified_absences"
    UNJUSTIFIED_ABSENCES = "unjustified_absences"
    WEEKLY_TRENDS = "weekly_trends"
    MONTHLY_TRENDS = "monthly_trends"
    COURSE_COMPARISON = "course_comparison"
    STUDENT_RANKING = "student_ranking"
    CLASS_AVERAGE = "class_average"


class AggregationPeriod(str, Enum):
    """Périodes d'agrégation"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ChartType(str, Enum):
    """Types de graphiques"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    SCATTER_PLOT = "scatter_plot"
    AREA_CHART = "area_chart"


class ExportFormat(str, Enum):
    """Formats d'export"""
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"
    PNG = "png"
    SVG = "svg"


# Modèles SQLAlchemy

class AttendanceRecord(Base):
    """Enregistrements de présence (réplique pour statistiques)"""
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiants
    student_id = Column(String(255), index=True)
    course_id = Column(String(255), index=True)
    class_id = Column(String(255), index=True)
    teacher_id = Column(String(255), index=True)
    
    # Données de présence
    date = Column(Date, index=True)
    time_slot = Column(String(50))
    status = Column(String(20), index=True)  # present, absent, late, excused
    
    # Métadonnées
    detection_method = Column(String(50))  # facial_recognition, manual, qr_code
    confidence_score = Column(Float)
    
    # Justification
    is_justified = Column(Boolean, default=False)
    justification_id = Column(String(255))
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StatisticsCache(Base):
    """Cache des statistiques calculées"""
    __tablename__ = "statistics_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Clé de cache
    cache_key = Column(String(500), unique=True, index=True)
    
    # Type et paramètres
    statistic_type = Column(String(100), index=True)
    entity_type = Column(String(50))  # student, class, global
    entity_id = Column(String(255))
    
    # Période
    start_date = Column(Date)
    end_date = Column(Date)
    aggregation_period = Column(String(20))
    
    # Données
    data = Column(JSON)
    meta_data = Column(JSON)
    
    # Gestion du cache
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    hit_count = Column(Integer, default=0)


class StatisticsReport(Base):
    """Rapports de statistiques générés"""
    __tablename__ = "statistics_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiants
    report_id = Column(String(255), unique=True, index=True)
    name = Column(String(500))
    description = Column(Text)
    
    # Type et configuration
    report_type = Column(String(100))
    entity_type = Column(String(50))
    entity_ids = Column(JSON)  # Liste des IDs concernés
    
    # Période
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Configuration
    statistics_included = Column(JSON)
    charts_included = Column(JSON)
    export_formats = Column(JSON)
    
    # Résultats
    data = Column(JSON)
    file_paths = Column(JSON)
    
    # Métadonnées
    generated_by = Column(String(255))
    generation_time_seconds = Column(Float)
    file_size_bytes = Column(Integer)
    
    # Statut
    status = Column(String(50), default="pending")  # pending, completed, failed
    error_message = Column(Text)
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class StudentStatistics(Base):
    """Statistiques pré-calculées par étudiant"""
    __tablename__ = "student_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiants
    student_id = Column(String(255), index=True)
    period_start = Column(Date, index=True)
    period_end = Column(Date, index=True)
    aggregation_period = Column(String(20))
    
    # Statistiques de base
    total_courses = Column(Integer, default=0)
    present_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)
    late_count = Column(Integer, default=0)
    excused_count = Column(Integer, default=0)
    
    # Taux calculés
    attendance_rate = Column(Float)
    absence_rate = Column(Float)
    tardiness_rate = Column(Float)
    justification_rate = Column(Float)
    
    # Tendances
    trend_direction = Column(String(20))  # improving, declining, stable
    trend_strength = Column(Float)
    
    # Comparaisons
    class_rank = Column(Integer)
    class_percentile = Column(Float)
    
    # Métadonnées
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


class ClassStatistics(Base):
    """Statistiques pré-calculées par classe"""
    __tablename__ = "class_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiants
    class_id = Column(String(255), index=True)
    period_start = Column(Date, index=True)
    period_end = Column(Date, index=True)
    aggregation_period = Column(String(20))
    
    # Statistiques de base
    total_students = Column(Integer, default=0)
    total_courses = Column(Integer, default=0)
    total_records = Column(Integer, default=0)
    
    # Compteurs
    present_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)
    late_count = Column(Integer, default=0)
    
    # Moyennes
    average_attendance_rate = Column(Float)
    median_attendance_rate = Column(Float)
    std_attendance_rate = Column(Float)
    
    # Extrêmes
    best_attendance_rate = Column(Float)
    worst_attendance_rate = Column(Float)
    best_student_id = Column(String(255))
    worst_student_id = Column(String(255))
    
    # Métadonnées
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


# Modèles Pydantic pour les API

class StatisticsRequest(BaseModel):
    """Requête de statistiques"""
    entity_type: str = Field(..., description="Type d'entité (student, class, global)")
    entity_id: Optional[str] = Field(None, description="ID de l'entité")
    start_date: Optional[date] = Field(None, description="Date de début")
    end_date: Optional[date] = Field(None, description="Date de fin")
    statistics: List[StatisticType] = Field(default=[], description="Types de statistiques")
    aggregation_period: Optional[AggregationPeriod] = Field(None, description="Période d'agrégation")
    include_trends: bool = Field(default=True, description="Inclure les tendances")
    include_comparisons: bool = Field(default=True, description="Inclure les comparaisons")


class ChartRequest(BaseModel):
    """Requête de génération de graphique"""
    chart_type: ChartType = Field(..., description="Type de graphique")
    data_source: str = Field(..., description="Source des données")
    title: Optional[str] = Field(None, description="Titre du graphique")
    x_axis_label: Optional[str] = Field(None, description="Label axe X")
    y_axis_label: Optional[str] = Field(None, description="Label axe Y")
    width: Optional[int] = Field(None, description="Largeur en pixels")
    height: Optional[int] = Field(None, description="Hauteur en pixels")
    theme: Optional[str] = Field(None, description="Thème du graphique")
    export_format: Optional[ExportFormat] = Field(ExportFormat.PNG, description="Format d'export")


class ExportRequest(BaseModel):
    """Requête d'export de données"""
    data_type: str = Field(..., description="Type de données à exporter")
    format: ExportFormat = Field(..., description="Format d'export")
    entity_type: str = Field(..., description="Type d'entité")
    entity_id: Optional[str] = Field(None, description="ID de l'entité")
    start_date: Optional[date] = Field(None, description="Date de début")
    end_date: Optional[date] = Field(None, description="Date de fin")
    include_charts: bool = Field(default=False, description="Inclure les graphiques")
    include_raw_data: bool = Field(default=False, description="Inclure les données brutes")


class StatisticsResponse(BaseModel):
    """Réponse de statistiques"""
    entity_type: str
    entity_id: Optional[str]
    period_start: date
    period_end: date
    statistics: Dict[str, Any]
    trends: Optional[Dict[str, Any]] = None
    comparisons: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]
    generated_at: datetime
    cache_hit: bool = False


class ChartResponse(BaseModel):
    """Réponse de génération de graphique"""
    chart_id: str
    chart_type: str
    file_path: str
    file_url: str
    file_size: int
    format: str
    width: int
    height: int
    generated_at: datetime


class ExportResponse(BaseModel):
    """Réponse d'export"""
    export_id: str
    file_path: str
    file_url: str
    file_size: int
    format: str
    record_count: int
    generated_at: datetime
    expires_at: datetime


class HealthCheck(BaseModel):
    """Vérification de santé"""
    service: str
    status: str
    timestamp: datetime
    database_connected: bool
    redis_connected: bool
    cache_size: int
    last_calculation: Optional[datetime] = None


class StudentStatsResponse(BaseModel):
    """Réponse statistiques étudiant"""
    student_id: str
    period_start: date
    period_end: date
    attendance_rate: float
    total_courses: int
    present_count: int
    absent_count: int
    late_count: int
    justified_absences: int
    unjustified_absences: int
    class_rank: Optional[int] = None
    class_percentile: Optional[float] = None
    trend: Optional[str] = None
    weekly_data: List[Dict[str, Any]] = []
    course_breakdown: List[Dict[str, Any]] = []


class ClassStatsResponse(BaseModel):
    """Réponse statistiques classe"""
    class_id: str
    period_start: date
    period_end: date
    total_students: int
    average_attendance_rate: float
    median_attendance_rate: float
    best_attendance_rate: float
    worst_attendance_rate: float
    student_rankings: List[Dict[str, Any]] = []
    weekly_trends: List[Dict[str, Any]] = []
    course_comparison: List[Dict[str, Any]] = []


class GlobalStatsResponse(BaseModel):
    """Réponse statistiques globales"""
    period_start: date
    period_end: date
    total_students: int
    total_classes: int
    total_courses: int
    global_attendance_rate: float
    total_records: int
    present_count: int
    absent_count: int
    late_count: int
    monthly_trends: List[Dict[str, Any]] = []
    class_rankings: List[Dict[str, Any]] = []
    top_performers: List[Dict[str, Any]] = []
    attendance_distribution: Dict[str, Any] = {}
