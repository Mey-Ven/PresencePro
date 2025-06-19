"""
Service de gestion des fichiers et documents
"""
import os
import uuid
from typing import Optional, List, Tuple
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from pathlib import Path

try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from app.models.justification import JustificationDocument
from app.models.schemas import JustificationDocumentResponse
from app.core.config import settings


class FileService:
    """Service de gestion des fichiers"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.upload_dir = Path(settings.upload_dir)
        self.max_file_size = settings.max_file_size
        self.allowed_types = settings.allowed_file_types_list
        
        # Créer le répertoire d'upload s'il n'existe pas
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_document(
        self,
        file: UploadFile,
        justification_id: int,
        uploaded_by: str,
        description: Optional[str] = None,
        is_primary: bool = False
    ) -> JustificationDocumentResponse:
        """Uploader un document pour une justification"""
        try:
            # Valider le fichier
            await self._validate_file(file)
            
            # Générer un nom de fichier unique
            file_extension = self._get_file_extension(file.filename)
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.upload_dir / str(justification_id) / unique_filename
            
            # Créer le répertoire de la justification
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder le fichier
            content = await file.read()
            if AIOFILES_AVAILABLE:
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(content)
            else:
                with open(file_path, 'wb') as f:
                    f.write(content)

            # Détecter le type MIME
            if MAGIC_AVAILABLE:
                mime_type = magic.from_file(str(file_path), mime=True)
            else:
                # Fallback basé sur l'extension
                extension = file_extension.lstrip('.').lower()
                mime_types = {
                    'pdf': 'application/pdf',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'doc': 'application/msword',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }
                mime_type = mime_types.get(extension, 'application/octet-stream')
            
            # Créer l'enregistrement en base
            document = JustificationDocument(
                justification_id=justification_id,
                filename=unique_filename,
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=len(content),
                file_type=file_extension.lstrip('.').lower(),
                mime_type=mime_type,
                description=description,
                is_primary=is_primary,
                uploaded_by=uploaded_by
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            self.logger.info(f"Document uploadé: {unique_filename} pour justification {justification_id}")
            return JustificationDocumentResponse.from_orm(document)
            
        except Exception as e:
            self.logger.error(f"Erreur upload document: {e}")
            # Nettoyer le fichier en cas d'erreur
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            raise
    
    async def get_document(self, document_id: int) -> Optional[JustificationDocumentResponse]:
        """Récupérer un document par ID"""
        try:
            document = self.db.query(JustificationDocument).filter(
                JustificationDocument.id == document_id
            ).first()
            
            if document:
                return JustificationDocumentResponse.from_orm(document)
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur récupération document: {e}")
            raise
    
    async def get_justification_documents(self, justification_id: int) -> List[JustificationDocumentResponse]:
        """Récupérer tous les documents d'une justification"""
        try:
            documents = self.db.query(JustificationDocument).filter(
                JustificationDocument.justification_id == justification_id
            ).order_by(JustificationDocument.is_primary.desc(), JustificationDocument.uploaded_at).all()
            
            return [JustificationDocumentResponse.from_orm(doc) for doc in documents]
            
        except Exception as e:
            self.logger.error(f"Erreur récupération documents justification: {e}")
            raise
    
    async def delete_document(self, document_id: int, deleted_by: str) -> bool:
        """Supprimer un document"""
        try:
            document = self.db.query(JustificationDocument).filter(
                JustificationDocument.id == document_id
            ).first()
            
            if not document:
                return False
            
            # Supprimer le fichier physique
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Supprimer l'enregistrement en base
            self.db.delete(document)
            self.db.commit()
            
            self.logger.info(f"Document {document_id} supprimé par {deleted_by}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur suppression document: {e}")
            raise
    
    async def get_file_content(self, document_id: int) -> Optional[Tuple[bytes, str, str]]:
        """Récupérer le contenu d'un fichier"""
        try:
            document = self.db.query(JustificationDocument).filter(
                JustificationDocument.id == document_id
            ).first()
            
            if not document:
                return None
            
            file_path = Path(document.file_path)
            if not file_path.exists():
                self.logger.error(f"Fichier physique non trouvé: {file_path}")
                return None
            
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            return content, document.original_filename, document.mime_type
            
        except Exception as e:
            self.logger.error(f"Erreur lecture fichier: {e}")
            raise
    
    async def _validate_file(self, file: UploadFile):
        """Valider un fichier uploadé"""
        # Vérifier la taille
        content = await file.read()
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"Fichier trop volumineux. Taille maximum: {self.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Remettre le curseur au début
        await file.seek(0)
        
        # Vérifier l'extension
        file_extension = self._get_file_extension(file.filename)
        if file_extension.lstrip('.').lower() not in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Type de fichier non autorisé. Types autorisés: {', '.join(self.allowed_types)}"
            )
        
        # Vérifier que le fichier n'est pas vide
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Le fichier est vide"
            )
    
    def _get_file_extension(self, filename: str) -> str:
        """Extraire l'extension d'un nom de fichier"""
        if not filename:
            return ""
        
        return Path(filename).suffix.lower()
    
    def get_upload_stats(self) -> dict:
        """Récupérer les statistiques d'upload"""
        try:
            total_documents = self.db.query(JustificationDocument).count()
            total_size = self.db.query(
                func.sum(JustificationDocument.file_size)
            ).scalar() or 0
            
            # Statistiques par type
            type_stats = self.db.query(
                JustificationDocument.file_type,
                func.count(JustificationDocument.id).label('count')
            ).group_by(JustificationDocument.file_type).all()
            
            return {
                "total_documents": total_documents,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "by_type": {stat.file_type: stat.count for stat in type_stats},
                "upload_directory": str(self.upload_dir),
                "max_file_size_mb": round(self.max_file_size / 1024 / 1024, 2),
                "allowed_types": self.allowed_types
            }
            
        except Exception as e:
            self.logger.error(f"Erreur statistiques upload: {e}")
            return {}
    
    def cleanup_orphaned_files(self) -> int:
        """Nettoyer les fichiers orphelins"""
        try:
            cleaned_count = 0
            
            # Récupérer tous les documents en base
            documents = self.db.query(JustificationDocument).all()
            db_files = {doc.file_path for doc in documents}
            
            # Parcourir les fichiers physiques
            for root, dirs, files in os.walk(self.upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Si le fichier n'est pas en base, le supprimer
                    if file_path not in db_files:
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                            self.logger.info(f"Fichier orphelin supprimé: {file_path}")
                        except Exception as e:
                            self.logger.error(f"Erreur suppression fichier orphelin {file_path}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Erreur nettoyage fichiers orphelins: {e}")
            return 0
