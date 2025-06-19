# PresencePro Auth Service

Microservice d'authentification et d'autorisation pour le système PresencePro.

## 🚀 Fonctionnalités

- **Authentification JWT** : Login sécurisé avec tokens d'accès et de rafraîchissement
- **Gestion des rôles** : Support pour 4 types d'utilisateurs (Admin, Enseignant, Étudiant, Parent)
- **Génération automatique de comptes** : Création en masse d'utilisateurs avec identifiants uniques
- **Middleware de sécurité** : Vérification des permissions par rôle
- **Base de données PostgreSQL** : Stockage sécurisé des utilisateurs et tokens

## 📋 Prérequis

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optionnel)

## 🛠️ Installation

### Installation locale

1. **Cloner et naviguer vers le projet**
```bash
cd auth-service
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. **Configurer la base de données**
```bash
# Créer la base de données PostgreSQL
createdb presencepro_auth

# Initialiser Alembic et créer les migrations
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

6. **Lancer le service**
```bash
uvicorn app.main:app --reload --port 8001
```

### Installation avec Docker

```bash
# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f auth-service
```

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://...` |
| `SECRET_KEY` | Clé secrète pour JWT | À changer en production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie token d'accès | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Durée de vie token de rafraîchissement | 7 |

## 📚 API Endpoints

### Authentification

| Méthode | Endpoint | Description | Rôle requis |
|---------|----------|-------------|-------------|
| `POST` | `/api/v1/auth/login` | Connexion utilisateur | Aucun |
| `POST` | `/api/v1/auth/refresh-token` | Rafraîchir le token | Aucun |
| `POST` | `/api/v1/auth/logout` | Déconnexion | Authentifié |

### Gestion des utilisateurs

| Méthode | Endpoint | Description | Rôle requis |
|---------|----------|-------------|-------------|
| `POST` | `/api/v1/auth/register` | Créer un utilisateur | Admin |
| `POST` | `/api/v1/auth/register/bulk` | Créer plusieurs utilisateurs | Admin |

### Rôles et permissions

| Méthode | Endpoint | Description | Rôle requis |
|---------|----------|-------------|-------------|
| `GET` | `/api/v1/auth/roles/me` | Obtenir mon rôle | Authentifié |
| `POST` | `/api/v1/auth/roles/check` | Vérifier les permissions | Authentifié |

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=app

# Tests spécifiques
pytest tests/test_auth.py -v
```

## 📖 Exemples d'utilisation

### 1. Connexion

```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "password": "admin123"
  }'
```

### 2. Créer un utilisateur (Admin requis)

```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "username": "teacher_john",
    "password": "secure123",
    "role": "enseignant",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@school.com"
  }'
```

### 3. Génération en masse d'étudiants

```bash
curl -X POST "http://localhost:8001/api/v1/auth/register/bulk" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "role": "etudiant",
    "count": 25,
    "prefix": "promo2024"
  }'
```

## 🔒 Sécurité

- **Hachage des mots de passe** : bcrypt avec salt
- **JWT sécurisé** : Tokens signés avec clé secrète
- **Tokens de rafraîchissement** : Stockés en base avec expiration
- **Validation des rôles** : Middleware de vérification des permissions
- **CORS configuré** : Protection contre les requêtes cross-origin

## 🏗️ Architecture

```
auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py          # Point d'entrée FastAPI
│   ├── config.py        # Configuration
│   ├── database.py      # Connexion DB
│   ├── models.py        # Modèles SQLAlchemy
│   ├── schemas.py       # Schémas Pydantic
│   ├── auth.py          # Logique d'authentification
│   ├── crud.py          # Opérations CRUD
│   └── routes.py        # Endpoints API
├── alembic/             # Migrations DB
├── tests/               # Tests unitaires
├── requirements.txt     # Dépendances Python
├── docker-compose.yml   # Configuration Docker
└── README.md
```

## 🚀 Déploiement

### Production

1. **Configurer les variables d'environnement de production**
2. **Utiliser une base de données PostgreSQL dédiée**
3. **Changer la clé secrète JWT**
4. **Configurer CORS pour votre domaine**
5. **Utiliser un reverse proxy (nginx)**

### Monitoring

- Health check disponible sur `/health`
- Logs structurés avec uvicorn
- Métriques de performance intégrées

## 🤝 Intégration avec autres microservices

Ce service expose des endpoints pour :
- Vérification des tokens JWT
- Validation des rôles utilisateur
- Récupération des informations utilisateur

Les autres microservices peuvent utiliser les tokens JWT générés ici pour l'authentification.

## 📞 Support

Pour toute question ou problème, consultez la documentation ou créez une issue dans le repository du projet.
