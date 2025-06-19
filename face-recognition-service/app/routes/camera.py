"""
Routes pour la gestion de la caméra et streaming
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import asyncio

from app.core.database import get_db
from app.services.camera_service import CameraService
from app.services.attendance_integration import AttendanceProcessor
from app.models.schemas import CameraStatus, CameraSessionCreate, CameraSession

router = APIRouter()

# Instance globale du service caméra
camera_service = None
attendance_processor = AttendanceProcessor()


def get_camera_service(db: Session = Depends(get_db)) -> CameraService:
    """Obtenir l'instance du service caméra"""
    global camera_service
    if camera_service is None:
        camera_service = CameraService(db)
        camera_service.initialize_camera()
    return camera_service


@router.get("/status", response_model=CameraStatus)
async def get_camera_status(
    camera_service: CameraService = Depends(get_camera_service)
):
    """Obtenir le statut de la caméra"""
    try:
        info = camera_service.get_camera_info()
        
        return CameraStatus(
            camera_id="default",
            status="active" if info.get("available", False) else "inactive",
            is_available=info.get("available", False),
            resolution=info.get("resolution"),
            fps=info.get("fps")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur statut caméra: {str(e)}")


@router.post("/initialize")
async def initialize_camera(
    camera_index: Optional[int] = None,
    camera_service: CameraService = Depends(get_camera_service)
):
    """Initialiser la caméra"""
    try:
        success = camera_service.initialize_camera(camera_index)
        
        if success:
            return {"success": True, "message": "Caméra initialisée avec succès"}
        else:
            raise HTTPException(status_code=400, detail="Impossible d'initialiser la caméra")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur initialisation: {str(e)}")


@router.post("/release")
async def release_camera(
    camera_service: CameraService = Depends(get_camera_service)
):
    """Libérer la caméra"""
    try:
        camera_service.release_camera()
        return {"success": True, "message": "Caméra libérée"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur libération: {str(e)}")


@router.get("/capture")
async def capture_frame(
    camera_service: CameraService = Depends(get_camera_service)
):
    """Capturer une frame de la caméra"""
    try:
        if not camera_service.is_camera_available():
            raise HTTPException(status_code=400, detail="Caméra non disponible")
        
        frame_base64 = camera_service.capture_frame_base64()
        
        if frame_base64:
            return {"success": True, "image": frame_base64}
        else:
            raise HTTPException(status_code=500, detail="Impossible de capturer une frame")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur capture: {str(e)}")


@router.get("/stream")
async def video_stream(
    with_recognition: bool = True,
    camera_service: CameraService = Depends(get_camera_service)
):
    """Stream vidéo en temps réel"""
    try:
        if not camera_service.is_camera_available():
            raise HTTPException(status_code=400, detail="Caméra non disponible")
        
        # Démarrer le streaming
        camera_service.start_streaming(recognition_enabled=with_recognition)
        
        return StreamingResponse(
            camera_service.generate_frames(with_recognition=with_recognition),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur streaming: {str(e)}")


@router.post("/stream/start")
async def start_streaming(
    with_recognition: bool = True,
    camera_service: CameraService = Depends(get_camera_service)
):
    """Démarrer le streaming"""
    try:
        if not camera_service.is_camera_available():
            raise HTTPException(status_code=400, detail="Caméra non disponible")
        
        camera_service.start_streaming(recognition_enabled=with_recognition)
        return {"success": True, "message": "Streaming démarré"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur démarrage streaming: {str(e)}")


@router.post("/stream/stop")
async def stop_streaming(
    camera_service: CameraService = Depends(get_camera_service)
):
    """Arrêter le streaming"""
    try:
        camera_service.stop_streaming()
        return {"success": True, "message": "Streaming arrêté"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur arrêt streaming: {str(e)}")


@router.post("/session/start", response_model=CameraSession)
async def start_camera_session(
    request: CameraSessionCreate,
    camera_service: CameraService = Depends(get_camera_service)
):
    """Démarrer une session de caméra"""
    try:
        session_id = camera_service.start_session(request.camera_id)
        
        # Récupérer la session créée
        session = camera_service.current_session
        return session
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur démarrage session: {str(e)}")


@router.post("/session/stop")
async def stop_camera_session(
    camera_service: CameraService = Depends(get_camera_service)
):
    """Arrêter la session de caméra actuelle"""
    try:
        camera_service.stop_session()
        return {"success": True, "message": "Session arrêtée"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur arrêt session: {str(e)}")


@router.get("/session/current")
async def get_current_session(
    camera_service: CameraService = Depends(get_camera_service)
):
    """Obtenir la session de caméra actuelle"""
    try:
        if camera_service.current_session:
            return camera_service.current_session
        else:
            return {"message": "Aucune session active"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération session: {str(e)}")


@router.get("/recognition-queue/status")
async def get_recognition_queue_status(
    camera_service: CameraService = Depends(get_camera_service)
):
    """Obtenir le statut de la queue de reconnaissance"""
    try:
        return {
            "queue_size": len(camera_service.recognition_queue),
            "results_cache_size": len(camera_service.recognition_results),
            "is_streaming": camera_service.is_streaming,
            "recognition_enabled": camera_service.recognition_service is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur statut queue: {str(e)}")


@router.post("/process-frame")
async def process_single_frame(
    background_tasks: BackgroundTasks,
    camera_service: CameraService = Depends(get_camera_service)
):
    """Traiter une seule frame pour reconnaissance"""
    try:
        if not camera_service.is_camera_available():
            raise HTTPException(status_code=400, detail="Caméra non disponible")
        
        # Capturer une frame
        frame_base64 = camera_service.capture_frame_base64()
        
        if not frame_base64:
            raise HTTPException(status_code=500, detail="Impossible de capturer une frame")
        
        # Ajouter à la queue de reconnaissance
        frame_id = camera_service.add_frame_for_recognition(frame_base64)
        
        return {
            "success": True,
            "frame_id": frame_id,
            "message": "Frame ajoutée à la queue de reconnaissance"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur traitement frame: {str(e)}")


@router.get("/recognition-result/{frame_id}")
async def get_frame_recognition_result(
    frame_id: str,
    camera_service: CameraService = Depends(get_camera_service)
):
    """Récupérer le résultat de reconnaissance pour une frame"""
    try:
        result = camera_service.get_recognition_result(frame_id)
        
        if result:
            return result
        else:
            return {"message": "Résultat non disponible", "status": "processing"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération résultat: {str(e)}")
