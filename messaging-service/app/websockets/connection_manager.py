"""
Gestionnaire de connexions WebSocket pour la messagerie en temps réel
"""
import json
import asyncio
import uuid
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect
import logging

from app.models.websocket_schemas import (
    WebSocketMessage, WebSocketMessageType, WebSocketAuthentication,
    WebSocketError, WebSocketSuccess, WebSocketChatMessage,
    WebSocketMessageReceived, WebSocketMessageSent, WebSocketTyping,
    WebSocketUserStatus, WebSocketPing, WebSocketPong
)
from app.models.message import OnlineStatus, UserRole, MessageCreate
from app.services.auth_service import auth_service
from app.services.messaging_service import MessagingService
from app.core.config import settings

logger = logging.getLogger(__name__)


class WebSocketConnection:
    """Représente une connexion WebSocket"""
    
    def __init__(self, websocket: WebSocket, connection_id: str):
        self.websocket = websocket
        self.connection_id = connection_id
        self.user_id: Optional[str] = None
        self.user_info: Optional[Dict[str, Any]] = None
        self.connected_at = datetime.now(timezone.utc)
        self.last_ping: Optional[datetime] = None
        self.is_authenticated = False
        self.subscribed_conversations: Set[str] = set()
    
    async def send_message(self, message: Dict[str, Any]):
        """Envoyer un message via WebSocket"""
        try:
            await self.websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Erreur envoi message WebSocket {self.connection_id}: {e}")
    
    async def send_error(self, error_code: str, error_message: str, details: Optional[Dict] = None):
        """Envoyer un message d'erreur"""
        error_msg = WebSocketError(
            error_code=error_code,
            error_message=error_message,
            details=details or {}
        )
        await self.send_message(error_msg.dict())
    
    async def send_success(self, message: str, data: Optional[Dict] = None):
        """Envoyer un message de succès"""
        success_msg = WebSocketSuccess(
            message=message,
            data=data or {}
        )
        await self.send_message(success_msg.dict())


