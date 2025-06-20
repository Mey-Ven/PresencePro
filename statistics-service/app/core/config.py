"""
Configuration du service de statistiques
"""
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any


class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "statistics-service"
    service_version: str = "1.0.0"
    service_port: int = 8009
    host: str = "0.0.0.0"
    debug: bool = True
    
    # Database Configuration - PostgreSQL (SQLite en développement)
    database_url: str = "sqlite:///./statistics.db"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "presencepro_statistics"
    database_user: str = "postgres"
    database_password: str = "password"
    
    # Redis Configuration (pour cache)
    redis_url: str = "redis://localhost:6379/1"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 1
    redis_password: Optional[str] = None
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 heure
    
    # Integration avec autres services
    auth_service_url: str = "http://localhost:8001"
    user_service_url: str = "http://localhost:8002"
    course_service_url: str = "http://localhost:8003"
    attendance_service_url: str = "http://localhost:8005"
    justification_service_url: str = "http://localhost:8006"
    
    # Security
    secret_key: str = "statistics-service-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Statistics Configuration
    default_period_days: int = 30
    max_period_days: int = 365
    min_data_points: int = 5
    
    # Chart Configuration
    chart_width: int = 1200
    chart_height: int = 800
    chart_dpi: int = 300
    chart_format: str = "png"  # png, jpg, svg, pdf
    chart_theme: str = "plotly_white"  # plotly, plotly_white, plotly_dark
    
    # Export Configuration
    export_dir: str = "./exports"
    max_export_size_mb: int = 100
    export_formats: List[str] = ["json", "csv", "xlsx", "pdf"]
    
    # Performance Configuration
    max_concurrent_requests: int = 100
    query_timeout_seconds: int = 30
    batch_size: int = 1000
    
    # Statistics Types
    available_stats: Dict[str, bool] = {
        "attendance_rate": True,
        "absence_count": True,
        "tardiness_count": True,
        "justified_absences": True,
        "unjustified_absences": True,
        "weekly_trends": True,
        "monthly_trends": True,
        "course_comparison": True,
        "student_ranking": True,
        "class_average": True
    }
    
    # Chart Types
    available_charts: Dict[str, bool] = {
        "line_chart": True,
        "bar_chart": True,
        "pie_chart": True,
        "heatmap": True,
        "histogram": True,
        "box_plot": True,
        "scatter_plot": True,
        "area_chart": True
    }
    
    # Aggregation Periods
    aggregation_periods: List[str] = [
        "daily", "weekly", "monthly", "quarterly", "yearly"
    ]
    
    # Data Retention
    raw_data_retention_days: int = 90
    aggregated_data_retention_days: int = 730  # 2 ans
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/statistics.log"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9091
    
    # Development
    mock_data_enabled: bool = False
    sample_data_size: int = 1000
    
    # API Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Notification Integration
    notification_service_url: str = "http://localhost:8008"
    send_report_notifications: bool = True
    
    # Report Scheduling
    daily_reports_enabled: bool = True
    weekly_reports_enabled: bool = True
    monthly_reports_enabled: bool = True
    report_recipients: List[str] = ["admin@presencepro.com"]
    
    # Data Sources Priority
    primary_data_source: str = "attendance_service"
    fallback_data_sources: List[str] = ["database_direct"]
    
    # Statistical Calculations
    confidence_level: float = 0.95
    significance_level: float = 0.05
    outlier_detection_enabled: bool = True
    outlier_threshold: float = 2.0  # Standard deviations
    
    # Internationalization
    default_language: str = "fr"
    supported_languages: List[str] = ["fr", "en"]
    timezone: str = "Europe/Paris"
    
    # Feature Flags
    features: Dict[str, bool] = {
        "advanced_analytics": True,
        "predictive_modeling": False,
        "real_time_stats": True,
        "custom_reports": True,
        "data_export": True,
        "chart_generation": True,
        "email_reports": True,
        "api_access": True
    }
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorer les variables d'environnement supplémentaires


settings = Settings()
