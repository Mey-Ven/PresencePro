#!/usr/bin/env python3
"""
Script d'initialisation de la base de données MongoDB pour le messaging-service
"""
import asyncio
import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.models.message import Message, Conversation, UserStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialiser la base de données MongoDB"""
    try:
        logger.info("🔗 Connexion à MongoDB...")
        
        # Créer le client MongoDB
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.mongodb_database]
        
        # Tester la connexion
        await client.admin.command('ping')
        logger.info("✅ Connexion MongoDB établie")
        
        # Initialiser Beanie
        logger.info("📊 Initialisation de Beanie...")
        await init_beanie(
            database=database,
            document_models=[Message, Conversation, UserStatus]
        )
        logger.info("✅ Beanie initialisé")
        
        # Créer les index
        logger.info("📈 Création des index...")
        await create_indexes(database)
        logger.info("✅ Index créés")
        
        # Insérer des données de test
        logger.info("🧪 Insertion des données de test...")
        await insert_test_data()
        logger.info("✅ Données de test insérées")
        
        # Fermer la connexion
        client.close()
        logger.info("✅ Initialisation terminée avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        raise


async def create_indexes(database):
    """Créer les index MongoDB"""
    try:
        # Index pour les messages
        await database[settings.mongodb_collection_messages].create_index([
            ("conversation_id", 1),
            ("created_at", -1)
        ])
        
        await database[settings.mongodb_collection_messages].create_index([
            ("sender_id", 1),
            ("created_at", -1)
        ])
        
        await database[settings.mongodb_collection_messages].create_index([
            ("recipient_id", 1),
            ("is_read", 1),
            ("created_at", -1)
        ])
        
        # Index pour les conversations
        await database[settings.mongodb_collection_conversations].create_index([
            ("participants", 1),
            ("updated_at", -1)
        ])
        
        await database[settings.mongodb_collection_conversations].create_index([
            ("created_by", 1),
            ("created_at", -1)
        ])
        
        # Index pour les statuts utilisateurs
        await database[settings.mongodb_collection_users].create_index([
            ("user_id", 1)
        ], unique=True)
        
        logger.info("✅ Index MongoDB créés")
        
    except Exception as e:
        logger.error(f"❌ Erreur création index: {e}")
        raise


async def insert_test_data():
    """Insérer des données de test"""
    try:
        # Créer des utilisateurs de test
        test_users = [
            UserStatus(
                user_id="student_001",
                username="alice.martin",
                display_name="Alice Martin",
                role="student",
                online_status="offline"
            ),
            UserStatus(
                user_id="parent_001",
                username="marie.martin",
                display_name="Marie Martin",
                role="parent",
                online_status="offline"
            ),
            UserStatus(
                user_id="teacher_001",
                username="prof.dupont",
                display_name="Prof. Dupont",
                role="teacher",
                online_status="offline"
            ),
            UserStatus(
                user_id="admin_001",
                username="admin",
                display_name="Administrateur",
                role="admin",
                online_status="offline"
            )
        ]
        
        # Insérer les utilisateurs
        for user in test_users:
            existing = await UserStatus.find_one(UserStatus.user_id == user.user_id)
            if not existing:
                await user.insert()
                logger.info(f"Utilisateur créé: {user.display_name}")
        
        # Créer une conversation de test
        test_conversation = Conversation(
            conversation_type="direct",
            participants=["student_001", "parent_001"],
            participant_details=[
                {"user_id": "student_001", "username": "alice.martin", "display_name": "Alice Martin"},
                {"user_id": "parent_001", "username": "marie.martin", "display_name": "Marie Martin"}
            ],
            created_by="student_001",
            unread_count={"student_001": 0, "parent_001": 0},
            is_muted={"student_001": False, "parent_001": False},
            is_archived={"student_001": False, "parent_001": False}
        )
        
        # Vérifier si la conversation existe déjà
        existing_conv = await Conversation.find_one(
            Conversation.participants == ["student_001", "parent_001"]
        )
        
        if not existing_conv:
            await test_conversation.insert()
            logger.info(f"Conversation créée: {test_conversation.conversation_id}")
            
            # Créer quelques messages de test
            test_messages = [
                Message(
                    conversation_id=test_conversation.conversation_id,
                    sender_id="student_001",
                    sender_name="Alice Martin",
                    sender_role="student",
                    recipient_id="parent_001",
                    content="Bonjour maman, j'ai une question sur mes devoirs.",
                    message_type="text"
                ),
                Message(
                    conversation_id=test_conversation.conversation_id,
                    sender_id="parent_001",
                    sender_name="Marie Martin",
                    sender_role="parent",
                    recipient_id="student_001",
                    content="Bonjour Alice ! Bien sûr, dis-moi tout.",
                    message_type="text"
                ),
                Message(
                    conversation_id=test_conversation.conversation_id,
                    sender_id="student_001",
                    sender_name="Alice Martin",
                    sender_role="student",
                    recipient_id="parent_001",
                    content="Est-ce que tu peux m'aider avec les mathématiques ce soir ?",
                    message_type="text"
                )
            ]
            
            for message in test_messages:
                await message.insert()
                logger.info(f"Message créé: {message.content[:30]}...")
            
            # Mettre à jour la conversation avec le dernier message
            last_message = test_messages[-1]
            test_conversation.last_message_id = last_message.message_id
            test_conversation.last_message_content = last_message.content
            test_conversation.last_message_at = last_message.created_at
            test_conversation.last_message_by = last_message.sender_id
            test_conversation.total_messages = len(test_messages)
            test_conversation.updated_at = datetime.now(timezone.utc)
            
            await test_conversation.save()
        
        logger.info("✅ Données de test insérées")
        
    except Exception as e:
        logger.error(f"❌ Erreur insertion données test: {e}")
        raise


async def cleanup_database():
    """Nettoyer la base de données (pour les tests)"""
    try:
        logger.info("🧹 Nettoyage de la base de données...")
        
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.mongodb_database]
        
        # Supprimer toutes les collections
        await database[settings.mongodb_collection_messages].delete_many({})
        await database[settings.mongodb_collection_conversations].delete_many({})
        await database[settings.mongodb_collection_users].delete_many({})
        
        client.close()
        logger.info("✅ Base de données nettoyée")
        
    except Exception as e:
        logger.error(f"❌ Erreur nettoyage: {e}")
        raise


async def show_database_stats():
    """Afficher les statistiques de la base de données"""
    try:
        logger.info("📊 Statistiques de la base de données:")
        
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.mongodb_database]
        
        # Compter les documents
        messages_count = await database[settings.mongodb_collection_messages].count_documents({})
        conversations_count = await database[settings.mongodb_collection_conversations].count_documents({})
        users_count = await database[settings.mongodb_collection_users].count_documents({})
        
        print(f"📧 Messages: {messages_count}")
        print(f"💬 Conversations: {conversations_count}")
        print(f"👥 Utilisateurs: {users_count}")
        
        client.close()
        
    except Exception as e:
        logger.error(f"❌ Erreur statistiques: {e}")
        raise


async def main():
    """Fonction principale"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "cleanup":
            await cleanup_database()
        elif command == "stats":
            await show_database_stats()
        elif command == "init":
            await init_database()
        else:
            print("Commandes disponibles: init, cleanup, stats")
            sys.exit(1)
    else:
        # Initialisation par défaut
        await init_database()


if __name__ == "__main__":
    asyncio.run(main())
