#!/usr/bin/env python3
"""
Script pour initialiser la base de données et créer un utilisateur admin.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajouter le répertoire app au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base
from app.models import User, UserRole
from app.auth import get_password_hash
from app.config import settings

def init_database():
    """Initialise la base de données et crée les tables."""
    print("🔧 Initialisation de la base de données...")
    
    # Créer l'engine
    engine = create_engine(settings.database_url)
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès")
    
    return engine

def create_admin_user(engine):
    """Crée un utilisateur administrateur par défaut."""
    print("👤 Création de l'utilisateur administrateur...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Vérifier si un admin existe déjà
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"⚠️  Un administrateur existe déjà: {existing_admin.username}")
            return existing_admin
        
        # Créer un nouvel admin
        admin_user = User(
            username="admin",
            email="admin@presencepro.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="System",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Utilisateur administrateur créé avec succès!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@presencepro.com")
        print("⚠️  CHANGEZ LE MOT DE PASSE EN PRODUCTION!")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'admin: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def create_sample_users(engine):
    """Crée quelques utilisateurs d'exemple."""
    print("👥 Création d'utilisateurs d'exemple...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    sample_users = [
        {
            "username": "teacher1",
            "email": "teacher1@school.com",
            "password": "teacher123",
            "role": UserRole.ENSEIGNANT,
            "first_name": "Marie",
            "last_name": "Dupont"
        },
        {
            "username": "student1",
            "email": "student1@school.com",
            "password": "student123",
            "role": UserRole.ETUDIANT,
            "first_name": "Jean",
            "last_name": "Martin"
        },
        {
            "username": "parent1",
            "email": "parent1@family.com",
            "password": "parent123",
            "role": UserRole.PARENT,
            "first_name": "Pierre",
            "last_name": "Martin"
        }
    ]
    
    created_users = []
    
    try:
        for user_data in sample_users:
            # Vérifier si l'utilisateur existe déjà
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                print(f"⚠️  L'utilisateur {user_data['username']} existe déjà")
                continue
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                is_active=True
            )
            
            db.add(user)
            created_users.append(user_data)
        
        db.commit()
        
        if created_users:
            print("✅ Utilisateurs d'exemple créés:")
            for user_data in created_users:
                print(f"   - {user_data['username']} ({user_data['role'].value}): {user_data['password']}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des utilisateurs d'exemple: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Fonction principale."""
    print("🚀 Initialisation du service d'authentification PresencePro")
    print("=" * 60)
    print(f"📊 Base de données: {settings.database_url}")
    print()
    
    try:
        # Initialiser la base de données
        engine = init_database()
        
        # Créer l'utilisateur admin
        admin_user = create_admin_user(engine)
        if not admin_user:
            print("❌ Impossible de créer l'utilisateur admin")
            sys.exit(1)
        
        # Créer des utilisateurs d'exemple
        create_sample_users(engine)
        
        print()
        print("🎉 Initialisation terminée avec succès!")
        print()
        print("📝 Prochaines étapes:")
        print("   1. Lancez le service: uvicorn app.main:app --reload --port 8001")
        print("   2. Testez l'API: http://localhost:8001/docs")
        print("   3. Connectez-vous avec admin/admin123")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
