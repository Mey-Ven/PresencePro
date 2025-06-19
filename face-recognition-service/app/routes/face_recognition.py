"""
Routes pour la reconnaissance faciale
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
import base64
import io

from app.core.database import get_db
from app.services.face_recognition_service import FaceRecognitionService
from app.services.camera_service import CameraService
from app.services.attendance_integration import AttendanceProcessor
from app.models.schemas import (
    FaceDetectionRequest, FaceDetectionResponse, TrainingRequest, TrainingResponse,
    FaceEncodingCreate, FaceEncoding, RecognitionLog
)

router = APIRouter()

# Instance globale du processeur de présence
attendance_processor = AttendanceProcessor()


@router.post("/detect", response_model=FaceDetectionResponse)
async def detect_faces(
    request: FaceDetectionRequest,
    db: Session = Depends(get_db)
):
    """Détecter et reconnaître les visages dans une image"""
    try:
        service = FaceRecognitionService(db)
        result = service.process_image(request.image_data, request.camera_id)
        
        # Traiter les reconnaissances pour l'attendance
        for recognition in result.recognitions:
            if recognition.status == "recognized":
                await attendance_processor.process_recognition(recognition, request.camera_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur détection: {str(e)}")


@router.post("/train", response_model=TrainingResponse)
async def train_face(
    request: TrainingRequest,
    db: Session = Depends(get_db)
):
    """Entraîner le système avec de nouvelles images d'un utilisateur"""
    try:
        service = FaceRecognitionService(db)
        encodings_created = 0
        errors = []
        
        for i, image_data in enumerate(request.images):
            try:
                success = service.add_face_encoding(
                    request.user_id, 
                    request.name, 
                    image_data
                )
                if success:
                    encodings_created += 1
                else:
                    errors.append(f"Image {i+1}: Échec de l'encodage")
            except Exception as e:
                errors.append(f"Image {i+1}: {str(e)}")
        
        if encodings_created > 0:
            return TrainingResponse(
                success=True,
                message=f"Entraînement réussi. {encodings_created} encodages créés.",
                encodings_created=encodings_created
            )
        else:
            return TrainingResponse(
                success=False,
                message=f"Échec de l'entraînement. Erreurs: {'; '.join(errors)}",
                encodings_created=0
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur entraînement: {str(e)}")


@router.post("/upload-face")
async def upload_face_image(
    user_id: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload d'une image de visage via formulaire multipart"""
    try:
        # Vérifier le type de fichier
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Le fichier doit être une image")
        
        # Lire et encoder l'image
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Ajouter l'encodage
        service = FaceRecognitionService(db)
        success = service.add_face_encoding(user_id, name, image_base64)
        
        if success:
            return {"success": True, "message": f"Visage ajouté pour {name}"}
        else:
            raise HTTPException(status_code=400, detail="Impossible d'encoder le visage")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur upload: {str(e)}")


@router.delete("/faces/{user_id}")
async def remove_user_faces(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Supprimer tous les visages d'un utilisateur"""
    try:
        service = FaceRecognitionService(db)
        success = service.remove_face_encoding(user_id)
        
        if success:
            return {"success": True, "message": f"Visages supprimés pour l'utilisateur {user_id}"}
        else:
            raise HTTPException(status_code=400, detail="Impossible de supprimer les visages")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur suppression: {str(e)}")


@router.get("/faces", response_model=List[FaceEncoding])
async def list_face_encodings(
    user_id: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Lister les encodages de visages"""
    try:
        from app.models.face import FaceEncoding as FaceEncodingModel
        
        query = db.query(FaceEncodingModel)
        
        if user_id:
            query = query.filter(FaceEncodingModel.user_id == user_id)
        
        if active_only:
            query = query.filter(FaceEncodingModel.is_active == True)
        
        encodings = query.all()
        return encodings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération: {str(e)}")


@router.get("/recognition-logs", response_model=List[RecognitionLog])
async def get_recognition_logs(
    user_id: Optional[str] = None,
    camera_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupérer les logs de reconnaissance"""
    try:
        from app.models.face import RecognitionLog as RecognitionLogModel
        
        query = db.query(RecognitionLogModel)
        
        if user_id:
            query = query.filter(RecognitionLogModel.user_id == user_id)
        
        if camera_id:
            query = query.filter(RecognitionLogModel.camera_id == camera_id)
        
        logs = query.order_by(RecognitionLogModel.timestamp.desc()).limit(limit).all()
        return logs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération logs: {str(e)}")


@router.get("/stats")
async def get_recognition_stats(db: Session = Depends(get_db)):
    """Obtenir les statistiques de reconnaissance"""
    try:
        service = FaceRecognitionService(db)
        stats = service.get_recognition_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur statistiques: {str(e)}")


@router.post("/reload-faces")
async def reload_known_faces(db: Session = Depends(get_db)):
    """Recharger les visages connus depuis la base de données"""
    try:
        service = FaceRecognitionService(db)
        service.load_known_faces()
        return {"success": True, "message": "Visages rechargés avec succès"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur rechargement: {str(e)}")
