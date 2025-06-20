# PresencePro Config Service

## 📋 Description

Le **Config Service** est un microservice centralisé pour la gestion des configurations de tous les services de l'écosystème PresencePro. Il fournit un point unique pour stocker, récupérer, valider et gérer les configurations avec chiffrement des données sensibles.

## ✨ Fonctionnalités

### 🔧 **Gestion des configurations**
- Stockage centralisé des configurations pour tous les microservices
- Support de multiples backends : Fichiers, Consul, Redis
- Chiffrement automatique des données sensibles (mots de passe, clés secrètes)
- Versioning et métadonnées des configurations

### 🛡️ **Sécurité**
- Authentification par clés API (maître et par service)
- Chiffrement AES des données sensibles
- Validation et masquage des données sensibles dans les logs
- Contrôle d'accès granulaire (lecture vs écriture)

### ✅ **Validation**
- Validation automatique des configurations selon des schémas
- Vérification des types, contraintes et formats
- Détection des conflits de ports et URLs malformées
- Avertissements pour les configurations faibles

### 📊 **Monitoring et observabilité**
- Métriques Prometheus intégrées
- Logging structuré avec correlation
- Health checks et diagnostics
- Audit trail des modifications

### 🔄 **Sauvegarde et comparaison**
- Sauvegarde automatique avant modifications
- Comparaison de configurations (diff)
- Templates de configuration par service
- Restauration depuis sauvegardes

## 🏗️ Architecture

### **Backends de stockage supportés**
- **File** : Stockage dans des fichiers JSON (par défaut)
- **Consul** : Stockage distribué avec Consul KV
- **Redis** : Stockage en mémoire avec persistance

### **Services supportés**
- auth-service (8001)
- user-service (8002)
- course-service (8003)
- face-recognition-service (8004)
- attendance-service (8005)
- justification-service (8006)
- messaging-service (8007)
- notification-service (8008)
- statistics-service (8009)
- gateway-service (8000)
- admin-panel-service (3000)
- config-service (8010)

## 🚀 Installation et démarrage

### **Prérequis**
- Python 3.11+
- Redis (optionnel)
- Consul (optionnel)

### **Installation**
```bash
# Cloner le repository
git clone https://github.com/Mey-Ven/PresencePro.git
cd PresencePro/config-service

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres
```

### **Démarrage**
```bash
# Mode développement
python run.py

# Ou avec uvicorn directement
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload

# Mode production
uvicorn app.main:app --host 0.0.0.0 --port 8010 --workers 4
```

### **Avec Docker**
```bash
# Build et démarrage
docker-compose up --build

# En arrière-plan
docker-compose up -d
```

## 🔧 Configuration

### **Variables d'environnement**
```env
# Configuration du service
CONFIG_HOST=0.0.0.0
CONFIG_PORT=8010
ENVIRONMENT=development

# Stockage
CONFIG_STORAGE_TYPE=file  # file, consul, redis
CONFIG_BASE_PATH=./configs
CONFIG_ENCRYPTION_KEY=your-32-char-encryption-key

# Sécurité
MASTER_API_KEY=config-master-key
SERVICE_API_KEYS=auth-service:auth-key,user-service:user-key

# Consul (optionnel)
CONSUL_HOST=localhost
CONSUL_PORT=8500

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/1
```

### **Clés API**
- **Clé maître** : Accès complet (lecture/écriture)
- **Clés de service** : Accès en lecture uniquement
- Header requis : `X-Config-API-Key`

## 📚 API Documentation

### **Endpoints principaux**

#### **GET /health**
Vérifier la santé du service
```bash
curl http://localhost:8010/health
```

#### **GET /services**
Lister tous les services
```bash
curl -H "X-Config-API-Key: auth-key" \
     http://localhost:8010/services
```

#### **GET /config/{service}**
Récupérer la configuration d'un service
```bash
curl -H "X-Config-API-Key: auth-key" \
     http://localhost:8010/config/auth-service
```

#### **PUT /config/{service}**
Sauvegarder une configuration (clé maître requise)
```bash
curl -X PUT \
     -H "X-Config-API-Key: config-master-key" \
     -H "Content-Type: application/json" \
     -d '{"config_data": {"host": "0.0.0.0", "port": 8001}}' \
     http://localhost:8010/config/auth-service
```

