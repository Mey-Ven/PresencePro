"""
Routes WebSocket pour la messagerie en temps réel
"""
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Query
from typing import Optional

from app.websockets.connection_manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="Token JWT pour l'authentification")
):
    """
    Endpoint WebSocket principal pour la messagerie en temps réel
    
    Paramètres:
    - token: Token JWT optionnel pour l'authentification immédiate
    
    Messages supportés:
    - authentication: Authentification avec token JWT
    - message: Envoi d'un message
    - message_read: Marquer un message comme lu
    - message_typing: Notification de frappe
    - message_stop_typing: Arrêt de frappe
    - ping: Test de connexion
    """
    connection_id = await connection_manager.connect(websocket)
    
    try:
        # Authentification immédiate si token fourni
        if token:
            await connection_manager.authenticate_connection(connection_id, token)
        
        # Boucle de traitement des messages
        while True:
            try:
                # Recevoir un message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Traiter le message
                await connection_manager.handle_message(connection_id, message_data)
                
            except WebSocketDisconnect:
                logger.info(f"Connexion WebSocket fermée par le client: {connection_id}")
                break
                
            except json.JSONDecodeError:
                logger.warning(f"Message JSON invalide reçu sur connexion {connection_id}")
                if connection_id in connection_manager.active_connections:
                    connection = connection_manager.active_connections[connection_id]
                    await connection.send_error("INVALID_JSON", "Format JSON invalide")
                
            except Exception as e:
                logger.error(f"Erreur traitement message WebSocket {connection_id}: {e}")
                if connection_id in connection_manager.active_connections:
                    connection = connection_manager.active_connections[connection_id]
                    await connection.send_error("PROCESSING_ERROR", "Erreur de traitement")
    
    except Exception as e:
        logger.error(f"Erreur connexion WebSocket {connection_id}: {e}")
    
    finally:
        # Nettoyer la connexion
        await connection_manager.disconnect(connection_id)


@router.websocket("/ws/conversation/{conversation_id}")
async def websocket_conversation_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: Optional[str] = Query(None, description="Token JWT pour l'authentification")
):
    """
    Endpoint WebSocket spécifique à une conversation
    
    Paramètres:
    - conversation_id: ID de la conversation à rejoindre
    - token: Token JWT pour l'authentification
    """
    connection_id = await connection_manager.connect(websocket)
    
    try:
        # Authentification requise pour les conversations spécifiques
        if not token:
            connection = connection_manager.active_connections[connection_id]
            await connection.send_error("AUTH_REQUIRED", "Token d'authentification requis")
            return
        
        # Authentifier la connexion
        auth_success = await connection_manager.authenticate_connection(connection_id, token)
        if not auth_success:
            return
        
        # Ajouter la connexion à la conversation
        connection = connection_manager.active_connections[connection_id]
        connection.subscribed_conversations.add(conversation_id)
        
        if conversation_id not in connection_manager.conversation_connections:
            connection_manager.conversation_connections[conversation_id] = set()
        connection_manager.conversation_connections[conversation_id].add(connection_id)
        
        # Confirmer la connexion à la conversation
        await connection.send_success(
            f"Connecté à la conversation {conversation_id}",
            {"conversation_id": conversation_id}
        )
        
        logger.info(f"Connexion {connection_id} rejointe conversation {conversation_id}")
        
        # Boucle de traitement des messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Ajouter automatiquement l'ID de conversation
                if "conversation_id" not in message_data:
                    message_data["conversation_id"] = conversation_id
                
                await connection_manager.handle_message(connection_id, message_data)
                
            except WebSocketDisconnect:
                logger.info(f"Connexion WebSocket conversation fermée: {connection_id}")
                break
                
            except json.JSONDecodeError:
                logger.warning(f"Message JSON invalide sur conversation {conversation_id}")
                await connection.send_error("INVALID_JSON", "Format JSON invalide")
                
            except Exception as e:
                logger.error(f"Erreur message conversation {conversation_id}: {e}")
                await connection.send_error("PROCESSING_ERROR", "Erreur de traitement")
    
    except Exception as e:
        logger.error(f"Erreur connexion conversation {conversation_id}: {e}")
    
    finally:
        # Nettoyer la connexion
        await connection_manager.disconnect(connection_id)
