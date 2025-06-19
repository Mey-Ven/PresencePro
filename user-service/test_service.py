"""
Script de test simple pour valider le service utilisateur
"""
import asyncio
import httpx
import json


async def test_user_service():
    """Test simple du service utilisateur"""
    base_url = "http://localhost:8002"
    
    print("🧪 Test du service utilisateur PresencePro")
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
                "/students/",
                "/teachers/", 
                "/parents/"
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
            print("   4. Testez les endpoints via http://localhost:8002/docs")
            
        except httpx.ConnectError:
            print("❌ Impossible de se connecter au service")
            print("   Assurez-vous que le service est démarré sur le port 8002")
            print("   Commande: uvicorn app.main:app --reload --port 8002")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")


def test_data_models():
    """Test des modèles de données"""
    print("\n📊 Test des modèles de données")
    print("-" * 30)
    
    # Exemple de données d'étudiant
    student_data = {
        "user_id": "student123",
        "student_number": "STU001",
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice@example.com",
        "phone": "0123456789",
        "class_name": "6ème A",
        "academic_year": "2023-2024",
        "is_active": True
    }
    
    # Exemple de données d'enseignant
    teacher_data = {
        "user_id": "teacher123",
        "employee_number": "EMP001",
        "first_name": "Marie",
        "last_name": "Dupont",
        "email": "marie@example.com",
        "phone": "0123456789",
        "department": "Mathématiques",
        "subject": "Algèbre",
        "is_active": True
    }
    
    # Exemple de données de parent
    parent_data = {
        "user_id": "parent123",
        "first_name": "Robert",
        "last_name": "Johnson",
        "email": "robert@example.com",
        "phone": "0123456789",
        "profession": "Ingénieur",
        "emergency_contact": True,
        "is_active": True
    }
    
    print("✅ Modèle Étudiant:")
    print(f"   {json.dumps(student_data, indent=2, ensure_ascii=False)}")
    
    print("\n✅ Modèle Enseignant:")
    print(f"   {json.dumps(teacher_data, indent=2, ensure_ascii=False)}")
    
    print("\n✅ Modèle Parent:")
    print(f"   {json.dumps(parent_data, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    print("🚀 Script de test du service utilisateur PresencePro")
    print("=" * 60)
    
    # Test des modèles de données
    test_data_models()
    
    # Test du service (asynchrone)
    asyncio.run(test_user_service())
