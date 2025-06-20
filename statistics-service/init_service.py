#!/usr/bin/env python3
"""
Script d'initialisation du Statistics Service
"""
import asyncio
import sys
import os
import logging
from datetime import date, datetime, timedelta
import argparse

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import init_database, get_database_stats, check_database_connection, check_redis_connection
from app.services.statistics_service import statistics_service
from app.services.integration_service import integration_service

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_database():
    """Initialiser la base de données"""
    logger.info("🔗 Initialisation de la base de données...")
    
    try:
        init_database()
        logger.info("✅ Base de données initialisée avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur initialisation base de données: {e}")
        return False


async def create_sample_data():
    """Créer des données d'exemple"""
    logger.info("📊 Création de données d'exemple...")
    
    try:
        from app.core.database import SessionLocal
        from app.models.statistics import AttendanceRecord
        import random
        
        db = SessionLocal()
        
        # Supprimer les anciennes données d'exemple
        db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id.like("sample_%")
        ).delete()
        
        # Créer des données d'exemple pour plusieurs étudiants et classes
        sample_data = []
        
        # 3 classes avec 10 étudiants chacune
        for class_num in range(1, 4):
            class_id = f"sample_class_{class_num:02d}"
            
            for student_num in range(1, 11):
                student_id = f"sample_student_{class_num:02d}_{student_num:02d}"
                
                # 60 jours de données
                for day_offset in range(60):
                    record_date = date.today() - timedelta(days=day_offset)
                    
                    # Simuler différents cours dans la journée
                    for course_num in range(1, 4):
                        course_id = f"sample_course_{course_num:02d}"
                        
                        # Probabilité de présence variable selon l'étudiant
                        base_attendance_rate = 0.7 + (student_num * 0.02)  # 70% à 90%
                        
                        # Variation selon le jour de la semaine
                        weekday = record_date.weekday()
                        if weekday == 0:  # Lundi
                            attendance_rate = base_attendance_rate * 0.9
                        elif weekday == 4:  # Vendredi
                            attendance_rate = base_attendance_rate * 0.85
                        else:
                            attendance_rate = base_attendance_rate
                        
                        # Déterminer le statut
                        rand = random.random()
                        if rand < attendance_rate:
                            status = "present"
                        elif rand < attendance_rate + 0.05:
                            status = "late"
                        else:
                            status = "absent"
                        
                        # Justification pour certaines absences
                        is_justified = status == "absent" and random.random() < 0.3
                        
                        record = AttendanceRecord(
                            student_id=student_id,
                            course_id=course_id,
                            class_id=class_id,
                            teacher_id=f"sample_teacher_{course_num:02d}",
                            date=record_date,
                            time_slot=f"{8 + course_num}:00-{9 + course_num}:00",
                            status=status,
                            detection_method=random.choice(["facial_recognition", "manual", "qr_code"]),
                            confidence_score=random.uniform(0.85, 0.99) if status == "present" else None,
                            is_justified=is_justified,
                            justification_id=f"just_{random.randint(1000, 9999)}" if is_justified else None
                        )
                        
                        sample_data.append(record)
        
        # Sauvegarder par lots
        batch_size = 1000
        total_records = len(sample_data)
        
        for i in range(0, total_records, batch_size):
            batch = sample_data[i:i + batch_size]
            db.add_all(batch)
            db.commit()
            logger.info(f"📝 Sauvegardé {min(i + batch_size, total_records)}/{total_records} enregistrements")
        
        db.close()
        
        logger.info(f"✅ {total_records} enregistrements d'exemple créés")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur création données d'exemple: {e}")
        return False


async def test_statistics_calculation():
    """Tester le calcul de statistiques"""
    logger.info("🧮 Test du calcul de statistiques...")
    
    try:
        # Test statistiques étudiant
        student_stats = await statistics_service.get_student_statistics(
            student_id="sample_student_01_01",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            use_cache=False
        )
        
        logger.info(f"📊 Statistiques étudiant - Taux de présence: {student_stats.get('attendance_rate', 0)}%")
        
        # Test statistiques classe
        class_stats = await statistics_service.get_class_statistics(
            class_id="sample_class_01",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            use_cache=False
        )
        
        logger.info(f"🏫 Statistiques classe - Moyenne: {class_stats.get('average_attendance_rate', 0)}%")
        
        # Test statistiques globales
        global_stats = await statistics_service.get_global_statistics(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            use_cache=False
        )
        
        logger.info(f"🌍 Statistiques globales - Taux global: {global_stats.get('global_attendance_rate', 0)}%")
        
        logger.info("✅ Calculs de statistiques validés")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test statistiques: {e}")
        return False


