#!/usr/bin/env python3
"""
Script de test automatisé pour le messaging-service
"""
import asyncio
import json
import time
import httpx
import websockets
from datetime import datetime
import sys


class MessagingServiceTester:
    """Testeur pour le service de messagerie"""
    
    def __init__(self, base_url="http://localhost:8007", ws_url="ws://localhost:8007"):
        self.base_url = base_url
        self.ws_url = ws_url
        self.test_results = []
        
        # Token de test (à remplacer par un vrai token)
        self.test_token = "test-jwt-token-replace-with-real-token"
        
        # Données de test
        self.test_user_id = "test_user_001"
        self.test_recipient_id = "test_user_002"
    
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
                        ws_status = data.get("checks", {}).get("websocket", {}).get("status")
                        
                        details = f"DB: {db_status}, WebSocket: {ws_status}"
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
                    
                    if service_name == "messaging-service":
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
    
    async def test_websocket_connection(self):
        """Tester la connexion WebSocket"""
        try:
            uri = f"{self.ws_url}/ws"
            
            async with websockets.connect(uri, timeout=10) as websocket:
                # Envoyer un ping
                ping_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(ping_message))
                
                # Attendre la réponse
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("type") == "pong":
                    self.log_test("WebSocket Connection", True, "Ping/Pong réussi")
                    return True
                else:
                    self.log_test("WebSocket Connection", False, f"Réponse inattendue: {response_data}")
                    return False
                    
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Erreur: {e}")
            return False
    
    async def test_websocket_authentication(self):
        """Tester l'authentification WebSocket"""
        try:
            uri = f"{self.ws_url}/ws"
            
            async with websockets.connect(uri, timeout=10) as websocket:
                # Envoyer un message d'authentification
                auth_message = {
                    "type": "authentication",
                    "token": self.test_token
                }
                
                await websocket.send(json.dumps(auth_message))
                
                # Attendre la réponse
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                # Comme nous n'avons pas de vrai token, on s'attend à une erreur
                if response_data.get("type") == "error":
                    error_code = response_data.get("error_code")
                    if error_code == "AUTH_FAILED":
                        self.log_test("WebSocket Authentication", True, "Rejet attendu du faux token")
                        return True
                    else:
                        self.log_test("WebSocket Authentication", False, f"Erreur inattendue: {error_code}")
                        return False
                else:
                    self.log_test("WebSocket Authentication", False, f"Réponse inattendue: {response_data}")
                    return False
                    
        except Exception as e:
            self.log_test("WebSocket Authentication", False, f"Erreur: {e}")
            return False
    
    async def test_rest_api_without_auth(self):
        """Tester l'API REST sans authentification"""
        try:
            async with httpx.AsyncClient() as client:
                # Tenter d'envoyer un message sans authentification
                response = await client.post(
                    f"{self.base_url}/api/v1/messages/send",
                    json={
                        "content": "Test message",
                        "recipient_id": self.test_recipient_id
                    },
                    timeout=10.0
                )
                
                # On s'attend à une erreur 401
                if response.status_code == 401:
                    self.log_test("REST API Without Auth", True, "Rejet attendu sans authentification")
                    return True
                else:
                    self.log_test("REST API Without Auth", False, f"HTTP {response.status_code} inattendu")
                    return False
                    
        except Exception as e:
            self.log_test("REST API Without Auth", False, f"Erreur: {e}")
            return False
    
    async def test_conversations_endpoint(self):
        """Tester l'endpoint des conversations"""
        try:
            async with httpx.AsyncClient() as client:
                # Tenter de récupérer les conversations sans authentification
                response = await client.get(
                    f"{self.base_url}/api/v1/messages/conversations",
                    timeout=10.0
                )
                
                # On s'attend à une erreur 401
                if response.status_code == 401:
                    self.log_test("Conversations Endpoint", True, "Authentification requise")
                    return True
                else:
                    self.log_test("Conversations Endpoint", False, f"HTTP {response.status_code} inattendu")
                    return False
                    
        except Exception as e:
            self.log_test("Conversations Endpoint", False, f"Erreur: {e}")
            return False
    
    async def test_websocket_message_format(self):
        """Tester le format des messages WebSocket"""
        try:
            uri = f"{self.ws_url}/ws"
            
            async with websockets.connect(uri, timeout=10) as websocket:
                # Envoyer un message avec un format invalide
                invalid_message = "invalid json"
                
                await websocket.send(invalid_message)
                
                # Attendre la réponse d'erreur
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("type") == "error" and response_data.get("error_code") == "INVALID_JSON":
                    self.log_test("WebSocket Message Format", True, "Validation JSON correcte")
                    return True
                else:
                    self.log_test("WebSocket Message Format", False, f"Réponse inattendue: {response_data}")
                    return False
                    
        except Exception as e:
            self.log_test("WebSocket Message Format", False, f"Erreur: {e}")
            return False
    
    async def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🧪 Test du Messaging Service PresencePro")
        print("=" * 50)
        print("🔍 Démarrage des tests du service de messagerie")
        print("=" * 60)
        
        # Attendre que le service soit prêt
        print("⏳ Attente du démarrage du service...")
        await asyncio.sleep(2)
        
        # Tests de base
        await self.test_service_health()
        await self.test_service_info()
        
        # Tests WebSocket
        await self.test_websocket_connection()
        await self.test_websocket_authentication()
        await self.test_websocket_message_format()
        
        # Tests API REST
        await self.test_rest_api_without_auth()
        await self.test_conversations_endpoint()
        
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
    tester = MessagingServiceTester()
    
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