#### **POST /validate**
Valider une configuration
```bash
curl -X POST \
     -H "X-Config-API-Key: auth-key" \
     -H "Content-Type: application/json" \
     -d '{"service_name": "auth-service", "config_data": {"port": 8001}}' \
     http://localhost:8010/validate
```

#### **GET /template/{service}**
Obtenir un template de configuration
```bash
curl -H "X-Config-API-Key: auth-key" \
     http://localhost:8010/template/auth-service
```

#### **POST /backup/{service}**
Créer une sauvegarde (clé maître requise)
```bash
curl -X POST \
     -H "X-Config-API-Key: config-master-key" \
     http://localhost:8010/backup/auth-service
```

#### **POST /diff**
Comparer deux configurations
```bash
curl -X POST \
     -H "X-Config-API-Key: auth-key" \
     -H "Content-Type: application/json" \
     -d '{"service_name": "auth-service", "config_a": {...}, "config_b": {...}}' \
     http://localhost:8010/diff
```

### **Documentation interactive**
- Swagger UI : http://localhost:8010/docs
- ReDoc : http://localhost:8010/redoc

## 🔐 Sécurité

### **Chiffrement des données sensibles**
Les champs suivants sont automatiquement chiffrés :
- `password`, `secret`, `key`, `token`, `api_key`
- `database_url`, `smtp_password`, `jwt_secret_key`

### **Validation de sécurité**
- Vérification de la longueur des clés secrètes (min 16 caractères)
- Détection des mots de passe faibles
- Validation de la complexité des secrets
- Avertissements pour les configurations par défaut

### **Contrôle d'accès**
- **Lecture** : Clés de service ou clé maître
- **Écriture/Suppression** : Clé maître uniquement
- **Validation/Templates** : Clés de service ou clé maître

## 📊 Monitoring

### **Métriques Prometheus**
- `config_requests_total` - Nombre total de requêtes
- `config_request_duration_seconds` - Durée des requêtes

### **Health checks**
- `GET /health` - Santé du service
- `GET /metrics` - Métriques Prometheus

### **Logging**
Logs structurés en JSON avec :
- Correlation IDs
- Informations de sécurité (service demandeur)
- Audit trail des modifications
- Masquage des données sensibles

## 🧪 Tests

### **Exécuter les tests**
```bash
# Tests unitaires
pytest

# Avec coverage
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_config_service.py -v
```

### **Types de tests**
- Tests d'authentification et autorisation
- Tests de validation de configuration
- Tests de chiffrement/déchiffrement
- Tests des backends de stockage
- Tests de l'API REST

## 🔄 Intégration avec les autres services

### **Utilisation depuis un service**
```python
import httpx

# Configuration du client
config_client = httpx.AsyncClient(
    base_url="http://localhost:8010",
    headers={"X-Config-API-Key": "auth-key"}
)

# Récupérer la configuration
response = await config_client.get("/config/auth-service")
config = response.json()["config_data"]

# Utiliser la configuration
database_url = config["database_url"]
jwt_secret = config["jwt_secret_key"]
```

### **Variables d'environnement pour les services**
```env
# Dans chaque service
CONFIG_SERVICE_URL=http://localhost:8010
CONFIG_API_KEY=service-specific-key
```

## 🐛 Dépannage

### **Problèmes courants**
1. **Clé API invalide (403)** : Vérifier la clé dans les headers
2. **Service non trouvé (404)** : Vérifier le nom du service
3. **Validation échouée (400)** : Vérifier le format de la configuration
4. **Erreur de chiffrement (500)** : Vérifier la clé de chiffrement

### **Logs de débogage**
```bash
# Activer les logs détaillés
LOG_LEVEL=DEBUG python run.py

# Logs en temps réel avec Docker
docker-compose logs -f config-service
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Ajouter des tests pour les nouvelles fonctionnalités
4. S'assurer que tous les tests passent
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

---

**PresencePro Config Service** - Gestion centralisée et sécurisée des configurations 🔧
