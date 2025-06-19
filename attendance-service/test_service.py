#!/usr/bin/env python3
"""
Script de test complet pour le service de présences
"""
import os
import sys
import asyncio
import httpx
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any

# Ajouter le répertoire app au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings


class AttendanceServiceTester:
    """Testeur pour le service de présences"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or f"http://localhost:{settings.service_port}"
        self.client = None
        self.test_data = {
            "student_id": "test_student_001",
            "course_id": 1,
            "schedule_id": 1
        }
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def test_service_health(self) -> bool:
        """Tester la santé du service"""
        print("🏥 Test de santé du service...")
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Service en bonne santé")
                print(f"   📊 Base de données: {'✅' if health_data.get('database_connected') else '❌'}")
                print(f"   📈 Total présences: {health_data.get('total_attendances', 0)}")
                print(f"   🔔 Alertes en attente: {health_data.get('pending_alerts', 0)}")
                return True
            else:
                print(f"❌ Service non disponible (status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion service: {e}")
            return False
    
    async def test_mark_attendance(self) -> bool:
        """Tester le marquage de présence"""
        print("\n📝 Test de marquage de présence...")
        
        try:
            # Test présence normale
            attendance_data = {
                "student_id": self.test_data["student_id"],
                "course_id": self.test_data["course_id"],
                "schedule_id": self.test_data["schedule_id"],
                "status": "present",
                "method": "manual",
                "notes": "Test automatique"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/attendance/mark",
                json=attendance_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Présence marquée avec succès (ID: {result.get('id')})")
                
                # Test retard
                late_data = attendance_data.copy()
                late_data["status"] = "late"
                late_data["student_id"] = "test_student_002"
                
                response = await self.client.post(
                    f"{self.base_url}/api/v1/attendance/mark",
                    json=late_data
                )
                
                if response.status_code == 200:
                    print("✅ Retard marqué avec succès")
                    return True
                else:
                    print(f"❌ Erreur marquage retard: {response.status_code}")
                    return False
            else:
                print(f"❌ Erreur marquage présence: {response.status_code}")
                print(f"   Détails: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test marquage: {e}")
            return False
    
    async def test_bulk_attendance(self) -> bool:
        """Tester le marquage en lot"""
        print("\n📋 Test de marquage en lot...")
        
        try:
            bulk_data = {
                "course_id": self.test_data["course_id"],
                "schedule_id": self.test_data["schedule_id"],
                "attendances": [
                    {
                        "student_id": "bulk_student_001",
                        "status": "present",
                        "method": "manual"
                    },
                    {
                        "student_id": "bulk_student_002",
                        "status": "absent",
                        "method": "manual"
                    },
                    {
                        "student_id": "bulk_student_003",
                        "status": "late",
                        "method": "manual"
                    }
                ]
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/attendance/bulk-mark",
                json=bulk_data
            )
            
            if response.status_code == 200:
                result = response.json()
                success_count = result.get("success_count", 0)
                error_count = result.get("error_count", 0)
                
                print(f"✅ Marquage en lot terminé")
                print(f"   📊 Succès: {success_count}")
                print(f"   ❌ Erreurs: {error_count}")
                
                return success_count > 0
            else:
                print(f"❌ Erreur marquage en lot: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test marquage en lot: {e}")
            return False
    
    async def test_get_student_attendance(self) -> bool:
        """Tester la récupération des présences d'un étudiant"""
        print("\n👤 Test récupération présences étudiant...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/attendance/student/{self.test_data['student_id']}"
            )
            
            if response.status_code == 200:
                attendances = response.json()
                print(f"✅ Présences récupérées: {len(attendances)} enregistrements")
                
                if attendances:
                    latest = attendances[0]
                    print(f"   📅 Dernière présence: {latest.get('marked_at')}")
                    print(f"   📊 Statut: {latest.get('status')}")
                
                return True
            else:
                print(f"❌ Erreur récupération présences: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test récupération: {e}")
            return False
    
    async def test_get_course_attendance(self) -> bool:
        """Tester la récupération des présences d'un cours"""
        print("\n📚 Test récupération présences cours...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/attendance/course/{self.test_data['course_id']}"
            )
            
            if response.status_code == 200:
                attendances = response.json()
                print(f"✅ Présences cours récupérées: {len(attendances)} enregistrements")
                
                # Statistiques par statut
                stats = {}
                for att in attendances:
                    status = att.get('status')
                    stats[status] = stats.get(status, 0) + 1
                
                for status, count in stats.items():
                    print(f"   📊 {status}: {count}")
                
                return True
            else:
                print(f"❌ Erreur récupération présences cours: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test récupération cours: {e}")
            return False
    
    async def test_attendance_stats(self) -> bool:
        """Tester les statistiques de présence"""
        print("\n📊 Test statistiques de présence...")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/attendance/stats")
            
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Statistiques récupérées")
                print(f"   📈 Total sessions: {stats.get('total_sessions', 0)}")
                print(f"   👥 Total présences: {stats.get('total_attendances', 0)}")
                print(f"   ✅ Présents: {stats.get('present_count', 0)}")
                print(f"   ❌ Absents: {stats.get('absent_count', 0)}")
                print(f"   ⏰ En retard: {stats.get('late_count', 0)}")
                print(f"   📊 Taux présence: {stats.get('attendance_rate', 0):.1%}")
                
                return True
            else:
                print(f"❌ Erreur récupération statistiques: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test statistiques: {e}")
            return False
    
    async def test_student_report(self) -> bool:
        """Tester la génération de rapport étudiant"""
        print("\n📋 Test rapport étudiant...")
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            response = await self.client.get(
                f"{self.base_url}/api/v1/reports/student/{self.test_data['student_id']}",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            
            if response.status_code == 200:
                report = response.json()
                print(f"✅ Rapport étudiant généré")
                print(f"   👤 Étudiant: {report.get('student_id')}")
                print(f"   📅 Période: {report.get('period_start')} → {report.get('period_end')}")
                print(f"   📊 Sessions totales: {report.get('total_sessions', 0)}")
                print(f"   ✅ Sessions présentes: {report.get('attended_sessions', 0)}")
                print(f"   📈 Taux présence: {report.get('attendance_rate', 0):.1%}")
                
                return True
            else:
                print(f"❌ Erreur génération rapport: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test rapport: {e}")
            return False
    
    async def test_face_recognition_integration(self) -> bool:
        """Tester l'intégration avec la reconnaissance faciale"""
        print("\n🎭 Test intégration reconnaissance faciale...")
        
        try:
            recognition_data = {
                "student_id": "face_test_student",
                "course_id": self.test_data["course_id"],
                "confidence": 0.95,
                "timestamp": datetime.now().isoformat(),
                "method": "face_recognition"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/attendance/face-recognition",
                json=recognition_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Intégration reconnaissance faciale OK")
                print(f"   🎯 Confiance: {recognition_data['confidence']:.1%}")
                print(f"   📝 Message: {result.get('message')}")
                
                return True
            else:
                print(f"❌ Erreur intégration reconnaissance: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test reconnaissance faciale: {e}")
            return False
    
    async def test_alerts(self) -> bool:
        """Tester le système d'alertes"""
        print("\n🔔 Test système d'alertes...")
        
        try:
            # Vérifier les alertes en attente
            response = await self.client.get(f"{self.base_url}/api/v1/alerts/pending/count")
            
            if response.status_code == 200:
                result = response.json()
                pending_count = result.get("pending_alerts", 0)
                print(f"✅ Alertes en attente: {pending_count}")
                
                # Test de vérification de patterns
                response = await self.client.post(
                    f"{self.base_url}/api/v1/alerts/check-patterns/{self.test_data['student_id']}"
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Vérification patterns terminée")
                    print(f"   🔔 Nouvelles alertes: {len(result.get('alerts', []))}")
                    
                    return True
                else:
                    print(f"❌ Erreur vérification patterns: {response.status_code}")
                    return False
            else:
                print(f"❌ Erreur récupération alertes: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test alertes: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Exécuter tous les tests"""
        print("🧪 Démarrage des tests du service de présences")
        print("=" * 60)
        
        tests = [
            ("Service Health", self.test_service_health),
            ("Mark Attendance", self.test_mark_attendance),
            ("Bulk Attendance", self.test_bulk_attendance),
            ("Student Attendance", self.test_get_student_attendance),
            ("Course Attendance", self.test_get_course_attendance),
            ("Attendance Stats", self.test_attendance_stats),
            ("Student Report", self.test_student_report),
            ("Face Recognition", self.test_face_recognition_integration),
            ("Alerts System", self.test_alerts)
        ]
        
        results = {}
        passed = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ Erreur test {test_name}: {e}")
                results[test_name] = False
        
        print("\n" + "=" * 60)
        print("📊 Résultats des tests")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Score: {passed}/{len(tests)} tests réussis ({passed/len(tests)*100:.1f}%)")
        
        if passed == len(tests):
            print("🎉 Tous les tests sont passés avec succès!")
        elif passed >= len(tests) * 0.8:
            print("✅ La plupart des tests sont passés")
        else:
            print("⚠️  Plusieurs tests ont échoué - Vérification nécessaire")
        
        return results


async def main():
    """Fonction principale"""
    print("🎭 Test du Attendance Service PresencePro")
    print("=" * 50)
    
    async with AttendanceServiceTester() as tester:
        results = await tester.run_all_tests()
        
        # Retourner un code d'erreur si des tests échouent
        failed_tests = [name for name, result in results.items() if not result]
        if failed_tests:
            print(f"\n❌ Tests échoués: {', '.join(failed_tests)}")
            sys.exit(1)
        else:
            print("\n🎊 Tous les tests sont passés!")
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
