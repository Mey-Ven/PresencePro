#!/usr/bin/env python3
"""
Script pour configurer Supabase avec le service d'authentification.
"""

import os
import sys

def setup_supabase_env():
    """Configure l'environnement pour Supabase."""
    print("🔧 Configuration Supabase pour PresencePro Auth Service")
    print("=" * 60)
    
    # Demander les informations Supabase
    project_ref = input("📋 Project Reference (ex: abcdefghijklmnop): ").strip()
    if not project_ref:
        print("❌ Project Reference requis")
        return False
    
    password = input("🔑 Database Password: ").strip()
    if not password:
        print("❌ Password requis")
        return False
    
    supabase_url = input(f"🌐 Supabase URL (défaut: https://{project_ref}.supabase.co): ").strip()
    if not supabase_url:
        supabase_url = f"https://{project_ref}.supabase.co"
    
    anon_key = input("🔐 Anon Key (optionnel): ").strip()
    service_key = input("🔐 Service Role Key (optionnel): ").strip()
    
    # Créer le fichier .env.production
    env_content = f"""# Database Configuration - Supabase Production
DATABASE_URL=postgresql://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars-for-security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Configuration
APP_NAME=PresencePro Auth Service
DEBUG=False
HOST=0.0.0.0
PORT=8001

# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_ANON_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_key}
"""
    
    try:
        with open('.env.production', 'w') as f:
            f.write(env_content)
        
        print("✅ Fichier .env.production créé avec succès!")
        print("\n📝 Prochaines étapes:")
        print("   1. Copiez .env.production vers .env pour utiliser Supabase")
        print("   2. Ou gardez .env actuel pour SQLite local")
        print("   3. Lancez: python init_db.py (pour créer les tables)")
        print("   4. Lancez: uvicorn app.main:app --port 8001")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier: {e}")
        return False

def test_supabase_connection():
    """Teste la connexion à Supabase."""
    print("\n🧪 Test de connexion Supabase...")
    
    if not os.path.exists('.env.production'):
        print("❌ Fichier .env.production non trouvé")
        return False
    
    # Charger les variables d'environnement de production
    import subprocess
    result = subprocess.run([
        'python', '-c', 
        '''
import os
from dotenv import load_dotenv
load_dotenv(".env.production")
from app.database import engine
try:
    with engine.connect() as conn:
        print("✅ Connexion Supabase réussie!")
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
'''
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return "✅" in result.stdout

def main():
    """Fonction principale."""
    print("🚀 Configuration Supabase pour PresencePro")
    print()
    
    choice = input("Que voulez-vous faire?\n1. Configurer Supabase\n2. Tester la connexion\n3. Quitter\nChoix (1-3): ").strip()
    
    if choice == "1":
        setup_supabase_env()
    elif choice == "2":
        test_supabase_connection()
    elif choice == "3":
        print("👋 Au revoir!")
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    main()
