"""
Modèles de données pour la messagerie avec Beanie (MongoDB ODM)
"""
from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


class MessageType(str, Enum):
    """Types de messages"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    """Statuts de message"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class ConversationType(str, Enum):
    """Types de conversation"""
    DIRECT = "direct"  # Conversation directe entre 2 personnes
    GROUP = "group"    # Conversation de groupe
    SUPPORT = "support"  # Conversation de support


class UserRole(str, Enum):
    """Rôles d'utilisateur"""
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"


class OnlineStatus(str, Enum):
    """Statuts de connexion"""
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BUSY = "busy"


class Message(Document):
    """Modèle pour les messages"""
    
    # Identifiants
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str

    # Expéditeur et destinataire
    sender_id: str
    sender_name: str
    sender_role: UserRole
    recipient_id: Optional[str] = None  # Pour messages directs
    
    # Contenu du message
    message_type: MessageType = MessageType.TEXT
    content: str
    metadata: Optional[Dict[str, Any]] = {}  # Métadonnées additionnelles
    
    # Statut et lecture
    status: MessageStatus = MessageStatus.SENT
    is_read: bool = False
    read_at: Optional[datetime] = None
    read_by: List[str] = []  # Liste des IDs qui ont lu le message
    
    # Réponse et thread
    reply_to: Optional[str] = None  # ID du message auquel on répond
    thread_id: Optional[str] = None  # ID du thread de conversation
    
    # Fichiers attachés (pour futurs développements)
    attachments: List[Dict[str, Any]] = []
    
    # Dates
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    # Modération
    is_deleted: bool = False
    is_edited: bool = False
    edit_history: List[Dict[str, Any]] = []
    
    class Settings:
        name = "messages"


class Conversation(Document):
    """Modèle pour les conversations"""
    
    # Identifiants
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Type et participants
    conversation_type: ConversationType = ConversationType.DIRECT
    participants: List[str]  # Liste des IDs des participants
    participant_details: List[Dict[str, Any]] = []  # Détails des participants
    
    # Métadonnées de la conversation
    title: Optional[str] = None  # Titre pour les conversations de groupe
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Dernier message
    last_message_id: Optional[str] = None
    last_message_content: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_by: Optional[str] = None
    
    # Compteurs
    total_messages: int = 0
    unread_count: Dict[str, int] = {}  # Nombre de messages non lus par participant
    
    # Paramètres
    is_muted: Dict[str, bool] = {}  # Participants qui ont mis en sourdine
    is_archived: Dict[str, bool] = {}  # Participants qui ont archivé
    
    # Dates
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    
    # Statut
    is_active: bool = True
    is_deleted: bool = False
    
    class Settings:
        name = "conversations"


class UserStatus(Document):
    """Modèle pour le statut des utilisateurs"""
    
    # Identifiant
    user_id: str
    
    # Informations utilisateur
    username: str
    display_name: str
    role: UserRole
    avatar_url: Optional[str] = None
    
    # Statut de connexion
    online_status: OnlineStatus = OnlineStatus.OFFLINE
    last_seen: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    # Connexions WebSocket actives
    active_connections: List[str] = []  # Liste des IDs de connexion
    device_info: List[Dict[str, Any]] = []  # Informations des appareils connectés
    
    # Préférences
    notification_settings: Dict[str, bool] = {
        "email_notifications": True,
        "push_notifications": True,
        "sound_notifications": True,
        "desktop_notifications": True
    }
    
    # Statistiques
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_conversations: int = 0
    
    # Dates
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "user_status"


# Modèles Pydantic pour les API

class MessageCreate(BaseModel):
    """Modèle pour créer un message"""
    conversation_id: Optional[str] = None
    recipient_id: Optional[str] = None  # Si pas de conversation_id, créer une nouvelle conversation
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: MessageType = MessageType.TEXT
    reply_to: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class MessageResponse(BaseModel):
    """Modèle de réponse pour un message"""
    message_id: str
    conversation_id: str
    sender_id: str
    sender_name: str
    sender_role: UserRole
    recipient_id: Optional[str] = None
    content: str
    message_type: MessageType
    status: MessageStatus
    is_read: bool
    read_at: Optional[datetime] = None
    reply_to: Optional[str] = None
    attachments: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_edited: bool = False


class ConversationCreate(BaseModel):
    """Modèle pour créer une conversation"""
    participant_ids: List[str] = Field(..., min_items=1)
    conversation_type: ConversationType = ConversationType.DIRECT
    title: Optional[str] = None
    description: Optional[str] = None


class ConversationResponse(BaseModel):
    """Modèle de réponse pour une conversation"""
    conversation_id: str
    conversation_type: ConversationType
    participants: List[str]
    participant_details: List[Dict[str, Any]]
    title: Optional[str] = None
    description: Optional[str] = None
    last_message_content: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_by: Optional[str] = None
    total_messages: int
    unread_count: int  # Pour l'utilisateur actuel
    created_at: datetime
    updated_at: datetime
    is_muted: bool = False
    is_archived: bool = False


class UserStatusResponse(BaseModel):
    """Modèle de réponse pour le statut utilisateur"""
    user_id: str
    username: str
    display_name: str
    role: UserRole
    online_status: OnlineStatus
    last_seen: Optional[datetime] = None
    avatar_url: Optional[str] = None


class MessageHistory(BaseModel):
    """Modèle pour l'historique des messages"""
    messages: List[MessageResponse]
    total_count: int
    page: int
    limit: int
    has_more: bool


class ConversationList(BaseModel):
    """Modèle pour la liste des conversations"""
    conversations: List[ConversationResponse]
    total_count: int
    page: int
    limit: int
