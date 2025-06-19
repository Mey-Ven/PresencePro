#!/usr/bin/env python3
"""
Script de test rapide pour vérifier que le service d'authentification fonctionne.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def test_health():
    """Test du endpoint de santé."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_auth_flow():
    """Test du flux d'authentification complet."""
    print("\n🔐 Test du flux d'authentification...")
    
    # Test login avec des identifiants invalides
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "invalid", "password": "invalid"}
        )
        print(f"✅ Login invalide: {response.status_code} (attendu: 401)")
    except Exception as e:
        print(f"❌ Test login invalide failed: {e}")
    
    # Test accès non autorisé
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/roles/me")
        print(f"✅ Accès non autorisé: {response.status_code} (attendu: 403)")
    except Exception as e:
        print(f"❌ Test accès non autorisé failed: {e}")

def main():
    """Fonction principale."""
    print("🚀 Test du service d'authentification PresencePro")
    print("=" * 50)
    
    # Test de santé
    if not test_health():
        print("\n❌ Le service ne semble pas être en cours d'exécution.")
        print("   Lancez le service avec: uvicorn app.main:app --reload --port 8001")
        sys.exit(1)
    
    # Test du flux d'authentification
    test_auth_flow()
    
    print("\n✅ Tests terminés avec succès !")
    print("\n📚 Pour tester complètement le service:")
    print("   1. Créez un utilisateur admin en base")
    print("   2. Utilisez les endpoints /register et /login")
    print("   3. Testez les permissions avec différents rôles")

if __name__ == "__main__":
    main()
