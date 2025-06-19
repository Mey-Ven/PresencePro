"""
Schémas Pydantic pour la validation des données
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FaceEncodingBase(BaseModel):
    user_id: str = Field(..., description="ID de l'utilisateur")
    name: str = Field(..., description="Nom de l'utilisateur")
    confidence: Optional[float] = Field(0.0, description="Niveau de confiance")
    is_active: Optional[bool] = Field(True, description="Encodage actif")


class FaceEncodingCreate(FaceEncodingBase):
    encoding_data: str = Field(..., description="Données d'encodage base64")
    image_path: Optional[str] = Field(None, description="Chemin de l'image")


class FaceEncodingUpdate(BaseModel):
    name: Optional[str] = None
    confidence: Optional[float] = None
    is_active: Optional[bool] = None


class FaceEncoding(FaceEncodingBase):
    id: int
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RecognitionResult(BaseModel):
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur reconnu")
    name: Optional[str] = Field(None, description="Nom de l'utilisateur")
    confidence: float = Field(..., description="Niveau de confiance de la reconnaissance")
    status: str = Field(..., description="Statut de la reconnaissance")
    timestamp: datetime = Field(..., description="Horodatage de la reconnaissance")
    bounding_box: Optional[List[int]] = Field(None, description="Coordonnées du rectangle de détection")


class RecognitionLogCreate(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    confidence: float
    camera_id: Optional[str] = "default"
    status: str = "recognized"
    image_path: Optional[str] = None


class RecognitionLog(BaseModel):
    id: int
    user_id: Optional[str] = None
    name: Optional[str] = None
    confidence: float
    timestamp: datetime
    camera_id: str
    status: str
    image_path: Optional[str] = None
    attendance_recorded: bool
    
    class Config:
        from_attributes = True


class CameraSessionCreate(BaseModel):
    camera_id: Optional[str] = "default"


class CameraSession(BaseModel):
    id: int
    session_id: str
    camera_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_detections: int
    total_recognitions: int
    
    class Config:
        from_attributes = True


class FaceDetectionRequest(BaseModel):
    image_data: str = Field(..., description="Image en base64")
    camera_id: Optional[str] = Field("default", description="ID de la caméra")


class FaceDetectionResponse(BaseModel):
    faces_detected: int = Field(..., description="Nombre de visages détectés")
    recognitions: List[RecognitionResult] = Field(..., description="Résultats de reconnaissance")
    processing_time: float = Field(..., description="Temps de traitement en secondes")


class TrainingRequest(BaseModel):
    user_id: str = Field(..., description="ID de l'utilisateur")
    name: str = Field(..., description="Nom de l'utilisateur")
    images: List[str] = Field(..., description="Liste d'images en base64")


class TrainingResponse(BaseModel):
    success: bool = Field(..., description="Succès de l'entraînement")
    message: str = Field(..., description="Message de résultat")
    encodings_created: int = Field(..., description="Nombre d'encodages créés")


class CameraStatus(BaseModel):
    camera_id: str = Field(..., description="ID de la caméra")
    status: str = Field(..., description="Statut de la caméra")
    is_available: bool = Field(..., description="Caméra disponible")
    resolution: Optional[str] = Field(None, description="Résolution de la caméra")
    fps: Optional[int] = Field(None, description="FPS de la caméra")


class ServiceHealth(BaseModel):
    status: str = Field(..., description="Statut du service")
    service: str = Field(..., description="Nom du service")
    version: str = Field(..., description="Version du service")
    camera_available: bool = Field(..., description="Caméra disponible")
    total_encodings: int = Field(..., description="Nombre total d'encodages")
    active_sessions: int = Field(..., description="Sessions actives")
