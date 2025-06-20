#!/usr/bin/env python3
"""
Script de démarrage des workers Celery
"""
import os
import sys
import subprocess
import logging

# Ajouter le répertoire app au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_celery_worker():
    """Démarrer un worker Celery"""
    try:
        logger.info("🚀 Démarrage du worker Celery...")
        
        # Commande Celery
        cmd = [
            "celery",
            "-A", "app.core.celery_app:celery_app",
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "--queues=email,sms,push,events",
            "--hostname=worker@%h"
        ]
        
        # Démarrer le worker
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du worker Celery")
    except Exception as e:
        logger.error(f"❌ Erreur worker Celery: {e}")
        raise


def start_celery_beat():
    """Démarrer le scheduler Celery Beat"""
    try:
        logger.info("⏰ Démarrage du scheduler Celery Beat...")
        
        # Commande Celery Beat
        cmd = [
            "celery",
            "-A", "app.core.celery_app:celery_app",
            "beat",
            "--loglevel=info",
            "--schedule=/tmp/celerybeat-schedule"
        ]
        
        # Démarrer le scheduler
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du scheduler Celery Beat")
    except Exception as e:
        logger.error(f"❌ Erreur scheduler Celery: {e}")
        raise


def start_celery_flower():
    """Démarrer Flower pour le monitoring"""
    try:
        logger.info("🌸 Démarrage de Flower (monitoring Celery)...")
        
        # Commande Flower
        cmd = [
            "celery",
            "-A", "app.core.celery_app:celery_app",
            "flower",
            "--port=5555",
            "--broker=" + settings.celery_broker_url
        ]
        
        # Démarrer Flower
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt de Flower")
    except Exception as e:
        logger.error(f"❌ Erreur Flower: {e}")
        raise


def show_celery_status():
    """Afficher le statut de Celery"""
    try:
        logger.info("📊 Statut Celery...")
        
        # Commande de statut
        cmd = [
            "celery",
            "-A", "app.core.celery_app:celery_app",
            "inspect", "stats"
        ]
        
        subprocess.run(cmd, check=True)
        
    except Exception as e:
        logger.error(f"❌ Erreur statut Celery: {e}")


def purge_celery_queues():
    """Vider les queues Celery"""
    try:
        logger.info("🧹 Vidage des queues Celery...")
        
        # Commande de purge
        cmd = [
            "celery",
            "-A", "app.core.celery_app:celery_app",
            "purge",
            "-f"
        ]
        
        subprocess.run(cmd, check=True)
        logger.info("✅ Queues vidées")
        
    except Exception as e:
        logger.error(f"❌ Erreur purge queues: {e}")


def main():
    """Fonction principale"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python start_celery.py [worker|beat|flower|status|purge]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "worker":
        start_celery_worker()
    elif command == "beat":
        start_celery_beat()
    elif command == "flower":
        start_celery_flower()
    elif command == "status":
        show_celery_status()
    elif command == "purge":
        purge_celery_queues()
    else:
        print("Commandes disponibles: worker, beat, flower, status, purge")
        sys.exit(1)


if __name__ == "__main__":
    main()
