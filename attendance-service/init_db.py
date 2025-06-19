#!/usr/bin/env python3
"""
Script d'initialisation de la base de données pour le service de présences
"""
import os
import sys
import logging
from datetime import datetime, date, timedelta
import asyncio

# Ajouter le répertoire app au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import engine, create_tables
from app.core.config import settings
from app.models.attendance import *
from app.services.integration_service import IntegrationService


def init_database():
    """Initialiser la base de données"""
    print("🚀 Initialisation du service de présences PresencePro")
    print("=" * 70)
    print(f"📊 Base de données: {settings.database_url}")
    
    try:
        # Créer les tables
        print("\n🔧 Création des tables de base de données...")
        create_tables()
        print("✅ Tables créées avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création tables: {e}")
        return False


def test_database_connection():
    """Tester la connexion à la base de données"""
    print("\n📊 Test de connexion à la base de données...")
    
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Connexion PostgreSQL réussie")
            return True
            
    except Exception as e:
        print(f"❌ Erreur connexion base de données: {e}")
        print("💡 Vérifiez que PostgreSQL est démarré et que la base de données existe")
        return False


async def test_service_integration():
    """Tester l'intégration avec les autres services"""
    print("\n🔗 Test d'intégration avec les autres services...")
    
    integration_service = IntegrationService()
    
    services = {
        "auth-service": "auth",
        "user-service": "user", 
        "course-service": "course",
        "face-recognition-service": "face_recognition"
    }
    
    available_count = 0
    
    for service_name, service_key in services.items():
        try:
            available = integration_service.is_service_available(service_key)
            status = "✅" if available else "❌"
            print(f"   {status} {service_name}: {'Disponible' if available else 'Non disponible'}")
            
            if available:
                available_count += 1
                
        except Exception as e:
            print(f"   ❌ {service_name}: Erreur - {e}")
    
    print(f"\n📈 Services disponibles: {available_count}/{len(services)}")
    
    if available_count == 0:
        print("⚠️  Aucun service externe disponible - Le service fonctionnera en mode autonome")
    elif available_count < len(services):
        print("⚠️  Certains services ne sont pas disponibles - Fonctionnalités limitées")
    else:
        print("🎉 Tous les services sont disponibles - Intégration complète")
    
    return available_count > 0


