#!/usr/bin/env python3
"""
Script d'initialisation du notification-service
"""
import asyncio
import logging
import sys
import os

# Ajouter le répertoire app au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database, SessionLocal
from app.services.template_service import template_service
from app.models.notification import UserPreference

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_service():
    """Initialiser le service de notifications"""
    try:
        logger.info("🚀 Initialisation du Notification Service...")
        
        # Initialiser la base de données
        logger.info("📊 Initialisation de la base de données...")
        init_database()
        logger.info("✅ Base de données initialisée")
        
        # Initialiser les templates par défaut
        logger.info("📝 Initialisation des templates par défaut...")
        await template_service.initialize_default_templates()
        logger.info("✅ Templates par défaut créés")
        
        # Créer des préférences utilisateur par défaut
        logger.info("👤 Création des préférences utilisateur par défaut...")
        await create_default_user_preferences()
        logger.info("✅ Préférences utilisateur créées")
        
        logger.info("🎉 Notification Service initialisé avec succès !")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        raise


async def create_default_user_preferences():
    """Créer des préférences utilisateur par défaut pour les tests"""
    db = SessionLocal()
    
    try:
        # Utilisateurs de test
        test_users = [
            {
                "user_id": "student_001",
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "absence_notifications": True,
                "justification_notifications": True,
                "message_notifications": True,
                "report_notifications": True,
                "immediate_alerts": True,
                "daily_digest": True,
                "weekly_report": True,
                "timezone": "Europe/Paris",
                "language": "fr"
            },
            {
                "user_id": "parent_001",
                "email_enabled": True,
                "sms_enabled": True,
                "push_enabled": True,
                "absence_notifications": True,
                "justification_notifications": True,
                "message_notifications": True,
                "report_notifications": True,
                "immediate_alerts": True,
                "daily_digest": True,
                "weekly_report": True,
                "timezone": "Europe/Paris",
                "language": "fr"
            },
            {
                "user_id": "teacher_001",
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "absence_notifications": False,
                "justification_notifications": True,
                "message_notifications": True,
                "report_notifications": False,
                "immediate_alerts": True,
                "daily_digest": False,
                "weekly_report": False,
                "timezone": "Europe/Paris",
                "language": "fr"
            },
            {
                "user_id": "admin_001",
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "absence_notifications": True,
                "justification_notifications": True,
                "message_notifications": True,
                "report_notifications": True,
                "immediate_alerts": True,
                "daily_digest": True,
                "weekly_report": True,
                "timezone": "Europe/Paris",
                "language": "fr"
            }
        ]
        
        for user_data in test_users:
            # Vérifier si l'utilisateur existe déjà
            existing = db.query(UserPreference).filter(
                UserPreference.user_id == user_data["user_id"]
            ).first()
            
            if not existing:
                user_pref = UserPreference(**user_data)
                db.add(user_pref)
                logger.info(f"Préférences créées pour {user_data['user_id']}")
        
        db.commit()
        logger.info("✅ Préférences utilisateur par défaut créées")
        
    except Exception as e:
        logger.error(f"❌ Erreur création préférences: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def cleanup_service():
    """Nettoyer le service (pour les tests)"""
    try:
        logger.info("🧹 Nettoyage du service...")
        
        from app.models.notification import NotificationLog, NotificationTemplate, UserPreference, EventQueue
        
        db = SessionLocal()
        
        # Supprimer toutes les données
        db.query(NotificationLog).delete()
        db.query(EventQueue).delete()
        db.query(UserPreference).delete()
        # Ne pas supprimer les templates par défaut
        
        db.commit()
        db.close()
        
        logger.info("✅ Service nettoyé")
        
    except Exception as e:
        logger.error(f"❌ Erreur nettoyage: {e}")
        raise


async def show_service_stats():
    """Afficher les statistiques du service"""
    try:
        from app.core.database import get_database_stats
        
        logger.info("📊 Statistiques du service:")
        
        stats = get_database_stats()
        
        print(f"📧 Notifications totales: {stats.get('total_notifications', 0)}")
        print(f"✅ Notifications envoyées: {stats.get('sent_notifications', 0)}")
        print(f"❌ Notifications échouées: {stats.get('failed_notifications', 0)}")
        print(f"⏳ Notifications en attente: {stats.get('pending_notifications', 0)}")
        print(f"📝 Templates: {stats.get('total_templates', 0)}")
        print(f"👤 Préférences utilisateur: {stats.get('total_user_preferences', 0)}")
        
    except Exception as e:
        logger.error(f"❌ Erreur statistiques: {e}")
        raise


async def test_email_sending():
    """Tester l'envoi d'email"""
    try:
        logger.info("📧 Test d'envoi d'email...")
        
        from app.services.email_service import email_service
        
        # Test d'envoi simple
        result = await email_service.send_email(
            to_email="test@example.com",
            subject="Test Notification Service",
            content="Ceci est un test du service de notifications PresencePro.",
            html_content="<h1>Test</h1><p>Ceci est un test du service de notifications PresencePro.</p>"
        )
        
        if result.get("success"):
            logger.info("✅ Email de test envoyé avec succès")
            if result.get("filepath"):
                logger.info(f"📁 Email sauvegardé: {result['filepath']}")
        else:
            logger.error(f"❌ Échec envoi email: {result.get('error')}")
        
    except Exception as e:
        logger.error(f"❌ Erreur test email: {e}")
        raise


async def main():
    """Fonction principale"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            await initialize_service()
        elif command == "cleanup":
            await cleanup_service()
        elif command == "stats":
            await show_service_stats()
        elif command == "test-email":
            await test_email_sending()
        else:
            print("Commandes disponibles: init, cleanup, stats, test-email")
            sys.exit(1)
    else:
        # Initialisation par défaut
        await initialize_service()


if __name__ == "__main__":
    asyncio.run(main())
