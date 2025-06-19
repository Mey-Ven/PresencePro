#!/usr/bin/env python3
"""
Script de test du service de justifications PresencePro
"""
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any


class JustificationServiceTester:
    """Testeur pour le service de justifications"""
    
    def __init__(self, base_url: str = "http://localhost:8006"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
    
    def test_health_check(self) -> bool:
        """Tester le health check du service"""
        print("🏥 Test de santé du service...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Service en bonne santé")
                print(f"   📊 Base de données: {'✅' if data.get('database_connected') else '❌'}")
                print(f"   📈 Total justifications: {data.get('total_justifications', 0)}")
                print(f"   ⏳ Approbations en attente: {data.get('pending_approvals', 0)}")
                print(f"   🔍 Validations en attente: {data.get('pending_validations', 0)}")
                print(f"   📁 Répertoire upload: {'✅' if data.get('upload_directory_writable') else '❌'}")
                return True
            else:
                print(f"❌ Service non disponible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur health check: {e}")
            return False
    
    def test_create_justification(self) -> Dict[str, Any]:
        """Tester la création d'une justification"""
        print("\n📝 Test de création de justification...")
        try:
            justification_data = {
                "title": "Test - Absence pour rendez-vous médical",
                "description": "Rendez-vous médical urgent chez le spécialiste. Certificat médical fourni en pièce jointe.",
                "justification_type": "medical",
                "priority": "high",
                "absence_start_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "absence_end_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "course_id": 1,
                "notes": "Test automatisé du service"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/justifications/create",
                json=justification_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Justification créée avec succès")
                print(f"   📋 ID: {data.get('id')}")
                print(f"   📊 Statut: {data.get('status')}")
                print(f"   👤 Étudiant: {data.get('student_id')}")
                return data
            else:
                print(f"❌ Erreur création justification: {response.status_code}")
                print(f"   Détails: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Erreur création justification: {e}")
            return {}
    
    def test_submit_justification(self, justification_id: int) -> bool:
        """Tester la soumission d'une justification"""
        print(f"\n📤 Test de soumission de justification {justification_id}...")
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/justifications/{justification_id}/submit",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Justification soumise avec succès")
                print(f"   📊 Nouveau statut: {data.get('status')}")
                return True
            else:
                print(f"❌ Erreur soumission: {response.status_code}")
                print(f"   Détails: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur soumission justification: {e}")
            return False
    
    def test_get_justification(self, justification_id: int) -> Dict[str, Any]:
        """Tester la récupération d'une justification"""
        print(f"\n🔍 Test de récupération de justification {justification_id}...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/justifications/{justification_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Justification récupérée avec succès")
                print(f"   📋 Titre: {data.get('title')}")
                print(f"   📊 Statut: {data.get('status')}")
                print(f"   📅 Créée le: {data.get('created_at')}")
                return data
            else:
                print(f"❌ Erreur récupération: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erreur récupération justification: {e}")
            return {}
    
    def test_get_student_justifications(self, student_id: str = "student_001") -> bool:
        """Tester la récupération des justifications d'un étudiant"""
        print(f"\n👤 Test de récupération des justifications de l'étudiant {student_id}...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/justifications/student/{student_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Justifications récupérées: {len(data)} trouvées")
                for justification in data[:3]:  # Afficher les 3 premières
                    print(f"   📋 {justification.get('id')}: {justification.get('title')} ({justification.get('status')})")
                return True
            else:
                print(f"❌ Erreur récupération justifications étudiant: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur récupération justifications étudiant: {e}")
            return False
    
    def test_get_pending_validations(self) -> bool:
        """Tester la récupération des validations en attente"""
        print("\n🔍 Test de récupération des validations en attente...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/justifications/pending/validations",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Validations en attente: {len(data)} trouvées")
                for justification in data[:3]:  # Afficher les 3 premières
                    print(f"   📋 {justification.get('id')}: {justification.get('title')} - {justification.get('student_id')}")
                return True
            else:
                print(f"❌ Erreur récupération validations: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur récupération validations: {e}")
            return False
    
    def test_justification_status(self, justification_id: int) -> bool:
        """Tester la récupération du statut d'une justification"""
        print(f"\n📊 Test de récupération du statut de justification {justification_id}...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/justifications/status/{justification_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Statut récupéré avec succès")
                print(f"   📊 Statut: {data.get('status')}")
                print(f"   👨‍👩‍👧‍👦 Approbation parentale requise: {data.get('parent_approval_required')}")
                print(f"   🏛️ Validation admin requise: {data.get('admin_validation_required')}")
                print(f"   ⏰ Expire le: {data.get('expires_at')}")
                return True
            else:
                print(f"❌ Erreur récupération statut: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur récupération statut: {e}")
            return False
    
    def test_service_info(self) -> bool:
        """Tester les informations du service"""
        print("\n📋 Test des informations du service...")
        try:
            response = self.session.get(f"{self.base_url}/info", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Informations récupérées")
                print(f"   🏷️ Service: {data.get('service', {}).get('name')}")
                print(f"   📦 Version: {data.get('service', {}).get('version')}")
                print(f"   🔧 Configuration:")
                config = data.get('configuration', {})
                print(f"      - Délai max justification: {config.get('max_justification_days')} jours")
                print(f"      - Approbation parentale: {config.get('require_parent_approval')}")
                print(f"      - Validation admin: {config.get('require_admin_validation')}")
                print(f"      - Taille max fichier: {config.get('max_file_size_mb')} MB")
                
                external_services = data.get('external_services', {})
                available_services = sum(1 for available in external_services.values() if available)
                print(f"   🔗 Services externes: {available_services}/{len(external_services)} disponibles")
                
                return True
            else:
                print(f"❌ Erreur récupération informations: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur récupération informations: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Exécuter tous les tests"""
        print("🎭 Test du Justification Service PresencePro")
        print("=" * 50)
        print("🧪 Démarrage des tests du service de justifications")
        print("=" * 60)
        
        results = {}
        
        # Test de santé
        results["Service Health"] = self.test_health_check()
        
        # Test d'informations
        results["Service Info"] = self.test_service_info()
        
        # Test de création de justification
        justification = self.test_create_justification()
        results["Create Justification"] = bool(justification)
        
        justification_id = justification.get('id') if justification else None
        
        if justification_id:
            # Test de soumission
            results["Submit Justification"] = self.test_submit_justification(justification_id)
            
            # Test de récupération
            results["Get Justification"] = bool(self.test_get_justification(justification_id))
            
            # Test de statut
            results["Justification Status"] = self.test_justification_status(justification_id)
        else:
            results["Submit Justification"] = False
            results["Get Justification"] = False
            results["Justification Status"] = False
        
        # Test de récupération par étudiant
        results["Student Justifications"] = self.test_get_student_justifications()
        
        # Test des validations en attente
        results["Pending Validations"] = self.test_get_pending_validations()
        
        # Résumé des résultats
        print("\n" + "=" * 60)
        print("📊 Résultats des tests")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100
        print(f"\n📈 Score: {passed}/{total} tests réussis ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 Tous les tests sont passés avec succès!")
        elif success_rate >= 80:
            print("✅ La plupart des tests sont passés")
        else:
            print("⚠️  Plusieurs tests ont échoué - Vérification nécessaire")
        
        failed_tests = [name for name, result in results.items() if not result]
        if failed_tests:
            print(f"\n❌ Tests échoués: {', '.join(failed_tests)}")
        
        return results


def main():
    """Fonction principale"""
    tester = JustificationServiceTester()
    
    # Attendre que le service soit prêt
    print("⏳ Attente du démarrage du service...")
    time.sleep(2)
    
    # Exécuter les tests
    results = tester.run_all_tests()
    
    # Code de sortie basé sur les résultats
    success_rate = sum(results.values()) / len(results)
    return 0 if success_rate >= 0.8 else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