class ConnectionManager:
    """Gestionnaire des connexions WebSocket"""
    
    def __init__(self):
        # Connexions actives par ID de connexion
        self.active_connections: Dict[str, WebSocketConnection] = {}
        
        # Connexions par utilisateur
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Connexions par conversation
        self.conversation_connections: Dict[str, Set[str]] = {}
        
        # Utilisateurs en train de taper par conversation
        self.typing_users: Dict[str, Dict[str, datetime]] = {}
        
        # Service de messagerie
        self.messaging_service = MessagingService()
        
        # Tâche de nettoyage des connexions inactives
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def connect(self, websocket: WebSocket) -> str:
        """Accepter une nouvelle connexion WebSocket"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        connection = WebSocketConnection(websocket, connection_id)
        
        self.active_connections[connection_id] = connection
        
        logger.info(f"Nouvelle connexion WebSocket: {connection_id}")
        
        # Démarrer la tâche de nettoyage si ce n'est pas déjà fait
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_inactive_connections())
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Déconnecter une connexion WebSocket"""
        if connection_id in self.active_connections:
            connection = self.active_connections[connection_id]
            
            # Retirer de toutes les structures de données
            if connection.user_id:
                await self._remove_user_connection(connection.user_id, connection_id)
            
            # Retirer des conversations
            for conv_id in connection.subscribed_conversations:
                if conv_id in self.conversation_connections:
                    self.conversation_connections[conv_id].discard(connection_id)
                    if not self.conversation_connections[conv_id]:
                        del self.conversation_connections[conv_id]
            
            # Supprimer la connexion
            del self.active_connections[connection_id]
            
            logger.info(f"Connexion WebSocket fermée: {connection_id}")
    
    async def authenticate_connection(self, connection_id: str, token: str) -> bool:
        """Authentifier une connexion WebSocket"""
        if connection_id not in self.active_connections:
            return False
        
        connection = self.active_connections[connection_id]
        
        # Vérifier le token
        user_info = await auth_service.authenticate_websocket_token(token)
        
        if not user_info:
            await connection.send_error("AUTH_FAILED", "Token invalide ou expiré")
            return False
        
        # Authentifier la connexion
        connection.user_id = user_info["user_id"]
        connection.user_info = user_info
        connection.is_authenticated = True
        
        # Ajouter aux connexions utilisateur
        if connection.user_id not in self.user_connections:
            self.user_connections[connection.user_id] = set()
        self.user_connections[connection.user_id].add(connection_id)
        
        # Mettre à jour le statut utilisateur
        await self._update_user_online_status(connection.user_id, OnlineStatus.ONLINE)
        
        # Envoyer confirmation d'authentification
        await connection.send_message({
            "type": WebSocketMessageType.AUTHENTICATED,
            "user_info": user_info,
            "timestamp": datetime.now(timezone.utc)
        })
        
        logger.info(f"Connexion {connection_id} authentifiée pour utilisateur {connection.user_id}")
        return True
    
    async def handle_message(self, connection_id: str, message_data: Dict[str, Any]):
        """Traiter un message WebSocket reçu"""
        if connection_id not in self.active_connections:
            return
        
        connection = self.active_connections[connection_id]
        
        try:
            message_type = message_data.get("type")
            
            if message_type == WebSocketMessageType.AUTHENTICATION:
                token = message_data.get("token")
                if token:
                    await self.authenticate_connection(connection_id, token)
                else:
                    await connection.send_error("AUTH_REQUIRED", "Token manquant")
            
            elif not connection.is_authenticated:
                await connection.send_error("AUTH_REQUIRED", "Authentification requise")
                return
            
            elif message_type == WebSocketMessageType.MESSAGE:
                await self._handle_chat_message(connection, message_data)
            
            elif message_type == WebSocketMessageType.MESSAGE_READ:
                await self._handle_message_read(connection, message_data)
            
            elif message_type == WebSocketMessageType.MESSAGE_TYPING:
                await self._handle_typing(connection, message_data)
            
            elif message_type == WebSocketMessageType.MESSAGE_STOP_TYPING:
                await self._handle_stop_typing(connection, message_data)
            
            elif message_type == WebSocketMessageType.PING:
                await self._handle_ping(connection, message_data)
            
            else:
                await connection.send_error("UNKNOWN_MESSAGE_TYPE", f"Type de message inconnu: {message_type}")
        
        except Exception as e:
            logger.error(f"Erreur traitement message WebSocket: {e}")
            await connection.send_error("PROCESSING_ERROR", "Erreur de traitement du message")
    
    async def _handle_chat_message(self, connection: WebSocketConnection, message_data: Dict[str, Any]):
        """Traiter un message de chat"""
        try:
            # Créer le message
            message_create = MessageCreate(
                conversation_id=message_data.get("conversation_id"),
                recipient_id=message_data.get("recipient_id"),
                content=message_data.get("content", ""),
                message_type=message_data.get("message_type", "text"),
                reply_to=message_data.get("reply_to"),
                metadata=message_data.get("metadata", {})
            )
            
            # Envoyer via le service de messagerie
            message_response = await self.messaging_service.send_message(
                message_create,
                connection.user_id,
                connection.user_info["display_name"],
                UserRole(connection.user_info["role"])
            )
            
            # Confirmer l'envoi à l'expéditeur
            sent_confirmation = WebSocketMessageSent(
                message_id=message_response.message_id,
                conversation_id=message_response.conversation_id,
                status=message_response.status,
                timestamp=message_response.created_at
            )
            await connection.send_message(sent_confirmation.dict())
            
            # Diffuser le message aux autres participants
            await self._broadcast_message_to_conversation(
                message_response.conversation_id,
                message_response,
                exclude_connection=connection.connection_id
            )
            
        except Exception as e:
            logger.error(f"Erreur envoi message chat: {e}")
            await connection.send_error("MESSAGE_SEND_FAILED", str(e))
    
    async def _handle_message_read(self, connection: WebSocketConnection, message_data: Dict[str, Any]):
        """Traiter la lecture d'un message"""
        message_id = message_data.get("message_id")
        if not message_id:
            return
        
        success = await self.messaging_service.mark_message_as_read(message_id, connection.user_id)
        
        if success:
            # Notifier les autres participants
            conversation_id = message_data.get("conversation_id")
            if conversation_id:
                read_notification = {
                    "type": WebSocketMessageType.MESSAGE_READ,
                    "message_id": message_id,
                    "conversation_id": conversation_id,
                    "read_by": connection.user_id,
                    "read_at": datetime.now(timezone.utc)
                }
                
                await self._broadcast_to_conversation(
                    conversation_id,
                    read_notification,
                    exclude_connection=connection.connection_id
                )
    
    async def _handle_typing(self, connection: WebSocketConnection, message_data: Dict[str, Any]):
        """Traiter la notification de frappe"""
        conversation_id = message_data.get("conversation_id")
        if not conversation_id:
            return
        
        # Enregistrer l'utilisateur comme en train de taper
        if conversation_id not in self.typing_users:
            self.typing_users[conversation_id] = {}
        
        self.typing_users[conversation_id][connection.user_id] = datetime.now(timezone.utc)
        
        # Diffuser aux autres participants
        typing_notification = WebSocketTyping(
            conversation_id=conversation_id,
            user_id=connection.user_id,
            user_name=connection.user_info["display_name"],
            is_typing=True
        )
        
        await self._broadcast_to_conversation(
            conversation_id,
            typing_notification.dict(),
            exclude_connection=connection.connection_id
        )
    
    async def _handle_stop_typing(self, connection: WebSocketConnection, message_data: Dict[str, Any]):
        """Traiter l'arrêt de frappe"""
        conversation_id = message_data.get("conversation_id")
        if not conversation_id:
            return
        
        # Retirer l'utilisateur de la liste des utilisateurs en train de taper
        if conversation_id in self.typing_users and connection.user_id in self.typing_users[conversation_id]:
            del self.typing_users[conversation_id][connection.user_id]
            
            if not self.typing_users[conversation_id]:
                del self.typing_users[conversation_id]
        
        # Diffuser aux autres participants
        stop_typing_notification = WebSocketTyping(
            type=WebSocketMessageType.MESSAGE_STOP_TYPING,
            conversation_id=conversation_id,
            user_id=connection.user_id,
            user_name=connection.user_info["display_name"],
            is_typing=False
        )
        
        await self._broadcast_to_conversation(
            conversation_id,
            stop_typing_notification.dict(),
            exclude_connection=connection.connection_id
        )
    
    async def _handle_ping(self, connection: WebSocketConnection, message_data: Dict[str, Any]):
        """Traiter un ping"""
        connection.last_ping = datetime.now(timezone.utc)
        
        pong = WebSocketPong()
        await connection.send_message(pong.dict())
    
    async def _broadcast_message_to_conversation(
        self,
        conversation_id: str,
        message_response,
        exclude_connection: Optional[str] = None
    ):
        """Diffuser un message à tous les participants d'une conversation"""
        message_notification = WebSocketMessageReceived(
            message_id=message_response.message_id,
            conversation_id=message_response.conversation_id,
            sender_id=message_response.sender_id,
            sender_name=message_response.sender_name,
            sender_role=message_response.sender_role,
            content=message_response.content,
            message_type=message_response.message_type,
            reply_to=message_response.reply_to,
            timestamp=message_response.created_at
        )
        
        await self._broadcast_to_conversation(
            conversation_id,
            message_notification.dict(),
            exclude_connection
        )
    
    async def _broadcast_to_conversation(
        self,
        conversation_id: str,
        message: Dict[str, Any],
        exclude_connection: Optional[str] = None
    ):
        """Diffuser un message à toutes les connexions d'une conversation"""
        if conversation_id not in self.conversation_connections:
            return
        
        connections_to_notify = self.conversation_connections[conversation_id].copy()
        if exclude_connection:
            connections_to_notify.discard(exclude_connection)
        
        for connection_id in connections_to_notify:
            if connection_id in self.active_connections:
                await self.active_connections[connection_id].send_message(message)
    
    async def _update_user_online_status(self, user_id: str, status: OnlineStatus):
        """Mettre à jour le statut en ligne d'un utilisateur"""
        # TODO: Mettre à jour dans la base de données
        # TODO: Notifier les contacts de l'utilisateur
        pass
    
    async def _remove_user_connection(self, user_id: str, connection_id: str):
        """Retirer une connexion d'un utilisateur"""
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                # Mettre à jour le statut à offline
                await self._update_user_online_status(user_id, OnlineStatus.OFFLINE)
    
    async def _cleanup_inactive_connections(self):
        """Nettoyer les connexions inactives"""
        while True:
            try:
                await asyncio.sleep(60)  # Vérifier toutes les minutes
                
                now = datetime.now(timezone.utc)
                inactive_connections = []
                
                for connection_id, connection in self.active_connections.items():
                    # Vérifier si la connexion est inactive
                    if connection.last_ping:
                        time_since_ping = (now - connection.last_ping).total_seconds()
                        if time_since_ping > settings.websocket_ping_timeout * 3:
                            inactive_connections.append(connection_id)
                    else:
                        # Pas de ping reçu, vérifier le temps de connexion
                        time_since_connect = (now - connection.connected_at).total_seconds()
                        if time_since_connect > 300:  # 5 minutes sans ping
                            inactive_connections.append(connection_id)
                
                # Fermer les connexions inactives
                for connection_id in inactive_connections:
                    logger.info(f"Fermeture connexion inactive: {connection_id}")
                    await self.disconnect(connection_id)
                
            except Exception as e:
                logger.error(f"Erreur nettoyage connexions: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques des connexions"""
        return {
            "total_connections": len(self.active_connections),
            "authenticated_connections": len([c for c in self.active_connections.values() if c.is_authenticated]),
            "users_online": len(self.user_connections),
            "active_conversations": len(self.conversation_connections),
            "typing_users": sum(len(users) for users in self.typing_users.values())
        }


# Instance globale du gestionnaire de connexions
connection_manager = ConnectionManager()
