// Script d'initialisation MongoDB pour le messaging-service
print('🚀 Initialisation de la base de données MongoDB pour messaging-service...');

// Sélectionner la base de données
db = db.getSiblingDB('presencepro_messaging');

// Créer les collections avec validation
print('📊 Création des collections...');

// Collection des messages
db.createCollection('messages', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['message_id', 'conversation_id', 'sender_id', 'content', 'created_at'],
            properties: {
                message_id: {
                    bsonType: 'string',
                    description: 'ID unique du message'
                },
                conversation_id: {
                    bsonType: 'string',
                    description: 'ID de la conversation'
                },
                sender_id: {
                    bsonType: 'string',
                    description: 'ID de l\'expéditeur'
                },
                sender_name: {
                    bsonType: 'string',
                    description: 'Nom de l\'expéditeur'
                },
                sender_role: {
                    bsonType: 'string',
                    enum: ['student', 'parent', 'teacher', 'admin'],
                    description: 'Rôle de l\'expéditeur'
                },
                content: {
                    bsonType: 'string',
                    maxLength: 2000,
                    description: 'Contenu du message'
                },
                message_type: {
                    bsonType: 'string',
                    enum: ['text', 'image', 'file', 'system'],
                    description: 'Type de message'
                },
                status: {
                    bsonType: 'string',
                    enum: ['sent', 'delivered', 'read', 'failed'],
                    description: 'Statut du message'
                },
                is_read: {
                    bsonType: 'bool',
                    description: 'Message lu ou non'
                },
                created_at: {
                    bsonType: 'date',
                    description: 'Date de création'
                }
            }
        }
    }
});

// Collection des conversations
db.createCollection('conversations', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['conversation_id', 'participants', 'created_by', 'created_at'],
            properties: {
                conversation_id: {
                    bsonType: 'string',
                    description: 'ID unique de la conversation'
                },
                conversation_type: {
                    bsonType: 'string',
                    enum: ['direct', 'group', 'support'],
                    description: 'Type de conversation'
                },
                participants: {
                    bsonType: 'array',
                    items: {
                        bsonType: 'string'
                    },
                    description: 'Liste des participants'
                },
                created_by: {
                    bsonType: 'string',
                    description: 'Créateur de la conversation'
                },
                total_messages: {
                    bsonType: 'int',
                    minimum: 0,
                    description: 'Nombre total de messages'
                },
                is_active: {
                    bsonType: 'bool',
                    description: 'Conversation active ou non'
                },
                created_at: {
                    bsonType: 'date',
                    description: 'Date de création'
                }
            }
        }
    }
});

// Collection des statuts utilisateurs
db.createCollection('user_status', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['user_id', 'username', 'role'],
            properties: {
                user_id: {
                    bsonType: 'string',
                    description: 'ID unique de l\'utilisateur'
                },
                username: {
                    bsonType: 'string',
                    description: 'Nom d\'utilisateur'
                },
                display_name: {
                    bsonType: 'string',
                    description: 'Nom d\'affichage'
                },
                role: {
                    bsonType: 'string',
                    enum: ['student', 'parent', 'teacher', 'admin'],
                    description: 'Rôle de l\'utilisateur'
                },
                online_status: {
                    bsonType: 'string',
                    enum: ['online', 'offline', 'away', 'busy'],
                    description: 'Statut de connexion'
                },
                last_seen: {
                    bsonType: 'date',
                    description: 'Dernière connexion'
                }
            }
        }
    }
});

print('✅ Collections créées avec validation');

// Créer les index pour optimiser les performances
print('📈 Création des index...');

// Index pour les messages
db.messages.createIndex({ 'conversation_id': 1, 'created_at': -1 });
db.messages.createIndex({ 'sender_id': 1, 'created_at': -1 });
db.messages.createIndex({ 'recipient_id': 1, 'is_read': 1, 'created_at': -1 });
db.messages.createIndex({ 'message_id': 1 }, { unique: true });

// Index pour les conversations
db.conversations.createIndex({ 'participants': 1, 'updated_at': -1 });
db.conversations.createIndex({ 'created_by': 1, 'created_at': -1 });
db.conversations.createIndex({ 'conversation_id': 1 }, { unique: true });
db.conversations.createIndex({ 'conversation_type': 1, 'is_active': 1 });

// Index pour les statuts utilisateurs
db.user_status.createIndex({ 'user_id': 1 }, { unique: true });
db.user_status.createIndex({ 'online_status': 1, 'last_seen': -1 });
db.user_status.createIndex({ 'role': 1, 'online_status': 1 });

print('✅ Index créés');

// Insérer des données de test
print('🧪 Insertion des données de test...');

// Utilisateurs de test
db.user_status.insertMany([
    {
        user_id: 'student_001',
        username: 'alice.martin',
        display_name: 'Alice Martin',
        role: 'student',
        online_status: 'offline',
        total_messages_sent: 0,
        total_messages_received: 0,
        total_conversations: 0,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        user_id: 'parent_001',
        username: 'marie.martin',
        display_name: 'Marie Martin',
        role: 'parent',
        online_status: 'offline',
        total_messages_sent: 0,
        total_messages_received: 0,
        total_conversations: 0,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        user_id: 'teacher_001',
        username: 'prof.dupont',
        display_name: 'Prof. Dupont',
        role: 'teacher',
        online_status: 'offline',
        total_messages_sent: 0,
        total_messages_received: 0,
        total_conversations: 0,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        user_id: 'admin_001',
        username: 'admin',
        display_name: 'Administrateur',
        role: 'admin',
        online_status: 'offline',
        total_messages_sent: 0,
        total_messages_received: 0,
        total_conversations: 0,
        created_at: new Date(),
        updated_at: new Date()
    }
]);

print('✅ Utilisateurs de test créés');

// Conversation de test
const conversationId = 'conv_' + new Date().getTime();
db.conversations.insertOne({
    conversation_id: conversationId,
    conversation_type: 'direct',
    participants: ['student_001', 'parent_001'],
    participant_details: [
        { user_id: 'student_001', username: 'alice.martin', display_name: 'Alice Martin' },
        { user_id: 'parent_001', username: 'marie.martin', display_name: 'Marie Martin' }
    ],
    title: null,
    description: null,
    last_message_content: 'Bonjour maman !',
    last_message_at: new Date(),
    last_message_by: 'student_001',
    total_messages: 1,
    unread_count: { 'student_001': 0, 'parent_001': 1 },
    is_muted: { 'student_001': false, 'parent_001': false },
    is_archived: { 'student_001': false, 'parent_001': false },
    created_by: 'student_001',
    created_at: new Date(),
    updated_at: new Date(),
    is_active: true,
    is_deleted: false
});

print('✅ Conversation de test créée');

// Message de test
const messageId = 'msg_' + new Date().getTime();
db.messages.insertOne({
    message_id: messageId,
    conversation_id: conversationId,
    sender_id: 'student_001',
    sender_name: 'Alice Martin',
    sender_role: 'student',
    recipient_id: 'parent_001',
    content: 'Bonjour maman ! Comment ça va ?',
    message_type: 'text',
    status: 'sent',
    is_read: false,
    read_at: null,
    read_by: [],
    reply_to: null,
    thread_id: null,
    attachments: [],
    metadata: {},
    created_at: new Date(),
    updated_at: null,
    deleted_at: null,
    is_deleted: false,
    is_edited: false,
    edit_history: []
});

print('✅ Message de test créé');

print('🎉 Initialisation MongoDB terminée avec succès !');
print('📊 Collections créées: messages, conversations, user_status');
print('📈 Index optimisés pour les performances');
print('🧪 Données de test insérées');
print('🔗 Base de données prête pour le messaging-service');
