"""
Configuration du service de reconnaissance faciale
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "face-recognition-service"
    service_version: str = "1.0.0"
    service_port: int = 8004
    host: str = "0.0.0.0"
    debug: bool = True
    
    # Database (SQLite pour stockage temporaire)
    database_url: str = "sqlite:///./face_recognition.db"
    
    # Computer Vision Configuration
    camera_index: int = 0  # Index de la webcam (0 par défaut)
    face_detection_model: str = "hog"  # "hog" ou "cnn"
    face_recognition_tolerance: float = 0.6  # Seuil de reconnaissance (plus bas = plus strict)
    max_face_distance: float = 0.6
    
    # Video Configuration
    video_width: int = 640
    video_height: int = 480
    video_fps: int = 30
    
    # Face Storage
    faces_directory: str = "./data/faces"
    temp_directory: str = "./data/temp"
    
    # Integration avec autres services
    auth_service_url: str = "http://localhost:8001"
    user_service_url: str = "http://localhost:8002"
    attendance_service_url: str = "http://localhost:8005"  # À créer plus tard
    
    # Security
    secret_key: str = "face-recognition-secret-key-change-in-production"
    algorithm: str = "HS256"
    
    # Recognition Settings
    recognition_confidence_threshold: float = 0.7
    max_faces_per_frame: int = 10
    face_encoding_model: str = "large"  # "small" ou "large"
    
    # Performance
    frame_skip: int = 2  # Traiter 1 frame sur N pour optimiser les performances
    max_concurrent_recognitions: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/face_recognition.log"
    
    class Config:
        env_file = ".env"


settings = Settings()
