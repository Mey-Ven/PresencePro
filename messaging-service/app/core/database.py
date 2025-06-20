"""
Configuration de la base de données MongoDB pour le service de messagerie
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
from .config import settings

logger = logging.getLogger(__name__)

# Client MongoDB global
mongodb_client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Connexion à MongoDB"""
    global mongodb_client, database
    
    try:
        logger.info(f"🔗 Connexion à MongoDB: {settings.mongodb_url}")
        
        # Créer le client MongoDB
        mongodb_client = AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Sélectionner la base de données
        database = mongodb_client[settings.mongodb_database]
        
        # Tester la connexion
        await mongodb_client.admin.command('ping')
        logger.info("✅ Connexion MongoDB établie")
        
        # Initialiser Beanie avec les modèles
        from app.models.message import Message, Conversation, UserStatus
        
        await init_beanie(
            database=database,
            document_models=[Message, Conversation, UserStatus]
        )
        
        logger.info("✅ Beanie initialisé avec les modèles")
        
        # Créer les index
        await create_indexes()
        
        return database
        
    except Exception as e:
        logger.error(f"❌ Erreur connexion MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Fermer la connexion MongoDB"""
    global mongodb_client
    
    if mongodb_client:
        logger.info("🔌 Fermeture connexion MongoDB")
        mongodb_client.close()


async def create_indexes():
    """Créer les index MongoDB pour optimiser les performances"""
    try:
        logger.info("📊 Création des index MongoDB...")
        
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


def get_database():
    """Obtenir la base de données MongoDB"""
    return database


async def ping_database():
    """Tester la connexion à la base de données"""
    try:
        if mongodb_client:
            await mongodb_client.admin.command('ping')
            return True
        return False
    except Exception:
        return False


async def get_database_stats():
    """Obtenir les statistiques de la base de données"""
    try:
        if not database:
            return {}
        
        # Statistiques générales
        stats = await database.command("dbStats")
        
        # Compter les documents dans chaque collection
        messages_count = await database[settings.mongodb_collection_messages].count_documents({})
        conversations_count = await database[settings.mongodb_collection_conversations].count_documents({})
        users_count = await database[settings.mongodb_collection_users].count_documents({})
        
        return {
            "database_name": stats.get("db"),
            "collections": stats.get("collections", 0),
            "data_size": stats.get("dataSize", 0),
            "storage_size": stats.get("storageSize", 0),
            "index_size": stats.get("indexSize", 0),
            "messages_count": messages_count,
            "conversations_count": conversations_count,
            "users_count": users_count
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération statistiques DB: {e}")
        return {}
