"""
Configuration de la base de données pour le service de notifications
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Configuration de l'engine SQLAlchemy
if settings.database_url.startswith("sqlite"):
    # Configuration spéciale pour SQLite
    engine = create_engine(
        settings.database_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        },
        poolclass=StaticPool,
        echo=settings.debug
    )
else:
    # Configuration pour PostgreSQL
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.debug
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Métadonnées
metadata = MetaData()


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
        logger.info("🔗 Initialisation de la base de données...")
        
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Base de données initialisée")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation base de données: {e}")
        raise


def check_database_connection():
    """Vérifier la connexion à la base de données"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Erreur connexion base de données: {e}")
        return False


def get_database_stats():
    """Obtenir les statistiques de la base de données"""
    try:
        from app.models.notification import NotificationLog, NotificationTemplate, UserPreference
        
        db = SessionLocal()
        
        stats = {
            "total_notifications": db.query(NotificationLog).count(),
            "total_templates": db.query(NotificationTemplate).count(),
            "total_user_preferences": db.query(UserPreference).count(),
            "sent_notifications": db.query(NotificationLog).filter(
                NotificationLog.status == "sent"
            ).count(),
            "failed_notifications": db.query(NotificationLog).filter(
                NotificationLog.status == "failed"
            ).count(),
            "pending_notifications": db.query(NotificationLog).filter(
                NotificationLog.status == "pending"
            ).count()
        }
        
        db.close()
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération statistiques DB: {e}")
        return {}
