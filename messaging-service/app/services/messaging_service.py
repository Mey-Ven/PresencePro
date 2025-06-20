"""
Service principal de messagerie
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
import logging
from beanie import PydanticObjectId
from beanie.operators import In, And, Or

from app.models.message import (
    Message, Conversation, UserStatus, MessageCreate, MessageResponse,
    ConversationCreate, ConversationResponse, MessageHistory, ConversationList,
    MessageType, MessageStatus, ConversationType, OnlineStatus, UserRole
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class MessagingService:
    """Service de gestion de la messagerie"""
    
    def __init__(self):
        self.max_message_length = settings.max_message_length
        self.max_messages_per_conversation = settings.max_messages_per_conversation
        self.message_retention_days = settings.message_retention_days
    
    async def send_message(
        self, 
        message_data: MessageCreate, 
        sender_id: str,
        sender_name: str,
        sender_role: UserRole
    ) -> MessageResponse:
        """Envoyer un message"""
        try:
            # Déterminer la conversation
            conversation_id = message_data.conversation_id
            
            if not conversation_id and message_data.recipient_id:
                # Créer ou trouver une conversation directe
                conversation = await self._get_or_create_direct_conversation(
                    sender_id, message_data.recipient_id
                )
                conversation_id = conversation.conversation_id
            elif not conversation_id:
                raise ValueError("conversation_id ou recipient_id requis")
            
            # Vérifier que la conversation existe et que l'utilisateur y participe
            conversation = await Conversation.find_one(
                Conversation.conversation_id == conversation_id
            )
            
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} non trouvée")
            
            if sender_id not in conversation.participants:
                raise ValueError("Vous n'êtes pas participant de cette conversation")
            
            # Créer le message
            message = Message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                sender_name=sender_name,
                sender_role=sender_role,
                recipient_id=message_data.recipient_id,
                content=message_data.content,
                message_type=message_data.message_type,
                reply_to=message_data.reply_to,
                metadata=message_data.metadata or {}
            )
            
            # Sauvegarder le message
            await message.insert()
            
            # Mettre à jour la conversation
            await self._update_conversation_last_message(conversation, message)
            
            # Mettre à jour les compteurs non lus
            await self._update_unread_counts(conversation, message, sender_id)
            
            logger.info(f"Message envoyé: {message.message_id} dans conversation {conversation_id}")
            
            return MessageResponse(
                message_id=message.message_id,
                conversation_id=message.conversation_id,
                sender_id=message.sender_id,
                sender_name=message.sender_name,
                sender_role=message.sender_role,
                recipient_id=message.recipient_id,
                content=message.content,
                message_type=message.message_type,
                status=message.status,
                is_read=message.is_read,
                read_at=message.read_at,
                reply_to=message.reply_to,
                attachments=message.attachments,
                created_at=message.created_at,
                updated_at=message.updated_at,
                is_edited=message.is_edited
            )
            
        except Exception as e:
            logger.error(f"Erreur envoi message: {e}")
            raise
    
    async def get_message_history(
        self,
        conversation_id: str,
        user_id: str,
        page: int = 1,
        limit: int = 50,
        before_message_id: Optional[str] = None
    ) -> MessageHistory:
        """Récupérer l'historique des messages d'une conversation"""
        try:
            # Vérifier que l'utilisateur participe à la conversation
            conversation = await Conversation.find_one(
                Conversation.conversation_id == conversation_id
            )
            
            if not conversation or user_id not in conversation.participants:
                raise ValueError("Conversation non trouvée ou accès non autorisé")
            
            # Construire la requête
            query = {"conversation_id": conversation_id, "is_deleted": False}
            
            if before_message_id:
                # Récupérer les messages avant un message spécifique (pagination)
                before_message = await Message.find_one(
                    Message.message_id == before_message_id
                )
                if before_message:
                    query["created_at"] = {"$lt": before_message.created_at}
            
            # Récupérer les messages
            messages = await Message.find(
                query,
                sort=[("created_at", -1)],
                limit=limit
            ).to_list()
            
            # Compter le total
            total_count = await Message.find(
                {"conversation_id": conversation_id, "is_deleted": False}
            ).count()
            
            # Convertir en réponses
            message_responses = []
            for msg in reversed(messages):  # Inverser pour avoir l'ordre chronologique
                message_responses.append(MessageResponse(
                    message_id=msg.message_id,
                    conversation_id=msg.conversation_id,
                    sender_id=msg.sender_id,
                    sender_name=msg.sender_name,
                    sender_role=msg.sender_role,
                    recipient_id=msg.recipient_id,
                    content=msg.content,
                    message_type=msg.message_type,
                    status=msg.status,
                    is_read=msg.is_read,
                    read_at=msg.read_at,
                    reply_to=msg.reply_to,
                    attachments=msg.attachments,
                    created_at=msg.created_at,
                    updated_at=msg.updated_at,
                    is_edited=msg.is_edited
                ))
            
            has_more = len(messages) == limit and (page * limit) < total_count
            
            return MessageHistory(
                messages=message_responses,
                total_count=total_count,
                page=page,
                limit=limit,
                has_more=has_more
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}")
            raise
    
    async def mark_message_as_read(
        self,
        message_id: str,
        user_id: str
    ) -> bool:
        """Marquer un message comme lu"""
        try:
            message = await Message.find_one(Message.message_id == message_id)
            
            if not message:
                return False
            
            # Vérifier que l'utilisateur peut lire ce message
            conversation = await Conversation.find_one(
                Conversation.conversation_id == message.conversation_id
            )
            
            if not conversation or user_id not in conversation.participants:
                return False
            
            # Marquer comme lu si ce n'est pas l'expéditeur
            if message.sender_id != user_id and user_id not in message.read_by:
                message.read_by.append(user_id)
                if not message.is_read:
                    message.is_read = True
                    message.read_at = datetime.now(timezone.utc)
                
                await message.save()
                
                # Mettre à jour le compteur non lu de la conversation
                if user_id in conversation.unread_count:
                    conversation.unread_count[user_id] = max(0, conversation.unread_count[user_id] - 1)
                    await conversation.save()
                
                logger.info(f"Message {message_id} marqué comme lu par {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur marquage message lu: {e}")
            return False
    
    async def get_user_conversations(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ) -> ConversationList:
        """Récupérer les conversations d'un utilisateur"""
        try:
            # Récupérer les conversations où l'utilisateur participe
            conversations = await Conversation.find(
                And(
                    In(user_id, Conversation.participants),
                    Conversation.is_active == True,
                    Or(
                        Conversation.is_archived.get(user_id, False) == False,
                        ~Conversation.is_archived.exists()
                    )
                ),
                sort=[("updated_at", -1)],
                skip=(page - 1) * limit,
                limit=limit
            ).to_list()
            
            # Compter le total
            total_count = await Conversation.find(
                And(
                    In(user_id, Conversation.participants),
                    Conversation.is_active == True
                )
            ).count()
            
            # Convertir en réponses
            conversation_responses = []
            for conv in conversations:
                unread_count = conv.unread_count.get(user_id, 0)
                is_muted = conv.is_muted.get(user_id, False)
                is_archived = conv.is_archived.get(user_id, False)
                
                conversation_responses.append(ConversationResponse(
                    conversation_id=conv.conversation_id,
                    conversation_type=conv.conversation_type,
                    participants=conv.participants,
                    participant_details=conv.participant_details,
                    title=conv.title,
                    description=conv.description,
                    last_message_content=conv.last_message_content,
                    last_message_at=conv.last_message_at,
                    last_message_by=conv.last_message_by,
                    total_messages=conv.total_messages,
                    unread_count=unread_count,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    is_muted=is_muted,
                    is_archived=is_archived
                ))
            
            return ConversationList(
                conversations=conversation_responses,
                total_count=total_count,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération conversations: {e}")
            raise
    
    async def create_conversation(
        self,
        conversation_data: ConversationCreate,
        creator_id: str,
        creator_name: str
    ) -> ConversationResponse:
        """Créer une nouvelle conversation"""
        try:
            # Valider les participants
            if creator_id not in conversation_data.participant_ids:
                conversation_data.participant_ids.append(creator_id)
            
            # Pour les conversations directes, vérifier qu'il n'y a que 2 participants
            if conversation_data.conversation_type == ConversationType.DIRECT:
                if len(conversation_data.participant_ids) != 2:
                    raise ValueError("Une conversation directe doit avoir exactement 2 participants")
                
                # Vérifier si une conversation directe existe déjà
                existing = await Conversation.find_one(
                    And(
                        Conversation.conversation_type == ConversationType.DIRECT,
                        Conversation.participants == conversation_data.participant_ids,
                        Conversation.is_active == True
                    )
                )
                
                if existing:
                    # Retourner la conversation existante
                    unread_count = existing.unread_count.get(creator_id, 0)
                    return ConversationResponse(
                        conversation_id=existing.conversation_id,
                        conversation_type=existing.conversation_type,
                        participants=existing.participants,
                        participant_details=existing.participant_details,
                        title=existing.title,
                        description=existing.description,
                        last_message_content=existing.last_message_content,
                        last_message_at=existing.last_message_at,
                        last_message_by=existing.last_message_by,
                        total_messages=existing.total_messages,
                        unread_count=unread_count,
                        created_at=existing.created_at,
                        updated_at=existing.updated_at,
                        is_muted=existing.is_muted.get(creator_id, False),
                        is_archived=existing.is_archived.get(creator_id, False)
                    )
            
            # Créer la conversation
            conversation = Conversation(
                conversation_type=conversation_data.conversation_type,
                participants=conversation_data.participant_ids,
                title=conversation_data.title,
                description=conversation_data.description,
                created_by=creator_id,
                unread_count={participant: 0 for participant in conversation_data.participant_ids},
                is_muted={participant: False for participant in conversation_data.participant_ids},
                is_archived={participant: False for participant in conversation_data.participant_ids}
            )
            
            # TODO: Récupérer les détails des participants depuis user-service
            conversation.participant_details = [
                {"user_id": pid, "username": f"user_{pid}", "display_name": f"User {pid}"}
                for pid in conversation_data.participant_ids
            ]
            
            await conversation.insert()
            
            logger.info(f"Conversation créée: {conversation.conversation_id} par {creator_id}")
            
            return ConversationResponse(
                conversation_id=conversation.conversation_id,
                conversation_type=conversation.conversation_type,
                participants=conversation.participants,
                participant_details=conversation.participant_details,
                title=conversation.title,
                description=conversation.description,
                last_message_content=conversation.last_message_content,
                last_message_at=conversation.last_message_at,
                last_message_by=conversation.last_message_by,
                total_messages=conversation.total_messages,
                unread_count=0,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                is_muted=False,
                is_archived=False
            )
            
        except Exception as e:
            logger.error(f"Erreur création conversation: {e}")
            raise
    
    async def _get_or_create_direct_conversation(
        self,
        user1_id: str,
        user2_id: str
    ) -> Conversation:
        """Récupérer ou créer une conversation directe entre deux utilisateurs"""
        participants = sorted([user1_id, user2_id])
        
        # Chercher une conversation existante
        existing = await Conversation.find_one(
            And(
                Conversation.conversation_type == ConversationType.DIRECT,
                Conversation.participants == participants,
                Conversation.is_active == True
            )
        )
        
        if existing:
            return existing
        
        # Créer une nouvelle conversation
        conversation = Conversation(
            conversation_type=ConversationType.DIRECT,
            participants=participants,
            created_by=user1_id,
            unread_count={user1_id: 0, user2_id: 0},
            is_muted={user1_id: False, user2_id: False},
            is_archived={user1_id: False, user2_id: False}
        )
        
        await conversation.insert()
        return conversation
    
    async def _update_conversation_last_message(
        self,
        conversation: Conversation,
        message: Message
    ):
        """Mettre à jour le dernier message de la conversation"""
        conversation.last_message_id = message.message_id
        conversation.last_message_content = message.content[:100] + "..." if len(message.content) > 100 else message.content
        conversation.last_message_at = message.created_at
        conversation.last_message_by = message.sender_id
        conversation.total_messages += 1
        conversation.updated_at = datetime.now(timezone.utc)
        
        await conversation.save()
    
    async def _update_unread_counts(
        self,
        conversation: Conversation,
        message: Message,
        sender_id: str
    ):
        """Mettre à jour les compteurs de messages non lus"""
        for participant in conversation.participants:
            if participant != sender_id:
                if participant not in conversation.unread_count:
                    conversation.unread_count[participant] = 0
                conversation.unread_count[participant] += 1
        
        await conversation.save()
