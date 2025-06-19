#!/usr/bin/env python3
"""
Script d'initialisation de la base de données pour le service de justifications
"""
import os
import sys
import logging
from datetime import datetime, timedelta

# Ajouter le répertoire app au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, SessionLocal, create_tables
from app.core.config import settings
from app.models.justification import *
from app.services.integration_service import IntegrationService


def test_database_connection():
    """Tester la connexion à la base de données"""
    print("\n📊 Test de connexion à la base de données...")
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Connexion base de données réussie")
            return True
    except Exception as e:
        print(f"❌ Erreur connexion base de données: {e}")
        return False


def create_sample_data():
    """Créer des données d'exemple"""
    print("\n👥 Création de données d'exemple...")
    
    try:
        db = SessionLocal()
        
        # Vérifier si des données existent déjà
        existing_count = db.query(Justification).count()
        if existing_count > 0:
            print(f"✅ Données existantes trouvées ({existing_count} justifications)")
            db.close()
            return True
        
        # Créer des templates de justification
        templates = [
            JustificationTemplate(
                name="Certificat médical",
                description="Justification pour absence médicale",
                justification_type=JustificationType.MEDICAL,
                title_template="Absence pour raison médicale",
                description_template="Je soussigné(e) certifie que l'étudiant(e) était dans l'impossibilité de se présenter en cours pour raison médicale.",
                default_priority=JustificationPriority.HIGH,
                requires_documents=True,
                max_absence_days=7,
                created_by="system"
            ),
            JustificationTemplate(
                name="Problème de transport",
                description="Justification pour problème de transport",
                justification_type=JustificationType.TRANSPORT,
                title_template="Retard/Absence due à un problème de transport",
                description_template="En raison d'un problème de transport (grève, panne, accident), je n'ai pas pu me présenter en cours.",
                default_priority=JustificationPriority.MEDIUM,
                requires_documents=False,
                max_absence_days=1,
                created_by="system"
            ),
            JustificationTemplate(
                name="Événement familial",
                description="Justification pour événement familial",
                justification_type=JustificationType.FAMILY,
                title_template="Absence pour événement familial",
                description_template="Je sollicite une autorisation d'absence pour un événement familial important.",
                default_priority=JustificationPriority.MEDIUM,
                requires_documents=True,
                max_absence_days=3,
                created_by="system"
            )
        ]
        
        for template in templates:
            db.add(template)
        
        # Créer des justifications d'exemple
        sample_justifications = [
            Justification(
                student_id="student_001",
                course_id=1,
                title="Absence pour rendez-vous médical",
                description="Rendez-vous médical urgent chez le dentiste. Certificat médical fourni.",
                justification_type=JustificationType.MEDICAL,
                priority=JustificationPriority.HIGH,
                absence_start_date=datetime.now() - timedelta(days=2),
                absence_end_date=datetime.now() - timedelta(days=2),
                status=JustificationStatus.ADMIN_APPROVED,
                parent_approval_required=True,
                admin_validation_required=True,
                parent_approved_by="parent_001",
                parent_approved_at=datetime.now() - timedelta(days=1),
                admin_validated_by="admin_001",
                admin_validated_at=datetime.now() - timedelta(hours=2),
                submission_deadline=datetime.now() + timedelta(days=5),
                expires_at=datetime.now() + timedelta(days=28),
                created_by="student_001",
                notes="Certificat médical en pièce jointe"
            ),
            Justification(
                student_id="student_002",
                course_id=2,
                title="Retard dû à une grève des transports",
                description="Grève SNCF, impossible d'arriver à l'heure pour le cours de 8h.",
                justification_type=JustificationType.TRANSPORT,
                priority=JustificationPriority.MEDIUM,
                absence_start_date=datetime.now() - timedelta(days=1),
                absence_end_date=datetime.now() - timedelta(days=1),
                status=JustificationStatus.PARENT_PENDING,
                parent_approval_required=True,
                admin_validation_required=True,
                submission_deadline=datetime.now() + timedelta(days=6),
                expires_at=datetime.now() + timedelta(days=29),
                created_by="student_002"
            ),
            Justification(
                student_id="student_003",
                course_id=1,
                title="Absence pour mariage familial",
                description="Mariage de ma sœur, événement familial important nécessitant ma présence.",
                justification_type=JustificationType.FAMILY,
                priority=JustificationPriority.MEDIUM,
                absence_start_date=datetime.now() + timedelta(days=7),
                absence_end_date=datetime.now() + timedelta(days=8),
                status=JustificationStatus.DRAFT,
                parent_approval_required=True,
                admin_validation_required=True,
                submission_deadline=datetime.now() + timedelta(days=14),
                expires_at=datetime.now() + timedelta(days=37),
                created_by="student_003",
                notes="Faire-part de mariage en pièce jointe"
            )
        ]
        
        for justification in sample_justifications:
            db.add(justification)
        
        db.commit()
        
        # Créer l'historique pour les justifications
        for i, justification in enumerate(sample_justifications, 1):
            db.refresh(justification)
            
            # Historique de création
            history_created = JustificationHistory(
                justification_id=justification.id,
                action="created",
                old_status=None,
                new_status=JustificationStatus.DRAFT.value,
                comment="Justification créée",
                changed_by=justification.created_by
            )
            db.add(history_created)
            
            # Historique supplémentaire pour les justifications non-draft
            if justification.status != JustificationStatus.DRAFT:
                history_submitted = JustificationHistory(
                    justification_id=justification.id,
                    action="submitted",
                    old_status=JustificationStatus.DRAFT.value,
                    new_status=JustificationStatus.PARENT_PENDING.value,
                    comment="Justification soumise pour approbation",
                    changed_by=justification.created_by
                )
                db.add(history_submitted)
                
                if justification.parent_approved_by:
                    history_parent = JustificationHistory(
                        justification_id=justification.id,
                        action="parent_approved",
                        old_status=JustificationStatus.PARENT_PENDING.value,
                        new_status=JustificationStatus.ADMIN_PENDING.value,
                        comment="Approuvé par les parents",
                        changed_by=justification.parent_approved_by
                    )
                    db.add(history_parent)
                
                if justification.admin_validated_by:
                    history_admin = JustificationHistory(
                        justification_id=justification.id,
                        action="admin_approved",
                        old_status=JustificationStatus.ADMIN_PENDING.value,
                        new_status=JustificationStatus.ADMIN_APPROVED.value,
                        comment="Validé par l'administration",
                        changed_by=justification.admin_validated_by
                    )
                    db.add(history_admin)
        
        db.commit()
        db.close()
        
        print("✅ Données d'exemple créées")
        print("   - 3 templates de justification")
        print("   - 3 justifications d'exemple")
        print("   - Historique des modifications")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création données d'exemple: {e}")
        return False


