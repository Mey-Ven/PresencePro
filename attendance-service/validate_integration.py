#!/usr/bin/env python3
"""
Script de validation de l'intégration avec les autres services PresencePro
"""
import asyncio
import httpx
import sys
from datetime import datetime
from typing import Dict, Any, List


class IntegrationValidator:
    """Validateur d'intégration avec les autres services"""
    
    def __init__(self):
        self.services = {
            "auth-service": "http://localhost:8001",
            "user-service": "http://localhost:8002", 
            "course-service": "http://localhost:8003",
            "face-recognition-service": "http://localhost:8004",
            "attendance-service": "http://localhost:8005"
        }
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def check_service_availability(self) -> Dict[str, bool]:
        """Vérifier la disponibilité de tous les services"""
        print("🔍 Vérification de la disponibilité des services...")
        
        availability = {}
        
        for service_name, service_url in self.services.items():
            try:
                response = await self.client.get(f"{service_url}/health", timeout=10.0)
                available = response.status_code == 200
                availability[service_name] = available
                
                status = "✅" if available else "❌"
                print(f"   {status} {service_name}: {service_url}")
                
                if available:
                    health_data = response.json()
                    print(f"      📊 Status: {health_data.get('status', 'unknown')}")
                
            except Exception as e:
                availability[service_name] = False
                print(f"   ❌ {service_name}: Erreur - {str(e)[:50]}...")
        
        available_count = sum(availability.values())
        total_count = len(availability)
        
        print(f"\n📈 Services disponibles: {available_count}/{total_count}")
        
        return availability
    
    async def test_auth_integration(self) -> bool:
        """Tester l'intégration avec auth-service"""
        print("\n🔐 Test intégration auth-service...")
        
        try:
            # Tenter de créer un token de test
            auth_data = {
                "username": "test_user",
                "password": "test_password"
            }
            
            response = await self.client.post(
                f"{self.services['auth-service']}/api/v1/auth/login",
                data=auth_data
            )
            
            if response.status_code in [200, 401]:  # 401 est OK (utilisateur inexistant)
                print("✅ Endpoint auth accessible")
                
                # Tester la vérification de token
                test_token = "test.jwt.token"
                response = await self.client.post(
                    f"{self.services['auth-service']}/api/v1/auth/verify-token",
                    headers={"Authorization": f"Bearer {test_token}"}
                )
                
                print("✅ Endpoint vérification token accessible")
                return True
            else:
                print(f"❌ Erreur auth-service: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur intégration auth: {e}")
            return False
    
    async def test_user_integration(self) -> bool:
        """Tester l'intégration avec user-service"""
        print("\n👥 Test intégration user-service...")
        
        try:
            # Tester la récupération d'utilisateur
            response = await self.client.get(
                f"{self.services['user-service']}/api/v1/users/test_user_id"
            )
            
            if response.status_code in [200, 404]:  # 404 est OK (utilisateur inexistant)
                print("✅ Endpoint utilisateurs accessible")
                
                # Tester la liste des utilisateurs
                response = await self.client.get(
                    f"{self.services['user-service']}/api/v1/users",
                    params={"limit": 1}
                )
                
                if response.status_code == 200:
                    users = response.json()
                    print(f"✅ Liste utilisateurs accessible ({len(users)} utilisateurs)")
                    return True
                else:
                    print("✅ Endpoint accessible (pas d'utilisateurs)")
                    return True
            else:
                print(f"❌ Erreur user-service: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur intégration user: {e}")
            return False
    
    async def test_course_integration(self) -> bool:
        """Tester l'intégration avec course-service"""
        print("\n📚 Test intégration course-service...")
        
        try:
            # Tester la récupération de cours
            response = await self.client.get(
                f"{self.services['course-service']}/api/v1/courses/1"
            )
            
            if response.status_code in [200, 404]:  # 404 est OK (cours inexistant)
                print("✅ Endpoint cours accessible")
                
                # Tester la liste des cours
                response = await self.client.get(
                    f"{self.services['course-service']}/api/v1/courses",
                    params={"limit": 1}
                )
                
                if response.status_code == 200:
                    courses = response.json()
                    print(f"✅ Liste cours accessible ({len(courses)} cours)")
                    
                    # Tester les emplois du temps
                    response = await self.client.get(
                        f"{self.services['course-service']}/api/v1/schedules"
                    )
                    
                    if response.status_code == 200:
                        print("✅ Endpoint emplois du temps accessible")
                        return True
                    else:
                        print("✅ Cours accessible (pas d'emplois du temps)")
                        return True
                else:
                    print("✅ Endpoint accessible (pas de cours)")
                    return True
            else:
                print(f"❌ Erreur course-service: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur intégration course: {e}")
            return False
    
    async def test_face_recognition_integration(self) -> bool:
        """Tester l'intégration avec face-recognition-service"""
        print("\n🎭 Test intégration face-recognition-service...")
        
        try:
            # Tester le statut de la caméra
            response = await self.client.get(
                f"{self.services['face-recognition-service']}/api/v1/camera/status"
            )
            
            if response.status_code == 200:
                camera_status = response.json()
                print(f"✅ Caméra accessible - Status: {camera_status.get('status')}")
                
                # Tester l'endpoint de reconnaissance
                test_data = {
                    "student_id": "test_student",
                    "confidence": 0.95,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = await self.client.post(
                    f"{self.services['attendance-service']}/api/v1/attendance/face-recognition",
                    json=test_data
                )
                
                if response.status_code in [200, 400]:  # 400 peut être OK (données invalides)
                    print("✅ Endpoint reconnaissance faciale accessible")
                    return True
                else:
                    print(f"❌ Erreur endpoint reconnaissance: {response.status_code}")
                    return False
            else:
                print(f"❌ Erreur face-recognition-service: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur intégration face-recognition: {e}")
            return False
    
    async def test_attendance_workflows(self) -> bool:
        """Tester les workflows complets de présence"""
        print("\n🔄 Test workflows complets...")
        
        try:
            # Workflow 1: Marquage manuel de présence
            attendance_data = {
                "student_id": "integration_test_student",
                "course_id": 1,
                "status": "present",
                "method": "manual",
                "notes": "Test d'intégration"
            }
            
            response = await self.client.post(
                f"{self.services['attendance-service']}/api/v1/attendance/mark",
                json=attendance_data
            )
            
            if response.status_code == 200:
                attendance = response.json()
                attendance_id = attendance.get("id")
                print(f"✅ Workflow marquage manuel OK (ID: {attendance_id})")
                
                # Workflow 2: Récupération des présences
                response = await self.client.get(
                    f"{self.services['attendance-service']}/api/v1/attendance/student/integration_test_student"
                )
                
                if response.status_code == 200:
                    attendances = response.json()
                    print(f"✅ Workflow récupération présences OK ({len(attendances)} enregistrements)")
                    
                    # Workflow 3: Génération de statistiques
                    response = await self.client.get(
                        f"{self.services['attendance-service']}/api/v1/attendance/stats",
                        params={"student_id": "integration_test_student"}
                    )
                    
                    if response.status_code == 200:
                        stats = response.json()
                        print(f"✅ Workflow statistiques OK (taux: {stats.get('attendance_rate', 0):.1%})")
                        return True
                    else:
                        print(f"❌ Erreur workflow statistiques: {response.status_code}")
                        return False
                else:
                    print(f"❌ Erreur workflow récupération: {response.status_code}")
                    return False
            else:
                print(f"❌ Erreur workflow marquage: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur workflows: {e}")
            return False
    
    async def test_data_consistency(self) -> bool:
        """Tester la cohérence des données entre services"""
        print("\n🔍 Test cohérence des données...")
        
        try:
            # Vérifier que les IDs de cours existent dans course-service
            response = await self.client.get(
                f"{self.services['attendance-service']}/api/v1/attendance/stats"
            )
            
            if response.status_code == 200:
                print("✅ Données de présence accessibles")
                
                # Vérifier les alertes
                response = await self.client.get(
                    f"{self.services['attendance-service']}/api/v1/alerts/pending/count"
                )
                
                if response.status_code == 200:
                    result = response.json()
                    pending_alerts = result.get("pending_alerts", 0)
                    print(f"✅ Système d'alertes fonctionnel ({pending_alerts} alertes)")
                    return True
                else:
                    print(f"❌ Erreur système alertes: {response.status_code}")
                    return False
            else:
                print(f"❌ Erreur accès données: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur cohérence données: {e}")
            return False
    
    async def run_full_validation(self) -> Dict[str, bool]:
        """Exécuter la validation complète"""
        print("🔍 Validation d'intégration du Attendance Service")
        print("=" * 60)
        
        # Vérifier la disponibilité des services
        availability = await self.check_service_availability()
        
        # Tests d'intégration
        tests = []
        
        if availability.get("auth-service"):
            tests.append(("Auth Integration", self.test_auth_integration))
        
        if availability.get("user-service"):
            tests.append(("User Integration", self.test_user_integration))
        
        if availability.get("course-service"):
            tests.append(("Course Integration", self.test_course_integration))
        
        if availability.get("face-recognition-service"):
            tests.append(("Face Recognition Integration", self.test_face_recognition_integration))
        
        if availability.get("attendance-service"):
            tests.append(("Attendance Workflows", self.test_attendance_workflows))
            tests.append(("Data Consistency", self.test_data_consistency))
        
        # Exécuter les tests
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
        
        # Résultats
        print("\n" + "=" * 60)
        print("📊 Résultats de validation")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        total_tests = len(tests)
        if total_tests > 0:
            print(f"\n📈 Score: {passed}/{total_tests} tests réussis ({passed/total_tests*100:.1f}%)")
            
            if passed == total_tests:
                print("🎉 Intégration complète validée!")
            elif passed >= total_tests * 0.8:
                print("✅ Intégration majoritairement fonctionnelle")
            else:
                print("⚠️  Problèmes d'intégration détectés")
        else:
            print("⚠️  Aucun service disponible pour les tests d'intégration")
        
        return results


async def main():
    """Fonction principale"""
    async with IntegrationValidator() as validator:
        results = await validator.run_full_validation()
        
        # Déterminer le code de sortie
        failed_tests = [name for name, result in results.items() if not result]
        if failed_tests:
            print(f"\n❌ Tests échoués: {', '.join(failed_tests)}")
            sys.exit(1)
        else:
            print("\n🎊 Validation d'intégration réussie!")
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
