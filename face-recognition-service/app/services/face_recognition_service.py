"""
Service principal de reconnaissance faciale
"""
import cv2
# import face_recognition  # Commenté pour l'instant
import numpy as np
import pickle
import base64
import io
from PIL import Image
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import os

from app.core.config import settings
from app.models.face import FaceEncoding, RecognitionLog
from app.models.schemas import RecognitionResult, FaceDetectionResponse


class FaceRecognitionService:
    """Service de reconnaissance faciale utilisant OpenCV et face_recognition"""
    
    def __init__(self, db: Session):
        self.db = db
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.logger = logging.getLogger(__name__)
        
        # Charger les encodages existants
        self.load_known_faces()
    
    def load_known_faces(self):
        """Charger tous les encodages de visages depuis la base de données"""
        try:
            face_encodings = self.db.query(FaceEncoding).filter(
                FaceEncoding.is_active == True
            ).all()
            
            self.known_face_encodings = []
            self.known_face_names = []
            self.known_face_ids = []
            
            for face_encoding in face_encodings:
                # Désérialiser l'encodage
                encoding = pickle.loads(face_encoding.encoding)
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(face_encoding.name)
                self.known_face_ids.append(face_encoding.user_id)
            
            self.logger.info(f"Chargé {len(self.known_face_encodings)} encodages de visages")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des visages: {e}")
    
    def base64_to_image(self, base64_string: str) -> np.ndarray:
        """Convertir une image base64 en array numpy"""
        try:
            # Supprimer le préfixe data:image si présent
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            # Décoder base64
            image_data = base64.b64decode(base64_string)
            
            # Convertir en image PIL puis en array numpy
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Convertir RGB en BGR pour OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            return image_array
            
        except Exception as e:
            self.logger.error(f"Erreur conversion base64 vers image: {e}")
            raise ValueError(f"Image base64 invalide: {e}")
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Détecter les visages dans une image avec OpenCV"""
        try:
            # Convertir en niveaux de gris pour la détection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Charger le classificateur de visages d'OpenCV
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Détecter les visages
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            # Convertir au format (top, right, bottom, left) comme face_recognition
            face_locations = []
            for (x, y, w, h) in faces:
                top = y
                right = x + w
                bottom = y + h
                left = x
                face_locations.append((top, right, bottom, left))

            return face_locations

        except Exception as e:
            self.logger.error(f"Erreur détection de visages: {e}")
            return []
    
    def encode_faces(self, image: np.ndarray, face_locations: List[Tuple[int, int, int, int]]) -> List[np.ndarray]:
        """Encoder les visages détectés (version simplifiée avec OpenCV)"""
        try:
            # Pour cette version simplifiée, nous créons des "encodages" basiques
            # basés sur les caractéristiques de l'image du visage
            face_encodings = []

            for (top, right, bottom, left) in face_locations:
                # Extraire la région du visage
                face_image = image[top:bottom, left:right]

                if face_image.size > 0:
                    # Redimensionner à une taille fixe
                    face_resized = cv2.resize(face_image, (64, 64))

                    # Convertir en niveaux de gris et aplatir
                    face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
                    face_encoding = face_gray.flatten().astype(np.float64)

                    # Normaliser
                    face_encoding = face_encoding / 255.0

                    face_encodings.append(face_encoding)

            return face_encodings

        except Exception as e:
            self.logger.error(f"Erreur encodage de visages: {e}")
            return []
    
    def recognize_faces(self, face_encodings: List[np.ndarray]) -> List[RecognitionResult]:
        """Reconnaître les visages encodés"""
        results = []
        
        for face_encoding in face_encodings:
            user_id = None
            name = "Inconnu"
            confidence = 0.0
            status = "unknown"
            
            if len(self.known_face_encodings) > 0:
                # Comparer avec les visages connus (version simplifiée)
                face_distances = []

                for known_encoding in self.known_face_encodings:
                    # Calculer la distance euclidienne
                    distance = np.linalg.norm(face_encoding - known_encoding)
                    face_distances.append(distance)

                face_distances = np.array(face_distances)
                best_match_index = np.argmin(face_distances)
                best_distance = face_distances[best_match_index]

                # Vérifier si la distance est acceptable (seuil adapté pour notre méthode)
                tolerance = settings.face_recognition_tolerance * 100  # Adapter le seuil
                if best_distance <= tolerance:
                    user_id = self.known_face_ids[best_match_index]
                    name = self.known_face_names[best_match_index]
                    confidence = max(0.0, 1.0 - (best_distance / tolerance))  # Convertir distance en confiance
                    status = "recognized"
            
            result = RecognitionResult(
                user_id=user_id,
                name=name,
                confidence=confidence,
                status=status,
                timestamp=datetime.now()
            )
            
            results.append(result)
        
        return results
    
    def process_image(self, image_data: str, camera_id: str = "default") -> FaceDetectionResponse:
        """Traiter une image pour détecter et reconnaître les visages"""
        start_time = datetime.now()
        
        try:
            # Convertir l'image
            image = self.base64_to_image(image_data)
            
            # Détecter les visages
            face_locations = self.detect_faces(image)
            
            # Encoder les visages
            face_encodings = self.encode_faces(image, face_locations)
            
            # Reconnaître les visages
            recognitions = self.recognize_faces(face_encodings)
            
            # Ajouter les coordonnées des boîtes englobantes
            for i, recognition in enumerate(recognitions):
                if i < len(face_locations):
                    top, right, bottom, left = face_locations[i]
                    recognition.bounding_box = [left, top, right, bottom]
            
            # Logger les reconnaissances
            for recognition in recognitions:
                self.log_recognition(recognition, camera_id)
            
            # Calculer le temps de traitement
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return FaceDetectionResponse(
                faces_detected=len(face_locations),
                recognitions=recognitions,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Erreur traitement image: {e}")
            raise
    
    def log_recognition(self, recognition: RecognitionResult, camera_id: str):
        """Logger une reconnaissance dans la base de données"""
        try:
            log_entry = RecognitionLog(
                user_id=recognition.user_id,
                name=recognition.name,
                confidence=recognition.confidence,
                camera_id=camera_id,
                status=recognition.status,
                timestamp=recognition.timestamp
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Erreur logging reconnaissance: {e}")
            self.db.rollback()
    
    def add_face_encoding(self, user_id: str, name: str, image_data: str) -> bool:
        """Ajouter un nouvel encodage de visage"""
        try:
            # Convertir l'image
            image = self.base64_to_image(image_data)
            
            # Détecter les visages
            face_locations = self.detect_faces(image)
            
            if len(face_locations) != 1:
                raise ValueError(f"L'image doit contenir exactement un visage, {len(face_locations)} détecté(s)")
            
            # Encoder le visage
            face_encodings = self.encode_faces(image, face_locations)
            
            if len(face_encodings) != 1:
                raise ValueError("Impossible d'encoder le visage")
            
            # Sérialiser l'encodage
            encoding_data = pickle.dumps(face_encodings[0])
            
            # Sauvegarder en base de données
            face_encoding = FaceEncoding(
                user_id=user_id,
                name=name,
                encoding=encoding_data,
                confidence=1.0,
                is_active=True
            )
            
            self.db.add(face_encoding)
            self.db.commit()
            
            # Recharger les visages connus
            self.load_known_faces()
            
            self.logger.info(f"Nouvel encodage ajouté pour {name} (ID: {user_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur ajout encodage: {e}")
            self.db.rollback()
            return False
    
    def remove_face_encoding(self, user_id: str) -> bool:
        """Supprimer les encodages d'un utilisateur"""
        try:
            # Désactiver les encodages
            self.db.query(FaceEncoding).filter(
                FaceEncoding.user_id == user_id
            ).update({"is_active": False})
            
            self.db.commit()
            
            # Recharger les visages connus
            self.load_known_faces()
            
            self.logger.info(f"Encodages supprimés pour l'utilisateur {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur suppression encodage: {e}")
            self.db.rollback()
            return False
    
    def get_recognition_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de reconnaissance"""
        try:
            total_encodings = self.db.query(FaceEncoding).filter(
                FaceEncoding.is_active == True
            ).count()
            
            total_recognitions = self.db.query(RecognitionLog).count()
            
            successful_recognitions = self.db.query(RecognitionLog).filter(
                RecognitionLog.status == "recognized"
            ).count()
            
            return {
                "total_encodings": total_encodings,
                "total_recognitions": total_recognitions,
                "successful_recognitions": successful_recognitions,
                "success_rate": successful_recognitions / total_recognitions if total_recognitions > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Erreur récupération statistiques: {e}")
            return {}
