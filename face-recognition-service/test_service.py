#!/usr/bin/env python3
"""
Script de test et validation du service de reconnaissance faciale
"""
import asyncio
import httpx
import base64
import json
import time
import os
from datetime import datetime
from PIL import Image, ImageDraw
import numpy as np


class FaceRecognitionTester:
    """Testeur pour le service de reconnaissance faciale"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def create_test_face_image(self, width: int = 200, height: int = 200) -> str:
        """Créer une image de test avec un visage simple"""
        # Créer une image avec un cercle (simule un visage)
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Dessiner un cercle pour la tête
        margin = 50
        draw.ellipse([margin, margin, width-margin, height-margin], fill='lightblue', outline='blue')
        
        # Dessiner des yeux
        eye_size = 10
        left_eye_x = width // 3
        right_eye_x = 2 * width // 3
        eye_y = height // 3
        
        draw.ellipse([left_eye_x-eye_size, eye_y-eye_size, left_eye_x+eye_size, eye_y+eye_size], fill='black')
        draw.ellipse([right_eye_x-eye_size, eye_y-eye_size, right_eye_x+eye_size, eye_y+eye_size], fill='black')
        
        # Dessiner une bouche
        mouth_y = 2 * height // 3
        draw.arc([width//3, mouth_y-10, 2*width//3, mouth_y+10], 0, 180, fill='red', width=3)
        
        # Convertir en base64
        import io
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_data = buffer.getvalue()
        return base64.b64encode(image_data).decode('utf-8')
    
    async def test_health_check(self):
        """Tester le health check"""
        print("1. Test de santé du service...")
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Service en bonne santé")
                print(f"   📊 Encodages: {health_data.get('total_encodings', 0)}")
                print(f"   📹 Caméra: {'✅' if health_data.get('camera_available') else '❌'}")
                return True
            else:
                print(f"❌ Service non disponible (code: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Impossible de se connecter au service: {e}")
            return False
    
    async def test_camera_status(self):
        """Tester le statut de la caméra"""
        print("\n2. Test du statut de la caméra...")
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/camera/status")
            if response.status_code == 200:
                camera_data = response.json()
                print(f"✅ Statut caméra: {camera_data.get('status')}")
                print(f"   📹 Disponible: {'✅' if camera_data.get('is_available') else '❌'}")
                if camera_data.get('resolution'):
                    print(f"   📐 Résolution: {camera_data.get('resolution')}")
                return True
            else:
                print(f"❌ Erreur statut caméra (code: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erreur test caméra: {e}")
            return False
    
    async def test_face_detection(self):
        """Tester la détection de visages"""
        print("\n3. Test de détection de visages...")
        try:
            # Créer une image de test
            test_image = self.create_test_face_image()
            
            detection_data = {
                "image_data": test_image,
                "camera_id": "test"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/face-recognition/detect",
                json=detection_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Détection réussie")
                print(f"   👥 Visages détectés: {result.get('faces_detected', 0)}")
                print(f"   ⏱️ Temps de traitement: {result.get('processing_time', 0):.3f}s")
                
                recognitions = result.get('recognitions', [])
                for i, recognition in enumerate(recognitions):
                    print(f"   🔍 Reconnaissance {i+1}: {recognition.get('status')} (confiance: {recognition.get('confidence', 0):.3f})")
                
                return True
            else:
                print(f"❌ Erreur détection (code: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erreur test détection: {e}")
            return False
    
    async def test_face_training(self):
        """Tester l'entraînement de visages"""
        print("\n4. Test d'entraînement de visages...")
        try:
            # Créer plusieurs images de test pour un utilisateur
            test_images = [
                self.create_test_face_image(200, 200),
                self.create_test_face_image(180, 180),
                self.create_test_face_image(220, 220)
            ]
            
            training_data = {
                "user_id": "test_user_001",
                "name": "Utilisateur Test",
                "images": test_images
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/face-recognition/train",
                json=training_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Entraînement: {'réussi' if result.get('success') else 'échoué'}")
                print(f"   📝 Message: {result.get('message')}")
                print(f"   🧠 Encodages créés: {result.get('encodings_created', 0)}")
                return result.get('success', False)
            else:
                print(f"❌ Erreur entraînement (code: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erreur test entraînement: {e}")
            return False
    
    async def test_face_list(self):
        """Tester la liste des visages"""
        print("\n5. Test de liste des visages...")
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/face-recognition/faces")
            
            if response.status_code == 200:
                faces = response.json()
                print(f"✅ Liste récupérée: {len(faces)} visages enregistrés")
                
                for face in faces[:3]:  # Afficher les 3 premiers
                    print(f"   👤 {face.get('name')} (ID: {face.get('user_id')})")
                
                return True
            else:
                print(f"❌ Erreur liste visages (code: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erreur test liste: {e}")
            return False
    
    async def test_recognition_logs(self):
        """Tester les logs de reconnaissance"""
        print("\n6. Test des logs de reconnaissance...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/face-recognition/recognition-logs?limit=5"
            )
            
            if response.status_code == 200:
                logs = response.json()
                print(f"✅ Logs récupérés: {len(logs)} entrées")
                
                for log in logs[:3]:  # Afficher les 3 premiers
                    timestamp = log.get('timestamp', '')[:19]  # Tronquer les microsecondes
                    print(f"   📝 {timestamp}: {log.get('status')} (confiance: {log.get('confidence', 0):.3f})")
                
                return True
            else:
                print(f"❌ Erreur logs (code: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erreur test logs: {e}")
            return False
    
    async def test_statistics(self):
        """Tester les statistiques"""
        print("\n7. Test des statistiques...")
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/face-recognition/stats")
            
            if response.status_code == 200:
                stats = response.json()
                print("✅ Statistiques récupérées:")
                print(f"   🧠 Total encodages: {stats.get('total_encodings', 0)}")
                print(f"   🔍 Total reconnaissances: {stats.get('total_recognitions', 0)}")
                print(f"   ✅ Reconnaissances réussies: {stats.get('successful_recognitions', 0)}")
                print(f"   📊 Taux de succès: {stats.get('success_rate', 0):.1%}")
                return True
            else:
                print(f"❌ Erreur statistiques (code: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erreur test statistiques: {e}")
            return False
    
    async def test_camera_capture(self):
        """Tester la capture de caméra"""
        print("\n8. Test de capture caméra...")
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/camera/capture")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Capture réussie")
                    image_data = result.get('image', '')
                    print(f"   📸 Taille image: {len(image_data)} caractères base64")
                    return True
                else:
                    print("❌ Capture échouée")
                    return False
            else:
                print(f"❌ Erreur capture (code: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erreur test capture: {e}")
            return False
    
    async def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🧪 Test complet du Face Recognition Service")
        print("=" * 60)
        
        tests = [
            self.test_health_check,
            self.test_camera_status,
            self.test_face_detection,
            self.test_face_training,
            self.test_face_list,
            self.test_recognition_logs,
            self.test_statistics,
            self.test_camera_capture
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ Erreur inattendue: {e}")
        
        print("\n" + "=" * 60)
        print("📋 RÉSUMÉ DES TESTS")
        print("=" * 60)
        print(f"Tests réussis: {passed}/{total}")
        print(f"Taux de réussite: {passed/total:.1%}")
        
        if passed == total:
            print("\n🎉 TOUS LES TESTS ONT RÉUSSI !")
            print("Le service Face Recognition est entièrement fonctionnel.")
        else:
            print(f"\n⚠️ {total-passed} test(s) ont échoué")
            print("Vérifiez les erreurs ci-dessus.")
        
        return passed == total


async def main():
    """Fonction principale"""
    print("🎯 Testeur du Face Recognition Service")
    print("=" * 50)
    
    async with FaceRecognitionTester() as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n📝 Prochaines étapes:")
            print("   1. Testez le streaming: http://localhost:8004/api/v1/camera/stream")
            print("   2. Ajoutez de vrais visages via l'API")
            print("   3. Intégrez avec l'attendance-service")
        
        return success


if __name__ == "__main__":
    asyncio.run(main())
