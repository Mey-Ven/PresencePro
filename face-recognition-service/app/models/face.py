"""
Modèles de données pour la reconnaissance faciale
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, LargeBinary
from sqlalchemy.sql import func
from app.core.database import Base


class FaceEncoding(Base):
    """Modèle pour stocker les encodages de visages"""
    __tablename__ = "face_encodings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    encoding = Column(LargeBinary, nullable=False)  # Encodage du visage (numpy array sérialisé)
    confidence = Column(Float, default=0.0)
    image_path = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FaceEncoding(user_id='{self.user_id}', name='{self.name}')>"


class RecognitionLog(Base):
    """Modèle pour logger les reconnaissances"""
    __tablename__ = "recognition_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=True, index=True)
    name = Column(String(100), nullable=True)
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    camera_id = Column(String(50), default="default")
    status = Column(String(20), default="recognized")  # recognized, unknown, failed
    image_path = Column(String(255), nullable=True)
    attendance_recorded = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<RecognitionLog(user_id='{self.user_id}', confidence={self.confidence})>"


class CameraSession(Base):
    """Modèle pour gérer les sessions de caméra"""
    __tablename__ = "camera_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    camera_id = Column(String(50), default="default")
    status = Column(String(20), default="active")  # active, stopped, error
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    total_detections = Column(Integer, default=0)
    total_recognitions = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<CameraSession(session_id='{self.session_id}', status='{self.status}')>"