def test_integration_services():
    """Tester l'intégration avec les autres services"""
    print("\n🔗 Test d'intégration avec les autres services...")
    
    integration_service = IntegrationService()
    services = {
        "auth-service": "auth",
        "user-service": "user", 
        "course-service": "course",
        "attendance-service": "attendance"
    }
    
    available_services = 0
    
    for service_name, service_key in services.items():
        try:
            is_available = integration_service.is_service_available(service_key)
            status = "✅" if is_available else "❌"
            print(f"   {status} {service_name}: {'Disponible' if is_available else 'Non disponible'}")
            if is_available:
                available_services += 1
        except Exception as e:
            print(f"   ❌ {service_name}: Erreur - {e}")
    
    print(f"\n📈 Services disponibles: {available_services}/{len(services)}")
    
    if available_services == 0:
        print("⚠️  Aucun service externe disponible - Le service fonctionnera en mode autonome")
    
    return available_services > 0


def main():
    """Fonction principale d'initialisation"""
    print("🚀 Initialisation du service de justifications PresencePro")
    print("=" * 70)
    print(f"📊 Base de données: {settings.database_url}")
    
    # Test de connexion
    if not test_database_connection():
        print("💥 Échec de l'initialisation - Problème de base de données")
        return False
    
    # Création des tables
    print("\n🔧 Création des tables de base de données...")
    try:
        create_tables()
        print("✅ Tables créées avec succès")
    except Exception as e:
        print(f"❌ Erreur création tables: {e}")
        return False
    
    # Test d'intégration
    test_integration_services()
    
    # Création des données d'exemple
    if not create_sample_data():
        print("💥 Échec de l'initialisation - Problème création données")
        return False
    
    # Créer le répertoire d'upload
    print("\n📁 Configuration du répertoire d'upload...")
    try:
        os.makedirs(settings.upload_dir, exist_ok=True)
        print(f"✅ Répertoire d'upload créé: {settings.upload_dir}")
    except Exception as e:
        print(f"❌ Erreur création répertoire upload: {e}")
    
    print("\n🎉 Initialisation terminée avec succès!")
    print("\n📝 Prochaines étapes:")
    print("   1. Lancez le service: uvicorn app.main:app --reload --port 8006")
    print("   2. Testez l'API: http://localhost:8006/docs")
    print("   3. Créez une justification: POST /api/v1/justifications/create")
    print("   4. Consultez le statut: GET /api/v1/justifications/status/{id}")
    print("\n🎊 Service de justifications prêt à être utilisé!")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
