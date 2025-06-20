"""
Schémas pour les messages WebSocket
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from .message import MessageType, MessageStatus, OnlineStatus, UserRole


class WebSocketMessageType(str, Enum):
    """Types de messages WebSocket"""
    # Messages de chat
    MESSAGE = "message"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_READ = "message_read"
    MESSAGE_TYPING = "message_typing"
    MESSAGE_STOP_TYPING = "message_stop_typing"
    
    # Statuts utilisateur
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
    USER_STATUS_CHANGE = "user_status_change"
    
    # Conversations
    CONVERSATION_CREATED = "conversation_created"
    CONVERSATION_UPDATED = "conversation_updated"
    CONVERSATION_JOINED = "conversation_joined"
    CONVERSATION_LEFT = "conversation_left"
    
    # Système
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    SUCCESS = "success"
    AUTHENTICATION = "authentication"
    AUTHENTICATED = "authenticated"
    UNAUTHORIZED = "unauthorized"


class WebSocketMessage(BaseModel):
    """Message WebSocket générique"""
    type: WebSocketMessageType
    data: Optional[Dict[str, Any]] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_id: Optional[str] = None


class WebSocketChatMessage(BaseModel):
    """Message de chat via WebSocket"""
    type: WebSocketMessageType = WebSocketMessageType.MESSAGE
    conversation_id: Optional[str] = None
    recipient_id: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: MessageType = MessageType.TEXT
    reply_to: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class WebSocketMessageSent(BaseModel):
    """Confirmation d'envoi de message"""
    type: WebSocketMessageType = WebSocketMessageType.MESSAGE_SENT
    message_id: str
    conversation_id: str
    status: MessageStatus
    timestamp: datetime


class WebSocketMessageReceived(BaseModel):
    """Notification de réception de message"""
    type: WebSocketMessageType = WebSocketMessageType.MESSAGE_RECEIVED
    message_id: str
    conversation_id: str
    sender_id: str
    sender_name: str
    sender_role: UserRole
    content: str
    message_type: MessageType
    reply_to: Optional[str] = None
    timestamp: datetime


class WebSocketMessageRead(BaseModel):
    """Notification de lecture de message"""
    type: WebSocketMessageType = WebSocketMessageType.MESSAGE_READ
    message_id: str
    conversation_id: str
    read_by: str
    read_at: datetime


class WebSocketTyping(BaseModel):
    """Notification de frappe"""
    type: WebSocketMessageType = WebSocketMessageType.MESSAGE_TYPING
    conversation_id: str
    user_id: str
    user_name: str
    is_typing: bool = True


class WebSocketUserStatus(BaseModel):
    """Notification de changement de statut utilisateur"""
    type: WebSocketMessageType = WebSocketMessageType.USER_STATUS_CHANGE
    user_id: str
    username: str
    display_name: str
    online_status: OnlineStatus
    last_seen: Optional[datetime] = None


class WebSocketConversationEvent(BaseModel):
    """Événement de conversation"""
    type: WebSocketMessageType
    conversation_id: str
    user_id: str
    user_name: str
    action: str  # created, updated, joined, left
    data: Optional[Dict[str, Any]] = {}


class WebSocketAuthentication(BaseModel):
    """Message d'authentification WebSocket"""
    type: WebSocketMessageType = WebSocketMessageType.AUTHENTICATION
    token: str


class WebSocketError(BaseModel):
    """Message d'erreur WebSocket"""
    type: WebSocketMessageType = WebSocketMessageType.ERROR
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = {}


class WebSocketSuccess(BaseModel):
    """Message de succès WebSocket"""
    type: WebSocketMessageType = WebSocketMessageType.SUCCESS
    message: str
    data: Optional[Dict[str, Any]] = {}


class WebSocketPing(BaseModel):
    """Message de ping"""
    type: WebSocketMessageType = WebSocketMessageType.PING
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebSocketPong(BaseModel):
    """Message de pong"""
    type: WebSocketMessageType = WebSocketMessageType.PONG
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Modèles pour les événements en temps réel

class TypingEvent(BaseModel):
    """Événement de frappe"""
    conversation_id: str
    user_id: str
    is_typing: bool


class ReadReceiptEvent(BaseModel):
    """Événement de lecture de message"""
    message_id: str
    conversation_id: str
    user_id: str


class OnlineStatusEvent(BaseModel):
    """Événement de changement de statut en ligne"""
    user_id: str
    status: OnlineStatus
    last_seen: Optional[datetime] = None


# Modèles pour les réponses d'API

class WebSocketConnectionInfo(BaseModel):
    """Informations de connexion WebSocket"""
    connection_id: str
    user_id: str
    connected_at: datetime
    last_ping: Optional[datetime] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class ActiveConnections(BaseModel):
    """Liste des connexions actives"""
    total_connections: int
    connections_by_user: Dict[str, int]
    connections: List[WebSocketConnectionInfo]


class MessageDeliveryStatus(BaseModel):
    """Statut de livraison d'un message"""
    message_id: str
    conversation_id: str
    sent_at: datetime
    delivered_to: List[str] = []
    read_by: List[str] = []
    failed_delivery: List[str] = []
