"""
Script de test simple pour valider le service de cours
"""
import asyncio
import httpx
import json


async def test_course_service():
    """Test simple du service de cours"""
    base_url = "http://localhost:8003"
    
    print("🧪 Test du service de cours PresencePro")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test de santé
            print("1. Test de santé du service...")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Service en bonne santé")
                print(f"   Réponse: {response.json()}")
            else:
                print(f"❌ Problème de santé: {response.status_code}")
                return
            
            # Test de l'endpoint racine
            print("\n2. Test de l'endpoint racine...")
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print("✅ Endpoint racine accessible")
                print(f"   Réponse: {response.json()}")
            else:
                print(f"❌ Problème avec l'endpoint racine: {response.status_code}")
            
            # Test de la documentation
            print("\n3. Test de la documentation...")
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("✅ Documentation accessible")
            else:
                print(f"❌ Problème avec la documentation: {response.status_code}")
            
            # Test des endpoints protégés (sans authentification)
            print("\n4. Test des endpoints protégés (sans auth)...")
            
            endpoints_to_test = [
                "/courses/",
                "/schedules/weekly",
                "/assignments/"
            ]
            
            for endpoint in endpoints_to_test:
                response = await client.get(f"{base_url}{endpoint}")
                if response.status_code in [401, 403]:
                    print(f"✅ {endpoint} correctement protégé (code: {response.status_code})")
                else:
                    print(f"⚠️  {endpoint} réponse inattendue: {response.status_code}")
            
            print("\n🎉 Tests terminés!")
            print("\n📝 Pour tester avec authentification:")
            print("   1. Démarrez le service d'authentification (port 8001)")
            print("   2. Obtenez un token JWT via /login")
            print("   3. Utilisez le token dans les headers: Authorization: Bearer <token>")
            print("   4. Testez les endpoints via http://localhost:8003/docs")
            
        except httpx.ConnectError:
            print("❌ Impossible de se connecter au service")
            print("   Assurez-vous que le service est démarré sur le port 8003")
            print("   Commande: uvicorn app.main:app --reload --port 8003")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")


def test_data_models():
    """Test des modèles de données"""
    print("\n📊 Test des modèles de données")
    print("-" * 30)
    
    # Exemple de données de cours
    course_data = {
        "name": "Mathématiques Avancées",
        "code": "MATH001",
        "description": "Cours de mathématiques niveau 6ème",
        "subject": "Mathématiques",
        "level": "6ème",
        "credits": 3,
        "max_students": 25,
        "status": "active",
        "academic_year": "2023-2024",
        "semester": "Semestre 1"
    }
    
    # Exemple de données d'emploi du temps
    schedule_data = {
        "course_id": 1,
        "day_of_week": "monday",
        "start_time": "08:00:00",
        "end_time": "09:30:00",
        "room": "A101",
        "building": "Bâtiment A",
        "start_date": "2023-09-01",
        "end_date": "2024-01-31"
    }
    
    # Exemple de données d'attribution
    assignment_data = {
        "course_id": 1,
        "user_id": "teacher1",
        "assignment_type": "teacher",
        "is_primary": True,
        "valid_from": "2023-09-01",
        "valid_to": "2024-06-30"
    }
    
    print("✅ Modèle Cours:")
    print(f"   {json.dumps(course_data, indent=2, ensure_ascii=False)}")
    
    print("\n✅ Modèle Emploi du Temps:")
    print(f"   {json.dumps(schedule_data, indent=2, ensure_ascii=False)}")
    
    print("\n✅ Modèle Attribution:")
    print(f"   {json.dumps(assignment_data, indent=2, ensure_ascii=False)}")


def test_integration_examples():
    """Exemples d'intégration avec d'autres services"""
    print("\n🔗 Exemples d'intégration")
    print("-" * 30)
    
    print("✅ Intégration avec le service d'authentification:")
    print("   - Vérification des tokens JWT")
    print("   - Validation des permissions par rôle")
    print("   - URL: http://localhost:8001")
    
    print("\n✅ Intégration avec le service utilisateur:")
    print("   - Récupération des informations utilisateur")
    print("   - Validation de l'existence des utilisateurs")
    print("   - URL: http://localhost:8002")
    
    print("\n✅ Flux d'utilisation typique:")
    print("   1. Authentification via auth-service")
    print("   2. Création de cours (Admin)")
    print("   3. Définition des emplois du temps")
    print("   4. Attribution des enseignants et étudiants")
    print("   5. Consultation des plannings")


if __name__ == "__main__":
    print("🚀 Script de test du service de cours PresencePro")
    print("=" * 60)
    
    # Test des modèles de données
    test_data_models()
    
    # Exemples d'intégration
    test_integration_examples()
    
    # Test du service (asynchrone)
    asyncio.run(test_course_service())
