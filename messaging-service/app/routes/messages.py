"""
Routes REST pour la messagerie
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
import logging

from app.models.message import (
    MessageCreate, MessageResponse, MessageHistory, ConversationCreate,
    ConversationResponse, ConversationList, UserStatusResponse
)
from app.services.auth_service import get_current_user, auth_service
from app.services.messaging_service import MessagingService
from app.websockets.connection_manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])

# Instance du service de messagerie
messaging_service = MessagingService()


@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Envoyer un message
    
    - **conversation_id**: ID de la conversation (optionnel si recipient_id fourni)
    - **recipient_id**: ID du destinataire (pour créer une nouvelle conversation)
    - **content**: Contenu du message
    - **message_type**: Type de message (text, image, file, system)
    - **reply_to**: ID du message auquel on répond (optionnel)
    """
    try:
        # Vérifier les permissions de messagerie
        if message_data.recipient_id:
            # TODO: Récupérer le rôle du destinataire
            recipient_role = "parent"  # Placeholder
            
            if not auth_service.can_message_user(current_user["role"], recipient_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous n'êtes pas autorisé à envoyer un message à cet utilisateur"
                )
        
        # Envoyer le message
        message_response = await messaging_service.send_message(
            message_data,
            current_user["user_id"],
            current_user["display_name"],
            current_user["role"]
        )
        
        logger.info(f"Message envoyé par {current_user['user_id']}: {message_response.message_id}")
        return message_response
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur envoi message: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")


@router.get("/history/{conversation_id}", response_model=MessageHistory)
async def get_message_history(
    conversation_id: str,
    page: int = Query(1, ge=1, description="Numéro de page"),
    limit: int = Query(50, ge=1, le=100, description="Nombre de messages par page"),
    before_message_id: Optional[str] = Query(None, description="ID du message avant lequel récupérer"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Récupérer l'historique des messages d'une conversation
    
    - **conversation_id**: ID de la conversation
    - **page**: Numéro de page (défaut: 1)
    - **limit**: Nombre de messages par page (défaut: 50, max: 100)
    - **before_message_id**: Pour la pagination, récupérer les messages avant ce message
    """
    try:
        history = await messaging_service.get_message_history(
            conversation_id,
            current_user["user_id"],
            page,
            limit,
            before_message_id
        )
        
        return history
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur récupération historique: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")


@router.post("/mark-read/{message_id}")
async def mark_message_as_read(
    message_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Marquer un message comme lu
    
    - **message_id**: ID du message à marquer comme lu
    """
    try:
        success = await messaging_service.mark_message_as_read(
            message_id,
            current_user["user_id"]
        )
        
        if success:
            return {"message": "Message marqué comme lu", "success": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message non trouvé ou déjà lu"
            )
            
    except Exception as e:
        logger.error(f"Erreur marquage message lu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")


@router.get("/conversations", response_model=ConversationList)
async def get_user_conversations(
    page: int = Query(1, ge=1, description="Numéro de page"),
    limit: int = Query(20, ge=1, le=50, description="Nombre de conversations par page"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Récupérer les conversations de l'utilisateur actuel
    
    - **page**: Numéro de page (défaut: 1)
    - **limit**: Nombre de conversations par page (défaut: 20, max: 50)
    """
    try:
        conversations = await messaging_service.get_user_conversations(
            current_user["user_id"],
            page,
            limit
        )
        
        return conversations
        
    except Exception as e:
        logger.error(f"Erreur récupération conversations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Créer une nouvelle conversation
    
    - **participant_ids**: Liste des IDs des participants
    - **conversation_type**: Type de conversation (direct, group, support)
    - **title**: Titre de la conversation (optionnel, requis pour les groupes)
    - **description**: Description de la conversation (optionnel)
    """
    try:
        # Vérifier les permissions
        permissions = await auth_service.get_user_conversations_permissions(
            current_user["user_id"],
            current_user["role"]
        )
        
        # Vérifier le nombre de participants
        if len(conversation_data.participant_ids) > permissions["max_participants_per_conversation"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Nombre maximum de participants dépassé ({permissions['max_participants_per_conversation']})"
            )
        
        # Vérifier les rôles des participants
        for participant_id in conversation_data.participant_ids:
            if participant_id != current_user["user_id"]:
                # TODO: Récupérer le rôle du participant
                participant_role = "parent"  # Placeholder
                
                if participant_role not in permissions["allowed_recipient_roles"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Vous n'êtes pas autorisé à créer une conversation avec ce type d'utilisateur"
                    )
        
        # Créer la conversation
        conversation = await messaging_service.create_conversation(
            conversation_data,
            current_user["user_id"],
            current_user["display_name"]
        )
        
        logger.info(f"Conversation créée par {current_user['user_id']}: {conversation.conversation_id}")
        return conversation
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur création conversation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Récupérer les détails d'une conversation
    
    - **conversation_id**: ID de la conversation
    """
    try:
        # TODO: Implémenter la récupération d'une conversation spécifique
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Fonctionnalité en cours de développement"
        )
        
    except Exception as e:
        logger.error(f"Erreur récupération conversation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")


@router.get("/stats")
async def get_messaging_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Récupérer les statistiques de messagerie de l'utilisateur
    """
    try:
        # TODO: Implémenter les statistiques utilisateur
        stats = {
            "total_conversations": 0,
            "unread_messages": 0,
            "total_messages_sent": 0,
            "total_messages_received": 0,
            "active_conversations": 0
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")


@router.get("/online-users", response_model=List[UserStatusResponse])
async def get_online_users(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Récupérer la liste des utilisateurs en ligne
    """
    try:
        # TODO: Implémenter la récupération des utilisateurs en ligne
        online_users = []
        
        return online_users
        
    except Exception as e:
        logger.error(f"Erreur récupération utilisateurs en ligne: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")


@router.get("/websocket/stats")
async def get_websocket_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Récupérer les statistiques des connexions WebSocket (admin seulement)
    """
    try:
        if current_user["role"] not in ["admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions administrateur requises"
            )
        
        stats = connection_manager.get_connection_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération stats WebSocket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")
