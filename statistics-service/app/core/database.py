"""
Configuration de la base de données PostgreSQL pour le service de statistiques
"""
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging
import redis
from typing import Optional

from .config import settings

logger = logging.getLogger(__name__)

# Configuration de l'engine PostgreSQL
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Métadonnées
metadata = MetaData()

# Redis client pour le cache
redis_client: Optional[redis.Redis] = None

if settings.cache_enabled:
    try:
        redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        # Test de connexion
        redis_client.ping()
        logger.info("✅ Connexion Redis établie pour le cache")
    except Exception as e:
        logger.warning(f"⚠️ Redis non disponible, cache désactivé: {e}")
        redis_client = None


def get_database():
    """Obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialiser la base de données"""
    try:
        logger.info("🔗 Initialisation de la base de données PostgreSQL...")
        
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        
        # Créer les index pour les performances
        create_performance_indexes()
        
        # Créer les vues pour les statistiques
        create_statistics_views()
        
        logger.info("✅ Base de données initialisée")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation base de données: {e}")
        raise


def create_performance_indexes():
    """Créer les index pour optimiser les performances"""
    try:
        with engine.connect() as connection:
            # Index pour les requêtes de statistiques fréquentes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_attendance_records_student_date ON attendance_records(student_id, date);",
                "CREATE INDEX IF NOT EXISTS idx_attendance_records_course_date ON attendance_records(course_id, date);",
                "CREATE INDEX IF NOT EXISTS idx_attendance_records_status ON attendance_records(status);",
                "CREATE INDEX IF NOT EXISTS idx_attendance_records_date_range ON attendance_records(date) WHERE date >= CURRENT_DATE - INTERVAL '1 year';",
                "CREATE INDEX IF NOT EXISTS idx_statistics_cache_key ON statistics_cache(cache_key);",
                "CREATE INDEX IF NOT EXISTS idx_statistics_cache_created ON statistics_cache(created_at);",
            ]
            
            for index_sql in indexes:
                try:
                    connection.execute(text(index_sql))
                    connection.commit()
                except Exception as e:
                    logger.warning(f"Index déjà existant ou erreur: {e}")
        
        logger.info("✅ Index de performance créés")
        
    except Exception as e:
        logger.error(f"❌ Erreur création index: {e}")


def create_statistics_views():
    """Créer les vues pour les statistiques pré-calculées"""
    try:
        with engine.connect() as connection:
            # Vue pour les statistiques quotidiennes par étudiant
            daily_stats_view = """
            CREATE OR REPLACE VIEW daily_student_stats AS
            SELECT 
                student_id,
                date,
                COUNT(*) as total_courses,
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent_count,
                SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as late_count,
                ROUND(
                    (SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END)::float / COUNT(*)) * 100, 2
                ) as attendance_rate
            FROM attendance_records 
            GROUP BY student_id, date;
            """
            
            # Vue pour les statistiques hebdomadaires par classe
            weekly_class_stats_view = """
            CREATE OR REPLACE VIEW weekly_class_stats AS
            SELECT 
                c.class_id,
                DATE_TRUNC('week', ar.date) as week_start,
                COUNT(DISTINCT ar.student_id) as total_students,
                COUNT(*) as total_records,
                SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN ar.status = 'absent' THEN 1 ELSE 0 END) as absent_count,
                ROUND(
                    (SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END)::float / COUNT(*)) * 100, 2
                ) as attendance_rate
            FROM attendance_records ar
            JOIN courses c ON ar.course_id = c.course_id
            GROUP BY c.class_id, DATE_TRUNC('week', ar.date);
            """
            
            # Vue pour les statistiques mensuelles globales
            monthly_global_stats_view = """
            CREATE OR REPLACE VIEW monthly_global_stats AS
            SELECT 
                DATE_TRUNC('month', date) as month_start,
                COUNT(DISTINCT student_id) as active_students,
                COUNT(*) as total_records,
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent_count,
                SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as late_count,
                ROUND(
                    (SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END)::float / COUNT(*)) * 100, 2
                ) as attendance_rate
            FROM attendance_records 
            GROUP BY DATE_TRUNC('month', date);
            """
            
            views = [daily_stats_view, weekly_class_stats_view, monthly_global_stats_view]
            
            for view_sql in views:
                try:
                    connection.execute(text(view_sql))
                    connection.commit()
                except Exception as e:
                    logger.warning(f"Vue déjà existante ou erreur: {e}")
        
        logger.info("✅ Vues statistiques créées")
        
    except Exception as e:
        logger.error(f"❌ Erreur création vues: {e}")


def check_database_connection():
    """Vérifier la connexion à la base de données"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Erreur connexion base de données: {e}")
        return False


def check_redis_connection():
    """Vérifier la connexion Redis"""
    if not redis_client:
        return False
    
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Erreur connexion Redis: {e}")
        return False


def get_database_stats():
    """Obtenir les statistiques de la base de données"""
    try:
        from app.models.statistics import StatisticsCache, AttendanceRecord
        
        db = SessionLocal()
        
        # Statistiques de base
        with engine.connect() as connection:
            # Nombre total d'enregistrements de présence
            total_records = connection.execute(
                text("SELECT COUNT(*) FROM attendance_records")
            ).scalar() or 0
            
            # Nombre d'étudiants uniques
            unique_students = connection.execute(
                text("SELECT COUNT(DISTINCT student_id) FROM attendance_records")
            ).scalar() or 0
            
            # Nombre de cours uniques
            unique_courses = connection.execute(
                text("SELECT COUNT(DISTINCT course_id) FROM attendance_records")
            ).scalar() or 0
            
            # Taux de présence global
            attendance_rate = connection.execute(
                text("""
                    SELECT ROUND(
                        (CAST(SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) * 100, 2
                    ) FROM attendance_records
                """)
            ).scalar() or 0
        
        # Statistiques du cache
        cache_stats = db.query(StatisticsCache).count() if StatisticsCache else 0
        
        db.close()
        
        return {
            "total_attendance_records": total_records,
            "unique_students": unique_students,
            "unique_courses": unique_courses,
            "global_attendance_rate": attendance_rate,
            "cached_statistics": cache_stats,
            "redis_connected": check_redis_connection()
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération statistiques DB: {e}")
        return {}


def get_cache_key(prefix: str, **kwargs) -> str:
    """Générer une clé de cache"""
    key_parts = [prefix]
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}:{value}")
    return ":".join(key_parts)


def get_from_cache(key: str):
    """Récupérer une valeur du cache Redis"""
    if not redis_client:
        return None
    
    try:
        return redis_client.get(key)
    except Exception as e:
        logger.error(f"Erreur lecture cache: {e}")
        return None


def set_cache(key: str, value: str, ttl: int = None):
    """Stocker une valeur dans le cache Redis"""
    if not redis_client:
        return False
    
    try:
        ttl = ttl or settings.cache_ttl
        redis_client.setex(key, ttl, value)
        return True
    except Exception as e:
        logger.error(f"Erreur écriture cache: {e}")
        return False


def clear_cache_pattern(pattern: str):
    """Supprimer les clés de cache correspondant à un pattern"""
    if not redis_client:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Erreur suppression cache: {e}")
        return 0
