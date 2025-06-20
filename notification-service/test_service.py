#!/usr/bin/env python3
"""
Script de test automatisé pour le notification-service
"""
import asyncio
import json
import time
import httpx
from datetime import datetime
import sys
import os

# Ajouter le répertoire app au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))


class NotificationServiceTester:
    """Testeur pour le service de notifications"""
    
    def __init__(self, base_url="http://localhost:8008"):
        self.base_url = base_url
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Logger un résultat de test"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now()
        })
    
    async def test_service_health(self):
        """Tester la santé du service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    
                    if status == "healthy":
                        db_status = data.get("checks", {}).get("database", {}).get("status")
                        redis_status = data.get("checks", {}).get("redis", {}).get("status")
                        celery_status = data.get("checks", {}).get("celery", {}).get("status")
                        
                        details = f"DB: {db_status}, Redis: {redis_status}, Celery: {celery_status}"
                        self.log_test("Service Health", True, details)
                        return True
                    else:
                        self.log_test("Service Health", False, f"Status: {status}")
                        return False
                else:
                    self.log_test("Service Health", False, f"HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test("Service Health", False, f"Erreur: {e}")
            return False
    
    async def test_service_info(self):
        """Tester les informations du service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/info", timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    service_name = data.get("service", {}).get("name")
                    version = data.get("service", {}).get("version")
                    
                    if service_name == "notification-service":
                        details = f"Version: {version}"
                        self.log_test("Service Info", True, details)
                        return True
                    else:
                        self.log_test("Service Info", False, f"Service incorrect: {service_name}")
                        return False
                else:
                    self.log_test("Service Info", False, f"HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test("Service Info", False, f"Erreur: {e}")
            return False
    
    async def test_database_connection(self):
        """Tester la connexion à la base de données"""
        try:
            from app.core.database import check_database_connection, get_database_stats
            
            # Test de connexion
            db_connected = check_database_connection()
            
            if db_connected:
                # Récupérer les statistiques
                stats = get_database_stats()
                details = f"Templates: {stats.get('total_templates', 0)}, Préférences: {stats.get('total_user_preferences', 0)}"
                self.log_test("Database Connection", True, details)
                return True
            else:
                self.log_test("Database Connection", False, "Connexion échouée")
                return False
                
        except Exception as e:
            self.log_test("Database Connection", False, f"Erreur: {e}")
            return False
    
    async def test_redis_connection(self):
        """Tester la connexion Redis"""
        try:
            from app.services.event_listener import event_listener
            
            await event_listener.connect()
            
            # Test de ping
            queue_info = await event_listener.get_queue_info()
            
            if queue_info:
                details = f"Version Redis: {queue_info.get('redis_version', 'N/A')}"
                self.log_test("Redis Connection", True, details)
                return True
            else:
                self.log_test("Redis Connection", False, "Pas d'informations Redis")
                return False
                
        except Exception as e:
            self.log_test("Redis Connection", False, f"Erreur: {e}")
            return False
    
    async def test_email_service(self):
        """Tester le service d'email"""
        try:
            from app.services.email_service import email_service
            
            # Test d'envoi d'email (mode mock)
            result = await email_service.send_email(
                to_email="test@example.com",
                subject="Test Notification Service",
                content="Test email du service de notifications",
                html_content="<h1>Test</h1><p>Test email du service de notifications</p>"
            )
            
            if result.get("success"):
                provider = result.get("provider", "unknown")
                details = f"Provider: {provider}"
                self.log_test("Email Service", True, details)
                return True
            else:
                error = result.get("error", "Erreur inconnue")
                self.log_test("Email Service", False, f"Erreur: {error}")
                return False
                
        except Exception as e:
            self.log_test("Email Service", False, f"Erreur: {e}")
            return False
    
    async def test_template_service(self):
        """Tester le service de templates"""
        try:
            from app.services.template_service import template_service
            
            # Récupérer un template par défaut
            template = await template_service.get_default_template(
                notification_type="absence_detected",
                channel="email",
                language="fr"
            )
            
            if template:
                details = f"Template: {template.name}"
                self.log_test("Template Service", True, details)
                return True
            else:
                self.log_test("Template Service", False, "Aucun template trouvé")
                return False
                
        except Exception as e:
            self.log_test("Template Service", False, f"Erreur: {e}")
            return False
    
    async def test_event_publishing(self):
        """Tester la publication d'événements"""
        try:
            from app.services.event_listener import event_listener
            
            # Publier un événement de test
            test_event = {
                "event_type": "absence_detected",
                "source_service": "test",
                "data": {
                    "student_id": "test_student",
                    "student_name": "Test Student",
                    "parent_name": "Test Parent",
                    "absence_date": "2025-06-20",
                    "absence_time": "09:00",
                    "course_name": "Test Course",
                    "teacher_name": "Test Teacher",
                    "parent_emails": ["parent@test.com"]
                }
            }
            
            await event_listener.publish_event(test_event)
            
            self.log_test("Event Publishing", True, "Événement publié")
            return True
                
        except Exception as e:
            self.log_test("Event Publishing", False, f"Erreur: {e}")
            return False
    
    async def test_celery_tasks(self):
        """Tester les tâches Celery"""
        try:
            from app.tasks.email_tasks import send_email_task
            
            # Lancer une tâche de test
            task = send_email_task.delay(
                notification_id="test_notification",
                to_email="test@example.com",
                subject="Test Celery",
                content="Test de tâche Celery",
                user_id="test_user",
                notification_type="test",
                priority="normal"
            )
            
            # Attendre un peu pour voir si la tâche est acceptée
            await asyncio.sleep(1)
            
            if task.id:
                details = f"Task ID: {task.id}"
                self.log_test("Celery Tasks", True, details)
                return True
            else:
                self.log_test("Celery Tasks", False, "Pas de task ID")
                return False
                
        except Exception as e:
            self.log_test("Celery Tasks", False, f"Erreur: {e}")
            return False
    
    async def test_api_endpoint(self):
        """Tester l'endpoint de test d'événement"""
        try:
            test_event = {
                "event_type": "message_received",
                "source_service": "test",
                "data": {
                    "message_id": "test_message",
                    "sender_name": "Test Sender",
                    "recipient_name": "Test Recipient",
                    "content": "Test message content",
                    "recipient_email": "recipient@test.com"
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/test/event",
                    json=test_event,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test("API Endpoint", True, "Événement de test envoyé")
                        return True
                    else:
                        self.log_test("API Endpoint", False, data.get("error", "Erreur inconnue"))
                        return False
                else:
                    self.log_test("API Endpoint", False, f"HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test("API Endpoint", False, f"Erreur: {e}")
            return False
    
    async def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🧪 Test du Notification Service PresencePro")
        print("=" * 60)
        print("🔍 Démarrage des tests du service de notifications")
        print("=" * 60)
        
        # Attendre que le service soit prêt
        print("⏳ Attente du démarrage du service...")
        await asyncio.sleep(2)
        
        # Tests de base
        await self.test_service_health()
        await self.test_service_info()
        
        # Tests de connexions
        await self.test_database_connection()
        await self.test_redis_connection()
        
        # Tests des services
        await self.test_email_service()
        await self.test_template_service()
        
        # Tests d'événements
        await self.test_event_publishing()
        await self.test_celery_tasks()
        
        # Tests API
        await self.test_api_endpoint()
        
        # Résumé des résultats
        print("\n" + "=" * 60)
        print("📊 Résultats des tests")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}")
        
        print(f"\n📈 Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 Tous les tests sont passés !")
            return True
        else:
            failed_tests = [r["test"] for r in self.test_results if not r["success"]]
            print(f"⚠️  Tests échoués: {', '.join(failed_tests)}")
            return False


async def main():
    """Fonction principale"""
    tester = NotificationServiceTester()
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur lors des tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