def create_sample_data():
    """Créer des données d'exemple"""
    print("\n👥 Création de données d'exemple...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        from app.models.attendance import Attendance, AttendanceSession, AttendanceRule
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Vérifier si des données existent déjà
        existing_count = db.query(Attendance).count()
        if existing_count > 0:
            print(f"ℹ️  {existing_count} présences déjà en base - Pas de données d'exemple ajoutées")
            db.close()
            return True
        
        # Créer des règles de présence par défaut
        default_rule = AttendanceRule(
            name="Règle par défaut",
            description="Règle de présence standard pour tous les cours",
            auto_mark_absent_after_minutes=120,
            late_threshold_minutes=10,
            grace_period_minutes=15,
            require_excuse_for_absence=False,
            allow_late_marking=True,
            is_active=True,
            priority=0,
            created_by="system"
        )
        
        db.add(default_rule)
        
        # Créer quelques présences d'exemple
        sample_attendances = [
            Attendance(
                student_id="student_001",
                course_id=1,
                schedule_id=1,
                status=AttendanceStatus.PRESENT,
                method=AttendanceMethod.MANUAL,
                scheduled_start_time=datetime.now() - timedelta(hours=2),
                scheduled_end_time=datetime.now() - timedelta(hours=1),
                actual_arrival_time=datetime.now() - timedelta(hours=2, minutes=5),
                marked_at=datetime.now() - timedelta(hours=2),
                location="Salle A101",
                notes="Présence normale",
                is_validated=True,
                created_by="system"
            ),
            Attendance(
                student_id="student_002",
                course_id=1,
                schedule_id=1,
                status=AttendanceStatus.LATE,
                method=AttendanceMethod.FACE_RECOGNITION,
                scheduled_start_time=datetime.now() - timedelta(hours=2),
                scheduled_end_time=datetime.now() - timedelta(hours=1),
                actual_arrival_time=datetime.now() - timedelta(hours=1, minutes=45),
                marked_at=datetime.now() - timedelta(hours=1, minutes=45),
                location="Salle A101",
                confidence_score=0.95,
                notes="Reconnaissance faciale - retard de 15 minutes",
                is_validated=True,
                created_by="face-recognition-service"
            ),
            Attendance(
                student_id="student_003",
                course_id=1,
                schedule_id=1,
                status=AttendanceStatus.ABSENT,
                method=AttendanceMethod.MANUAL,
                scheduled_start_time=datetime.now() - timedelta(hours=2),
                scheduled_end_time=datetime.now() - timedelta(hours=1),
                marked_at=datetime.now() - timedelta(hours=1),
                location="Salle A101",
                notes="Absence non justifiée",
                is_validated=True,
                created_by="teacher_001"
            )
        ]
        
        for attendance in sample_attendances:
            db.add(attendance)
        
        # Créer une session d'exemple
        sample_session = AttendanceSession(
            session_name="Cours de Mathématiques - Séance 1",
            course_id=1,
            schedule_id=1,
            start_time=datetime.now() - timedelta(hours=2),
            end_time=datetime.now() - timedelta(hours=1),
            auto_mark_absent=True,
            grace_period_minutes=15,
            is_active=False,
            is_closed=True,
            closed_at=datetime.now() - timedelta(hours=1),
            closed_by="teacher_001",
            total_students=3,
            present_count=1,
            absent_count=1,
            late_count=1,
            created_by="teacher_001"
        )
        
        db.add(sample_session)
        
        db.commit()
        db.close()
        
        print("✅ Données d'exemple créées")
        print("   - 1 règle de présence par défaut")
        print("   - 3 présences d'exemple")
        print("   - 1 session d'exemple")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création données d'exemple: {e}")
        return False


def test_attendance_features():
    """Tester les fonctionnalités de présence"""
    print("\n🧪 Test des fonctionnalités de présence...")

    try:
        from sqlalchemy.orm import sessionmaker
        from app.services.attendance_service import AttendanceService
        from app.services.alert_service import AlertService

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        # Test du service de présence
        attendance_service = AttendanceService(db)

        # Test de récupération des statistiques
        stats = attendance_service.get_attendance_stats()
        print(f"✅ Test statistiques réussi - {stats.total_attendances} présences en base")

        # Test du service d'alertes
        alert_service = AlertService(db)
        pending_count = alert_service.get_pending_alerts_count()
        print(f"✅ Test alertes réussi - {pending_count} alertes en attente")

        db.close()

        return True

    except Exception as e:
        print(f"❌ Erreur test fonctionnalités: {e}")
        return False


async def main():
    """Fonction principale"""
    success = True
    
    # Test de connexion base de données
    if not test_database_connection():
        success = False
    
    # Initialisation de la base de données
    if success and not init_database():
        success = False
    
    # Test d'intégration services
    if success:
        await test_service_integration()
    
    # Création de données d'exemple
    if success and not create_sample_data():
        success = False
    
    # Test des fonctionnalités
    if success and not test_attendance_features():
        success = False
    
    if success:
        print("\n🎉 Initialisation terminée avec succès!")
        print("\n📝 Prochaines étapes:")
        print("   1. Lancez le service: uvicorn app.main:app --reload --port 8005")
        print("   2. Testez l'API: http://localhost:8005/docs")
        print("   3. Marquez des présences: POST /api/v1/attendance/mark")
        print("   4. Consultez les rapports: GET /api/v1/reports/student/{id}")
        print("\n🎊 Service de présences prêt à être utilisé!")
    else:
        print("\n💥 Échec de l'initialisation")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
