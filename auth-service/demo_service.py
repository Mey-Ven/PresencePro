#!/usr/bin/env python3
"""
Script de démonstration du service d'authentification PresencePro.
Teste le service comme un utilisateur final.
"""

import requests
import json
import sys
from typing import Optional

BASE_URL = "http://localhost:8002"

class AuthServiceDemo:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.current_user = None

    def print_header(self, title: str):
        """Affiche un en-tête formaté."""
        print(f"\n{'='*60}")
        print(f"🔐 {title}")
        print(f"{'='*60}")

    def print_response(self, response: requests.Response, title: str = ""):
        """Affiche une réponse formatée."""
        if title:
            print(f"\n📋 {title}")
        print(f"Status: {response.status_code}")
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response: {response.text}")

    def test_health(self):
        """Test du endpoint de santé."""
        self.print_header("Test de santé du service")
        
        try:
            response = requests.get(f"{BASE_URL}/health")
            self.print_response(response, "Health Check")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

    def login(self, username: str, password: str):
        """Connexion utilisateur."""
        self.print_header(f"Connexion - {username}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"username": username, "password": password}
            )
            
            self.print_response(response, "Login")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                print("✅ Connexion réussie!")
                return True
            else:
                print("❌ Échec de la connexion")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

    def get_my_profile(self):
        """Récupère le profil de l'utilisateur connecté."""
        if not self.access_token:
            print("❌ Vous devez être connecté")
            return False

        self.print_header("Mon profil")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{BASE_URL}/api/v1/auth/roles/me", headers=headers)
            
            self.print_response(response, "Mon profil")
            
            if response.status_code == 200:
                self.current_user = response.json()
                return True
            return False
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

    def check_permissions(self, required_roles: list):
        """Vérifie les permissions pour des rôles spécifiques."""
        if not self.access_token:
            print("❌ Vous devez être connecté")
            return False

        self.print_header(f"Vérification des permissions - {required_roles}")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/roles/check",
                json={"required_roles": required_roles},
                headers=headers
            )
            
            self.print_response(response, "Vérification des permissions")
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

    def create_user(self, user_data: dict):
        """Crée un nouvel utilisateur (admin uniquement)."""
        if not self.access_token:
            print("❌ Vous devez être connecté")
            return False

        self.print_header(f"Création d'utilisateur - {user_data['username']}")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=user_data,
                headers=headers
            )
            
            self.print_response(response, "Création d'utilisateur")
            return response.status_code == 201
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

    def create_bulk_users(self, role: str, count: int, prefix: str = None):
        """Crée plusieurs utilisateurs en masse (admin uniquement)."""
        if not self.access_token:
            print("❌ Vous devez être connecté")
            return False

        self.print_header(f"Création en masse - {count} {role}s")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            data = {"role": role, "count": count}
            if prefix:
                data["prefix"] = prefix
                
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/register/bulk",
                json=data,
                headers=headers
            )
            
            self.print_response(response, "Création en masse")
            return response.status_code == 201
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

    def refresh_access_token(self):
        """Rafraîchit le token d'accès."""
        if not self.refresh_token:
            print("❌ Pas de refresh token disponible")
            return False

        self.print_header("Rafraîchissement du token")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/refresh-token",
                json={"refresh_token": self.refresh_token}
            )
            
            self.print_response(response, "Refresh Token")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                print("✅ Token rafraîchi avec succès!")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

    def demo_admin_flow(self):
        """Démonstration du flux administrateur."""
        print("\n🎭 DÉMONSTRATION - FLUX ADMINISTRATEUR")
        
        # Connexion admin
        if not self.login("admin", "admin123"):
            return False
        
        # Profil admin
        self.get_my_profile()
        
        # Vérification permissions admin
        self.check_permissions(["admin"])
        
        # Création d'un utilisateur
        new_user = {
            "username": "demo_teacher",
            "password": "demo123",
            "role": "enseignant",
            "first_name": "Demo",
            "last_name": "Teacher",
            "email": "demo.teacher@school.com"
        }
        self.create_user(new_user)
        
        # Création en masse
        self.create_bulk_users("etudiant", 3, "demo_class")
        
        return True

    def demo_user_flow(self):
        """Démonstration du flux utilisateur normal."""
        print("\n🎭 DÉMONSTRATION - FLUX UTILISATEUR")
        
        # Connexion enseignant
        if not self.login("teacher1", "teacher123"):
            return False
        
        # Profil enseignant
        self.get_my_profile()
        
        # Vérification permissions (devrait échouer pour admin)
        self.check_permissions(["admin"])
        
        # Vérification permissions (devrait réussir pour enseignant)
        self.check_permissions(["enseignant"])
        
        # Tentative de création d'utilisateur (devrait échouer)
        new_user = {
            "username": "unauthorized_user",
            "password": "test123",
            "role": "etudiant"
        }
        self.create_user(new_user)
        
        return True

    def run_demo(self):
        """Lance la démonstration complète."""
        print("🚀 DÉMONSTRATION DU SERVICE D'AUTHENTIFICATION PRESENCEPRO")
        print("=" * 70)
        
        # Test de santé
        if not self.test_health():
            print("❌ Le service n'est pas accessible")
            return False
        
        # Démonstration admin
        demo = AuthServiceDemo()  # Nouvelle instance pour admin
        demo.demo_admin_flow()
        
        # Démonstration utilisateur
        demo = AuthServiceDemo()  # Nouvelle instance pour user
        demo.demo_user_flow()
        
        print("\n🎉 DÉMONSTRATION TERMINÉE!")
        print("\n📚 Endpoints disponibles:")
        print(f"   - Documentation: {BASE_URL}/docs")
        print(f"   - Health: {BASE_URL}/health")
        print(f"   - API: {BASE_URL}/api/v1/auth/")
        
        return True

def main():
    """Fonction principale."""
    demo = AuthServiceDemo()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo.run_demo()
        elif sys.argv[1] == "login":
            username = input("Username: ")
            password = input("Password: ")
            demo.login(username, password)
            if demo.access_token:
                demo.get_my_profile()
        else:
            print("Usage: python demo_service.py [demo|login]")
    else:
        demo.run_demo()

if __name__ == "__main__":
    main()
