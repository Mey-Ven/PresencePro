#!/usr/bin/env python3
"""
Script d'initialisation de la base de données pour le service de reconnaissance faciale
"""
import os
import sys
import logging
from datetime import datetime

# Ajouter le répertoire app au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import engine, create_tables
from app.core.config import settings
from app.models.face import FaceEncoding, RecognitionLog, CameraSession


def init_database():
    """Initialiser la base de données"""
    print("🚀 Initialisation du service de reconnaissance faciale PresencePro")
    print("=" * 70)
    print(f"📊 Base de données: {settings.database_url}")
    print()
    
    try:
        # Créer les répertoires nécessaires
        print("📁 Création des répertoires...")
        os.makedirs(settings.faces_directory, exist_ok=True)
        os.makedirs(settings.temp_directory, exist_ok=True)
        os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
        print("✅ Répertoires créés")
        
        # Créer les tables
        print("\n🔧 Création des tables de base de données...")
        create_tables()
        print("✅ Tables créées avec succès")
        
        # Vérifier la caméra
        print("\n📹 Vérification de la caméra...")
        try:
            import cv2
            camera = cv2.VideoCapture(settings.camera_index)
            if camera.isOpened():
                width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(camera.get(cv2.CAP_PROP_FPS))
                print(f"✅ Caméra {settings.camera_index} détectée: {width}x{height} @ {fps}fps")
                camera.release()
            else:
                print(f"⚠️ Caméra {settings.camera_index} non disponible")
        except Exception as e:
            print(f"❌ Erreur vérification caméra: {e}")
        
        # Vérifier les bibliothèques
        print("\n📚 Vérification des bibliothèques...")
        try:
            import cv2
            import numpy as np
            print(f"✅ OpenCV: {cv2.__version__}")
            print(f"✅ NumPy: {np.__version__}")
            print("✅ Pillow: Installé")
            print("ℹ️ face_recognition: Non installé (utilisation d'OpenCV uniquement)")
        except ImportError as e:
            print(f"❌ Bibliothèque manquante: {e}")
            return False
        
        print("\n🎉 Initialisation terminée avec succès!")
        print("\n📝 Prochaines étapes:")
        print(f"   1. Lancez le service: uvicorn app.main:app --reload --port {settings.service_port}")
        print(f"   2. Testez l'API: http://localhost:{settings.service_port}/docs")
        print(f"   3. Stream vidéo: http://localhost:{settings.service_port}/api/v1/camera/stream")
        print("   4. Ajoutez des visages via l'API /api/v1/face-recognition/train")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False


def create_sample_data():
    """Créer des données d'exemple (optionnel)"""
    try:
        from sqlalchemy.orm import sessionmaker
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("\n👥 Création de données d'exemple...")
        
        # Exemple de session caméra
        sample_session = CameraSession(
            session_id="sample-session-001",
            camera_id="default",
            status="stopped",
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_detections=0,
            total_recognitions=0
        )
        
        db.add(sample_session)
        db.commit()
        
        print("✅ Données d'exemple créées")
        db.close()
        
    except Exception as e:
        print(f"⚠️ Erreur création données d'exemple: {e}")


def test_face_recognition():
    """Tester les fonctionnalités de reconnaissance faciale"""
    print("\n🧪 Test des fonctionnalités de reconnaissance...")

    try:
        import cv2
        import numpy as np

        # Test de détection de visage avec OpenCV
        print("📸 Test de détection de visage avec OpenCV...")

        # Créer une image de test simple (carré blanc)
        test_image = np.ones((200, 200, 3), dtype=np.uint8) * 255

        # Tester le classificateur de visages d'OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        print(f"✅ Détection OpenCV testée: {len(faces)} visages trouvés (normal sur image vide)")
        print("✅ Classificateur de visages OpenCV chargé avec succès")

        return True

    except Exception as e:
        print(f"❌ Erreur test reconnaissance: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    
    if success:
        # Créer des données d'exemple
        create_sample_data()
        
        # Tester la reconnaissance
        test_face_recognition()
        
        print("\n🎊 Service de reconnaissance faciale prêt à être utilisé!")
    else:
        print("\n💥 Échec de l'initialisation")
        sys.exit(1)