async def test_chart_generation():
    """Tester la génération de graphiques"""
    logger.info("📈 Test de génération de graphiques...")
    
    try:
        from app.services.chart_service import chart_service
        from app.models.statistics import ChartType, ExportFormat
        
        # Données d'exemple
        chart_data = {
            "x": ["Sem 1", "Sem 2", "Sem 3", "Sem 4"],
            "y": [85, 88, 90, 87],
            "name": "Taux de présence"
        }
        
        # Générer un graphique en ligne
        chart_result = await chart_service.generate_chart(
            chart_type=ChartType.LINE_CHART,
            data=chart_data,
            title="Test - Évolution du taux de présence",
            x_axis_label="Semaines",
            y_axis_label="Taux (%)",
            export_format=ExportFormat.PNG
        )
        
        if os.path.exists(chart_result["file_path"]):
            logger.info(f"✅ Graphique généré: {chart_result['file_path']}")
            return True
        else:
            logger.error("❌ Fichier graphique non créé")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erreur génération graphique: {e}")
        return False


async def sync_attendance_data():
    """Synchroniser les données de présence"""
    logger.info("🔄 Synchronisation des données de présence...")
    
    try:
        result = await integration_service.sync_attendance_data(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )
        
        if result["success"]:
            logger.info(f"✅ {result.get('records_synced', 0)} enregistrements synchronisés")
        else:
            logger.warning(f"⚠️ Synchronisation échouée: {result.get('error', 'Erreur inconnue')}")
        
        return result["success"]
        
    except Exception as e:
        logger.error(f"❌ Erreur synchronisation: {e}")
        return False


async def check_service_health():
    """Vérifier la santé du service"""
    logger.info("🏥 Vérification de la santé du service...")
    
    try:
        # Base de données
        db_connected = check_database_connection()
        logger.info(f"🔗 Base de données: {'✅ Connectée' if db_connected else '❌ Déconnectée'}")
        
        # Redis
        redis_connected = check_redis_connection()
        logger.info(f"🔴 Redis: {'✅ Connecté' if redis_connected else '⚠️ Non disponible'}")
        
        # Statistiques de base de données
        db_stats = get_database_stats()
        logger.info(f"📊 Enregistrements de présence: {db_stats.get('total_attendance_records', 0)}")
        logger.info(f"👥 Étudiants uniques: {db_stats.get('unique_students', 0)}")
        logger.info(f"📚 Cours uniques: {db_stats.get('unique_courses', 0)}")
        
        # Services externes
        services_health = await integration_service.check_services_health()
        logger.info("🔗 Services externes:")
        for service, status in services_health.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"  {status_icon} {service}")
        
        overall_health = db_connected
        logger.info(f"🎯 État général: {'✅ Sain' if overall_health else '❌ Problème'}")
        
        return overall_health
        
    except Exception as e:
        logger.error(f"❌ Erreur vérification santé: {e}")
        return False


async def show_service_info():
    """Afficher les informations du service"""
    logger.info("ℹ️ Informations du Statistics Service")
    logger.info("=" * 50)
    logger.info(f"📛 Nom: {settings.service_name}")
    logger.info(f"🔢 Version: {settings.service_version}")
    logger.info(f"🚪 Port: {settings.service_port}")
    logger.info(f"🐛 Debug: {settings.debug}")
    logger.info(f"🗄️ Base de données: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'Local'}")
    logger.info(f"🔴 Redis: {settings.redis_url}")
    logger.info(f"📊 Types de statistiques: {len(settings.available_stats)}")
    logger.info(f"📈 Types de graphiques: {len(settings.available_charts)}")
    logger.info(f"📤 Formats d'export: {', '.join(settings.export_formats)}")
    logger.info("=" * 50)


async def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Initialisation du Statistics Service")
    parser.add_argument("action", nargs="?", default="init", 
                       choices=["init", "sample-data", "test-stats", "test-charts", "sync", "health", "info"],
                       help="Action à exécuter")
    
    args = parser.parse_args()
    
    logger.info("🎭 Statistics Service - Script d'initialisation")
    
    if args.action == "init":
        logger.info("🚀 Initialisation complète du service...")
        
        success = True
        success &= await initialize_database()
        success &= await create_sample_data()
        success &= await test_statistics_calculation()
        success &= await test_chart_generation()
        success &= await check_service_health()
        
        if success:
            logger.info("🎉 Service initialisé avec succès!")
            await show_service_info()
        else:
            logger.error("❌ Échec de l'initialisation")
            return 1
    
    elif args.action == "sample-data":
        success = await create_sample_data()
        return 0 if success else 1
    
    elif args.action == "test-stats":
        success = await test_statistics_calculation()
        return 0 if success else 1
    
    elif args.action == "test-charts":
        success = await test_chart_generation()
        return 0 if success else 1
    
    elif args.action == "sync":
        success = await sync_attendance_data()
        return 0 if success else 1
    
    elif args.action == "health":
        success = await check_service_health()
        return 0 if success else 1
    
    elif args.action == "info":
        await show_service_info()
        return 0
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
