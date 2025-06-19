"""
Service de gestion de la caméra et streaming vidéo
"""
import cv2
import asyncio
import base64
import threading
import time
import uuid
from typing import Optional, Generator, Dict, Any
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.core.config import settings
from app.models.face import CameraSession
from app.services.face_recognition_service import FaceRecognitionService


class CameraService:
    """Service de gestion de la caméra et streaming en temps réel"""
    
    def __init__(self, db: Session):
        self.db = db
        self.camera = None
        self.is_streaming = False
        self.current_session = None
        self.frame_count = 0
        self.recognition_service = None
        self.logger = logging.getLogger(__name__)
        
        # Thread pour la reconnaissance en arrière-plan
        self.recognition_thread = None
        self.recognition_queue = []
        self.recognition_results = {}
        
    def initialize_camera(self, camera_index: int = None) -> bool:
        """Initialiser la caméra"""
        try:
            if camera_index is None:
                camera_index = settings.camera_index
            
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                self.logger.error(f"Impossible d'ouvrir la caméra {camera_index}")
                return False
            
            # Configurer la résolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, settings.video_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.video_height)
            self.camera.set(cv2.CAP_PROP_FPS, settings.video_fps)
            
            self.logger.info(f"Caméra {camera_index} initialisée avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation caméra: {e}")
            return False
    
    def release_camera(self):
        """Libérer la caméra"""
        try:
            if self.camera and self.camera.isOpened():
                self.camera.release()
                self.logger.info("Caméra libérée")
        except Exception as e:
            self.logger.error(f"Erreur libération caméra: {e}")
    
    def is_camera_available(self) -> bool:
        """Vérifier si la caméra est disponible"""
        return self.camera is not None and self.camera.isOpened()
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Obtenir les informations de la caméra"""
        if not self.is_camera_available():
            return {"available": False}
        
        try:
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.camera.get(cv2.CAP_PROP_FPS))
            
            return {
                "available": True,
                "resolution": f"{width}x{height}",
                "fps": fps,
                "width": width,
                "height": height
            }
        except Exception as e:
            self.logger.error(f"Erreur récupération info caméra: {e}")
            return {"available": False}
    
    def capture_frame(self) -> Optional[bytes]:
        """Capturer une frame de la caméra"""
        if not self.is_camera_available():
            return None
        
        try:
            ret, frame = self.camera.read()
            if not ret:
                return None
            
            # Encoder la frame en JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
            
        except Exception as e:
            self.logger.error(f"Erreur capture frame: {e}")
            return None
    
    def capture_frame_base64(self) -> Optional[str]:
        """Capturer une frame et la retourner en base64"""
        frame_bytes = self.capture_frame()
        if frame_bytes:
            return base64.b64encode(frame_bytes).decode('utf-8')
        return None
    
    def start_session(self, camera_id: str = "default") -> str:
        """Démarrer une session de caméra"""
        try:
            session_id = str(uuid.uuid4())
            
            session = CameraSession(
                session_id=session_id,
                camera_id=camera_id,
                status="active",
                start_time=datetime.now()
            )
            
            self.db.add(session)
            self.db.commit()
            
            self.current_session = session
            self.frame_count = 0
            
            self.logger.info(f"Session caméra démarrée: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Erreur démarrage session: {e}")
            self.db.rollback()
            raise
    
    def stop_session(self):
        """Arrêter la session de caméra actuelle"""
        try:
            if self.current_session:
                self.current_session.status = "stopped"
                self.current_session.end_time = datetime.now()
                self.db.commit()
                
                self.logger.info(f"Session caméra arrêtée: {self.current_session.session_id}")
                self.current_session = None
            
        except Exception as e:
            self.logger.error(f"Erreur arrêt session: {e}")
            self.db.rollback()
    
    def start_streaming(self, recognition_enabled: bool = True):
        """Démarrer le streaming avec reconnaissance optionnelle"""
        if self.is_streaming:
            return
        
        self.is_streaming = True
        
        if recognition_enabled and not self.recognition_service:
            self.recognition_service = FaceRecognitionService(self.db)
        
        # Démarrer le thread de reconnaissance si activé
        if recognition_enabled:
            self.recognition_thread = threading.Thread(
                target=self._recognition_worker,
                daemon=True
            )
            self.recognition_thread.start()
        
        self.logger.info("Streaming démarré")
    
    def stop_streaming(self):
        """Arrêter le streaming"""
        self.is_streaming = False
        
        if self.recognition_thread:
            self.recognition_thread.join(timeout=2)
            self.recognition_thread = None
        
        self.logger.info("Streaming arrêté")
    
    def _recognition_worker(self):
        """Worker thread pour la reconnaissance en arrière-plan"""
        while self.is_streaming:
            try:
                if len(self.recognition_queue) > 0:
                    frame_data = self.recognition_queue.pop(0)
                    
                    # Traiter la reconnaissance
                    if self.recognition_service:
                        result = self.recognition_service.process_image(
                            frame_data["image"], 
                            frame_data.get("camera_id", "default")
                        )
                        
                        # Stocker le résultat
                        self.recognition_results[frame_data["frame_id"]] = result
                        
                        # Nettoyer les anciens résultats (garder seulement les 10 derniers)
                        if len(self.recognition_results) > 10:
                            oldest_key = min(self.recognition_results.keys())
                            del self.recognition_results[oldest_key]
                
                time.sleep(0.1)  # Éviter une boucle trop rapide
                
            except Exception as e:
                self.logger.error(f"Erreur worker reconnaissance: {e}")
    
    def add_frame_for_recognition(self, frame_base64: str, camera_id: str = "default") -> str:
        """Ajouter une frame à la queue de reconnaissance"""
        frame_id = str(uuid.uuid4())
        
        # Limiter la taille de la queue
        if len(self.recognition_queue) >= settings.max_concurrent_recognitions:
            self.recognition_queue.pop(0)  # Supprimer la plus ancienne
        
        self.recognition_queue.append({
            "frame_id": frame_id,
            "image": frame_base64,
            "camera_id": camera_id,
            "timestamp": datetime.now()
        })
        
        return frame_id
    
    def get_recognition_result(self, frame_id: str):
        """Récupérer le résultat de reconnaissance pour une frame"""
        return self.recognition_results.get(frame_id)
    
    def generate_frames(self, with_recognition: bool = True) -> Generator[bytes, None, None]:
        """Générateur de frames pour streaming HTTP"""
        if not self.is_camera_available():
            return
        
        frame_skip_counter = 0
        
        while self.is_streaming:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    break
                
                self.frame_count += 1
                
                # Traitement de reconnaissance (optionnel et avec skip de frames)
                if with_recognition and frame_skip_counter % settings.frame_skip == 0:
                    # Convertir frame en base64 pour reconnaissance
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Ajouter à la queue de reconnaissance
                    frame_id = self.add_frame_for_recognition(frame_base64)
                    
                    # Récupérer les résultats récents et les dessiner
                    for result_frame_id, recognition_result in list(self.recognition_results.items()):
                        if recognition_result and recognition_result.recognitions:
                            frame = self._draw_recognition_results(frame, recognition_result.recognitions)
                
                frame_skip_counter += 1
                
                # Encoder la frame pour streaming
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                # Contrôler le FPS
                time.sleep(1.0 / settings.video_fps)
                
            except Exception as e:
                self.logger.error(f"Erreur génération frame: {e}")
                break
    
    def _draw_recognition_results(self, frame, recognitions):
        """Dessiner les résultats de reconnaissance sur la frame"""
        for recognition in recognitions:
            if recognition.bounding_box:
                left, top, right, bottom = recognition.bounding_box
                
                # Couleur selon le statut
                color = (0, 255, 0) if recognition.status == "recognized" else (0, 0, 255)
                
                # Dessiner le rectangle
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Dessiner le nom et la confiance
                label = f"{recognition.name} ({recognition.confidence:.2f})"
                cv2.putText(frame, label, (left, top - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame
