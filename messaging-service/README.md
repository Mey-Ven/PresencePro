# 🎭 Messaging Service - PresencePro

Service de messagerie en temps réel pour la communication entre parents et administrateurs dans l'écosystème PresencePro.

## 🚀 **Fonctionnalités**

### 💬 **Messagerie en temps réel**
- **WebSockets** pour la communication instantanée
- **Notifications de frappe** en temps réel
- **Accusés de réception** et de lecture
- **Statuts de connexion** des utilisateurs

### 🔐 **Sécurité et authentification**
- **Authentification JWT** intégrée avec auth-service
- **Permissions basées sur les rôles** (étudiant, parent, enseignant, admin)
- **Validation des autorisations** de messagerie
- **Communications sécurisées** via WebSocket

### 📊 **Gestion des conversations**
- **Conversations directes** entre utilisateurs
- **Conversations de groupe** (enseignants/admins)
- **Historique complet** des messages
- **Archivage** et mise en sourdine

## 🏗️ **Architecture**

### **Technologies**
- **FastAPI** : Framework web moderne
- **WebSockets** : Communication en temps réel
- **MongoDB** : Base de données NoSQL avec Motor/Beanie
- **JWT** : Authentification sécurisée
- **Docker** : Containerisation

### **Structure du projet**
```
messaging-service/
├── app/
│   ├── core/              # Configuration et base de données
│   ├── models/            # Modèles de données (Beanie)
│   ├── services/          # Logique métier
│   ├── routes/            # Endpoints REST API
│   ├── websockets/        # Gestion WebSocket
│   └── utils/             # Utilitaires
├── tests/                 # Tests unitaires
├── logs/                  # Fichiers de log
├── init_db.py            # Initialisation base de données
├── test_service.py       # Tests automatisés
└── docker-compose.yml    # Configuration Docker
```

## 📊 **Modèles de données**

### **Message**
```python
{
    "message_id": "uuid",
    "conversation_id": "uuid",
    "sender_id": "user_id",
    "sender_name": "string",
    "sender_role": "student|parent|teacher|admin",
    "recipient_id": "user_id",
    "content": "string",
    "message_type": "text|image|file|system",
    "status": "sent|delivered|read|failed",
    "is_read": "boolean",
    "read_at": "datetime",
    "reply_to": "message_id",
    "created_at": "datetime"
}
```

### **Conversation**
```python
{
    "conversation_id": "uuid",
    "conversation_type": "direct|group|support",
    "participants": ["user_id1", "user_id2"],
    "participant_details": [{"user_id", "username", "display_name"}],
    "title": "string",
    "last_message_content": "string",
    "last_message_at": "datetime",
    "total_messages": "integer",
    "unread_count": {"user_id": count},
    "is_muted": {"user_id": boolean},
    "is_archived": {"user_id": boolean}
}
```

### **UserStatus**
```python
{
    "user_id": "string",
    "username": "string",
    "display_name": "string",
    "role": "student|parent|teacher|admin",
    "online_status": "online|offline|away|busy",
    "last_seen": "datetime",
    "active_connections": ["connection_id"],
    "notification_settings": {}
}
```

## 🔗 **API REST**

### **Messages** (`/api/v1/messages`)
- `POST /send` - Envoyer un message
- `GET /history/{conversation_id}` - Historique des messages
- `POST /mark-read/{message_id}` - Marquer comme lu
- `GET /conversations` - Conversations de l'utilisateur
- `POST /conversations` - Créer une conversation
- `GET /stats` - Statistiques utilisateur
- `GET /online-users` - Utilisateurs en ligne

### **Santé et info**
- `GET /health` - Vérification de santé
- `GET /info` - Informations détaillées
- `GET /admin/stats` - Statistiques admin

## 🌐 **WebSocket API**

### **Connexion**
```javascript
// Connexion principale
const ws = new WebSocket('ws://localhost:8007/ws?token=JWT_TOKEN');

// Connexion à une conversation spécifique
const ws = new WebSocket('ws://localhost:8007/ws/conversation/conv_123?token=JWT_TOKEN');
```

### **Messages supportés**

#### **Authentification**
```json
{
    "type": "authentication",
    "token": "jwt_token"
}
```

#### **Envoyer un message**
```json
{
    "type": "message",
    "conversation_id": "conv_123",
    "content": "Bonjour !",
    "message_type": "text",
    "reply_to": "msg_456"
}
```

#### **Notification de frappe**
```json
{
    "type": "message_typing",
    "conversation_id": "conv_123"
}
```

#### **Marquer comme lu**
```json
{
    "type": "message_read",
    "message_id": "msg_123",
    "conversation_id": "conv_123"
}
```

#### **Ping/Pong**
```json
{
    "type": "ping",
    "timestamp": "2025-06-20T00:00:00Z"
}
```

## 🚀 **Installation et démarrage**

### **Prérequis**
- Python 3.9+
- MongoDB 4.4+
- Docker (optionnel)

### **Installation locale**
```bash
# Cloner le repository
git clone https://github.com/Mey-Ven/PresencePro.git
cd PresencePro/messaging-service

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Initialiser la base de données
python init_db.py

# Démarrer le service
uvicorn app.main:app --reload --port 8007
```

### **Avec Docker**
```bash
# Construire l'image
docker build -t presencepro/messaging-service .

# Démarrer avec docker-compose
docker-compose up -d
```

## 🧪 **Tests**

### **Tests automatisés**
```bash
# Exécuter les tests
python test_service.py

# Tests avec pytest
pytest tests/

# Tests de couverture
pytest --cov=app tests/
```

### **Tests manuels**
```bash
# Vérifier la santé
curl http://localhost:8007/health

# Informations du service
curl http://localhost:8007/info

# Test WebSocket avec wscat
wscat -c ws://localhost:8007/ws
```

## ⚙️ **Configuration**

### **Variables d'environnement**
```env
# Service
SERVICE_PORT=8007
DEBUG=True

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=presencepro_messaging

# Sécurité
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Services externes
AUTH_SERVICE_URL=http://localhost:8001
USER_SERVICE_URL=http://localhost:8002

# WebSocket
WEBSOCKET_PING_INTERVAL=20
MAX_CONNECTIONS_PER_USER=5

# Messages
MAX_MESSAGE_LENGTH=2000
MESSAGE_RETENTION_DAYS=365
```

## 🔗 **Intégration PresencePro**

### **Services connectés**
- **auth-service** (port 8001) : Authentification JWT
- **user-service** (port 8002) : Gestion des utilisateurs
- **attendance-service** (port 8005) : Notifications d'absence
- **justification-service** (port 8006) : Communication sur justifications

### **Permissions de messagerie**
- **Étudiants** → Parents, Enseignants, Admins
- **Parents** → Étudiants, Enseignants, Admins  
- **Enseignants** → Tous
- **Admins** → Tous

## 📈 **Monitoring**

### **Health checks**
- Statut de la base de données MongoDB
- Connexions WebSocket actives
- Utilisateurs en ligne
- Conversations actives

### **Métriques**
- Nombre total de messages
- Messages par minute
- Utilisateurs actifs
- Temps de réponse moyen

## 🔧 **Développement**

### **Structure du code**
- **models/** : Modèles Beanie pour MongoDB
- **services/** : Logique métier
- **routes/** : Endpoints FastAPI
- **websockets/** : Gestion temps réel
- **core/** : Configuration et base de données

### **Ajout de fonctionnalités**
1. Créer les modèles dans `models/`
2. Implémenter la logique dans `services/`
3. Ajouter les routes dans `routes/`
4. Mettre à jour les WebSockets si nécessaire
5. Ajouter les tests

## 📝 **TODO / Améliorations**

- [ ] **Attachments** : Support des fichiers joints
- [ ] **Recherche** : Recherche dans les messages
- [ ] **Chiffrement** : Chiffrement end-to-end
- [ ] **Notifications push** : Intégration service notifications
- [ ] **Modération** : Outils de modération avancés
- [ ] **Analytics** : Tableaux de bord et rapports
- [ ] **Mobile** : Optimisations pour mobile
- [ ] **Traduction** : Support multilingue

## 📞 **Support**

Pour toute question ou problème :
- **Documentation** : http://localhost:8007/docs
- **Health check** : http://localhost:8007/health
- **Logs** : `./logs/messaging.log`

---

**🎭 PresencePro Messaging Service** - Communication en temps réel pour l'éducation
