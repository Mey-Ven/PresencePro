#!/usr/bin/env python3
"""
Script de démonstration du service de reconnaissance faciale
"""
import asyncio
import httpx
import base64
import json
import time
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np


class FaceRecognitionDemo:
    """Démonstration du service de reconnaissance faciale"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def create_demo_face(self, name: str, color: str = "lightblue") -> str:
        """Créer un visage de démonstration avec un nom"""
        # Créer une image 300x300
        image = Image.new('RGB', (300, 300), 'white')
        draw = ImageDraw.Draw(image)
        
        # Dessiner un visage stylisé
        # Tête
        draw.ellipse([50, 50, 250, 250], fill=color, outline='black', width=3)
        
        # Yeux
        draw.ellipse([100, 120, 130, 150], fill='black')
        draw.ellipse([170, 120, 200, 150], fill='black')
        
        # Nez
        draw.polygon([(150, 160), (140, 180), (160, 180)], fill='pink')
        
        # Bouche
        draw.arc([120, 190, 180, 220], 0, 180, fill='red', width=4)
        
        # Ajouter le nom
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (300 - text_width) // 2
        draw.text((text_x, 260), name, fill='black', font=font)
        
        # Convertir en base64
        import io
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        image_data = buffer.getvalue()
        return base64.b64encode(image_data).decode('utf-8')
    
    async def demo_service_info(self):
        """Démonstration des informations du service"""
        print("🔍 Informations du service")
        print("-" * 40)
        
        try:
            # Health check
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Service: {health.get('service')}")
                print(f"📊 Version: {health.get('version')}")
                print(f"📹 Caméra: {'✅ Disponible' if health.get('camera_available') else '❌ Non disponible'}")
                print(f"🧠 Encodages: {health.get('total_encodings', 0)}")
            
            # Informations détaillées
            response = await self.client.get(f"{self.base_url}/info")
            if response.status_code == 200:
                info = response.json()
                config = info.get('configuration', {})
                print(f"📐 Résolution: {config.get('video_resolution')}")
                print(f"🎯 Modèle: {config.get('face_detection_model')}")
                print(f"🔧 Tolérance: {config.get('face_recognition_tolerance')}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    async def demo_face_training(self):
        """Démonstration de l'entraînement de visages"""
        print("\n🎓 Entraînement de visages")
        print("-" * 40)
        
        # Créer des utilisateurs de démonstration
        demo_users = [
            {"id": "demo_001", "name": "Alice Dupont", "color": "lightblue"},
            {"id": "demo_002", "name": "Bob Martin", "color": "lightgreen"},
            {"id": "demo_003", "name": "Claire Durand", "color": "lightpink"}
        ]
        
        for user in demo_users:
            print(f"\n👤 Entraînement pour {user['name']}...")
            
            # Créer plusieurs images pour l'utilisateur
            images = []
            for i in range(3):
                # Varier légèrement la couleur pour simuler différentes conditions
                colors = [user['color'], 'lightcyan', 'lightyellow']
                image = self.create_demo_face(user['name'], colors[i])
                images.append(image)
            
            # Entraîner le modèle
            training_data = {
                "user_id": user['id'],
                "name": user['name'],
                "images": images
            }
            
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/face-recognition/train",
                    json=training_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ Entraînement réussi: {result.get('encodings_created')} encodages")
                    else:
                        print(f"❌ Échec: {result.get('message')}")
                else:
                    print(f"❌ Erreur HTTP: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
            
            # Petite pause entre les utilisateurs
            await asyncio.sleep(1)
    
    async def demo_face_recognition(self):
        """Démonstration de la reconnaissance"""
        print("\n🔍 Test de reconnaissance")
        print("-" * 40)
        
        # Créer une image de test pour Alice
        test_image = self.create_demo_face("Alice Dupont", "lightblue")
        
        detection_data = {
            "image_data": test_image,
            "camera_id": "demo"
        }
        
        try:
            print("📸 Test de reconnaissance sur image d'Alice...")
            response = await self.client.post(
                f"{self.base_url}/api/v1/face-recognition/detect",
                json=detection_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"👥 Visages détectés: {result.get('faces_detected', 0)}")
                print(f"⏱️ Temps de traitement: {result.get('processing_time', 0):.3f}s")
                
                recognitions = result.get('recognitions', [])
                for i, recognition in enumerate(recognitions):
                    status = recognition.get('status')
                    name = recognition.get('name', 'Inconnu')
                    confidence = recognition.get('confidence', 0)
                    
                    if status == "recognized":
                        print(f"✅ Reconnaissance {i+1}: {name} (confiance: {confidence:.3f})")
                    else:
                        print(f"❓ Reconnaissance {i+1}: {status}")
            else:
                print(f"❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    async def demo_camera_test(self):
        """Démonstration du test de caméra"""
        print("\n📹 Test de caméra")
        print("-" * 40)
        
        try:
            # Statut de la caméra
            response = await self.client.get(f"{self.base_url}/api/v1/camera/status")
            if response.status_code == 200:
                status = response.json()
                print(f"📹 Statut: {status.get('status')}")
                print(f"🔧 Disponible: {'✅' if status.get('is_available') else '❌'}")
                if status.get('resolution'):
                    print(f"📐 Résolution: {status.get('resolution')}")
                
                # Test de capture si disponible
                if status.get('is_available'):
                    print("\n📸 Test de capture...")
                    response = await self.client.get(f"{self.base_url}/api/v1/camera/capture")
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            print("✅ Capture réussie")
                            image_size = len(result.get('image', ''))
                            print(f"📊 Taille image: {image_size} caractères base64")
                        else:
                            print("❌ Capture échouée")
                else:
                    print("⚠️ Caméra non disponible pour la capture")
            else:
                print(f"❌ Erreur statut caméra: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    async def demo_statistics(self):
        """Démonstration des statistiques"""
        print("\n📊 Statistiques du service")
        print("-" * 40)
        
        try:
            # Statistiques de reconnaissance
            response = await self.client.get(f"{self.base_url}/api/v1/face-recognition/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"🧠 Total encodages: {stats.get('total_encodings', 0)}")
                print(f"🔍 Total reconnaissances: {stats.get('total_recognitions', 0)}")
                print(f"✅ Reconnaissances réussies: {stats.get('successful_recognitions', 0)}")
                print(f"📈 Taux de succès: {stats.get('success_rate', 0):.1%}")
            
            # Liste des visages enregistrés
            response = await self.client.get(f"{self.base_url}/api/v1/face-recognition/faces")
            if response.status_code == 200:
                faces = response.json()
                print(f"\n👥 Visages enregistrés: {len(faces)}")
                for face in faces[:5]:  # Afficher les 5 premiers
                    print(f"   • {face.get('name')} (ID: {face.get('user_id')})")
            
            # Logs récents
            response = await self.client.get(f"{self.base_url}/api/v1/face-recognition/recognition-logs?limit=5")
            if response.status_code == 200:
                logs = response.json()
                print(f"\n📝 Logs récents: {len(logs)} entrées")
                for log in logs:
                    timestamp = log.get('timestamp', '')[:19]
                    status = log.get('status')
                    name = log.get('name', 'Inconnu')
                    confidence = log.get('confidence', 0)
                    print(f"   • {timestamp}: {name} - {status} ({confidence:.3f})")
                    
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    async def run_full_demo(self):
        """Exécuter la démonstration complète"""
        print("🎭 Démonstration du Face Recognition Service")
        print("=" * 60)
        print("Cette démonstration va:")
        print("1. Afficher les informations du service")
        print("2. Entraîner le système avec des visages de démonstration")
        print("3. Tester la reconnaissance")
        print("4. Tester la caméra")
        print("5. Afficher les statistiques")
        print()
        
        # Vérifier que le service est disponible
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code != 200:
                print("❌ Service non disponible. Assurez-vous qu'il est démarré sur le port 8004")
                return False
        except Exception as e:
            print(f"❌ Impossible de se connecter au service: {e}")
            return False
        
        # Exécuter les démonstrations
        await self.demo_service_info()
        await self.demo_face_training()
        await self.demo_face_recognition()
        await self.demo_camera_test()
        await self.demo_statistics()
        
        print("\n" + "=" * 60)
        print("🎉 Démonstration terminée!")
        print("\n📝 Prochaines étapes:")
        print("   1. Accédez à la documentation: http://localhost:8004/docs")
        print("   2. Testez le streaming: http://localhost:8004/api/v1/camera/stream")
        print("   3. Ajoutez de vrais visages via l'API")
        print("   4. Intégrez avec votre système de présence")
        
        return True


async def main():
    """Fonction principale"""
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        async with FaceRecognitionDemo() as demo:
            await demo.run_full_demo()
    else:
        print("Usage: python demo_service.py demo")
        print("Assurez-vous que le service est démarré sur le port 8004")


if __name__ == "__main__":
    asyncio.run(main())
