# PresencePro User Service

Service de gestion des utilisateurs pour l'application PresencePro. Ce microservice gère les étudiants, enseignants, parents et leurs relations.

## 🚀 Fonctionnalités

### Gestion des Utilisateurs
- **Étudiants** : Création, consultation, mise à jour, suppression
- **Enseignants** : Gestion complète avec départements et matières
- **Parents** : Gestion des informations parentales
- **Relations Parent-Élève** : Liens familiaux avec types de relations

### Sécurité
- Authentification JWT via le service d'authentification
- Autorisation basée sur les rôles (Admin, Teacher, Parent, Student)
- Permissions granulaires selon le type d'utilisateur

### API REST
- Endpoints RESTful complets (CRUD)
- Documentation automatique avec Swagger/OpenAPI
- Validation des données avec Pydantic
- Pagination et filtres de recherche

## 📋 Prérequis

- Python 3.12+
- FastAPI
- SQLAlchemy
- SQLite (développement) ou PostgreSQL (production)
- Service d'authentification PresencePro

## 🛠️ Installation

### 1. Cloner et installer les dépendances

```bash
cd user-service
pip install -r requirements.txt
```

### 2. Configuration

Créer un fichier `.env` :

```env
# Database Configuration
DATABASE_URL=sqlite:///./presencepro_users.db
# ou pour PostgreSQL :
# DATABASE_URL=postgresql://user:password@host:port/database

# Service Configuration
SERVICE_NAME=user-service
SERVICE_VERSION=1.0.0
SERVICE_PORT=8002

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256

# External Services
AUTH_SERVICE_URL=http://localhost:8001

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000", "http://localhost:8001"]

# Logs
LOG_LEVEL=INFO
```

### 3. Initialiser la base de données

```bash
python init_db.py
```

### 4. Lancer le service

```bash
uvicorn app.main:app --reload --port 8002
```

## 📚 Documentation API

Une fois le service lancé, accédez à :
- **Swagger UI** : http://localhost:8002/docs
- **ReDoc** : http://localhost:8002/redoc

## 🔗 Endpoints Principaux

### Étudiants (`/students`)
- `POST /students/` - Créer un étudiant (Admin)
- `GET /students/` - Lister les étudiants (Teacher+)
- `GET /students/{id}` - Détails d'un étudiant
- `PUT /students/{id}` - Modifier un étudiant (Admin)
- `DELETE /students/{id}` - Supprimer un étudiant (Admin)
- `GET /students/search` - Rechercher des étudiants

### Enseignants (`/teachers`)
- `POST /teachers/` - Créer un enseignant (Admin)
- `GET /teachers/` - Lister les enseignants (Teacher+)
- `GET /teachers/{id}` - Détails d'un enseignant
- `PUT /teachers/{id}` - Modifier un enseignant (Admin)
- `DELETE /teachers/{id}` - Supprimer un enseignant (Admin)
- `GET /teachers/by-department/{dept}` - Par département
- `GET /teachers/by-subject/{subject}` - Par matière

### Parents (`/parents`)
- `POST /parents/` - Créer un parent (Admin)
- `GET /parents/` - Lister les parents (Teacher+)
- `GET /parents/{id}` - Détails d'un parent
- `PUT /parents/{id}` - Modifier un parent (Admin)
- `DELETE /parents/{id}` - Supprimer un parent (Admin)
- `POST /parents/{parent_id}/students/{student_id}` - Créer relation
- `GET /parents/{parent_id}/students` - Enfants d'un parent
- `DELETE /parents/relations/{relation_id}` - Supprimer relation

## 🔐 Authentification

Le service utilise des tokens JWT fournis par le service d'authentification. 

### Headers requis
```
Authorization: Bearer <jwt_token>
```

### Hiérarchie des rôles
1. **Admin** : Accès complet (CRUD sur tous les utilisateurs)
2. **Teacher** : Lecture de tous les utilisateurs, modification de ses propres données
3. **Parent** : Lecture de ses enfants et de ses propres données
4. **Student** : Lecture de ses propres données uniquement

## 🧪 Tests

### Lancer tous les tests
```bash
python -m pytest tests/ -v
```

### Tests avec couverture
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

### Tests spécifiques
```bash
# Tests des étudiants
python -m pytest tests/test_students.py -v

# Tests des services
python -m pytest tests/test_services.py -v
```

## 📊 Modèles de Données

### Student (Étudiant)
```python
{
    "id": 1,
    "user_id": "student123",
    "student_number": "STU001",
    "first_name": "Alice",
    "last_name": "Johnson",
    "email": "alice@example.com",
    "phone": "0123456789",
    "date_of_birth": "2005-01-15",
    "address": "123 Rue Example",
    "class_name": "6ème A",
    "academic_year": "2023-2024",
    "is_active": true,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
}
```

### Teacher (Enseignant)
```python
{
    "id": 1,
    "user_id": "teacher123",
    "employee_number": "EMP001",
    "first_name": "Marie",
    "last_name": "Dupont",
    "email": "marie@example.com",
    "phone": "0123456789",
    "department": "Mathématiques",
    "subject": "Algèbre",
    "hire_date": "2020-09-01",
    "is_active": true,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
}
```

### Parent
```python
{
    "id": 1,
    "user_id": "parent123",
    "first_name": "Robert",
    "last_name": "Johnson",
    "email": "robert@example.com",
    "phone": "0123456789",
    "address": "123 Rue Example",
    "profession": "Ingénieur",
    "emergency_contact": true,
    "is_active": true,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
}
```

### ParentStudentRelation (Relation Parent-Élève)
```python
{
    "id": 1,
    "parent_id": 1,
    "student_id": 1,
    "relationship_type": "père",
    "is_primary_contact": true,
    "is_emergency_contact": false,
    "created_at": "2023-01-01T00:00:00"
}
```

## 🔧 Configuration Avancée

### Base de données PostgreSQL
```env
DATABASE_URL=postgresql://username:password@localhost:5432/presencepro_users
```

### Migrations Alembic
```bash
# Créer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head
```

### Variables d'environnement
- `DATABASE_URL` : URL de connexion à la base de données
- `AUTH_SERVICE_URL` : URL du service d'authentification
- `SECRET_KEY` : Clé secrète pour la sécurité
- `CORS_ORIGINS` : Origines autorisées pour CORS
- `LOG_LEVEL` : Niveau de logs (DEBUG, INFO, WARNING, ERROR)

## 🚀 Déploiement

### Docker
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  user-service:
    build: .
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/presencepro
      - AUTH_SERVICE_URL=http://auth-service:8001
    depends_on:
      - db
      - auth-service
```

## 🤝 Intégration avec d'autres services

### Service d'authentification
Le service communique avec le service d'authentification pour :
- Vérifier les tokens JWT
- Valider les permissions utilisateur
- Récupérer les informations utilisateur

### Exemple d'utilisation
```python
import httpx

# Créer un étudiant
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8002/students/",
        json={
            "user_id": "student123",
            "student_number": "STU001",
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice@example.com",
            "class_name": "6ème A",
            "academic_year": "2023-2024"
        },
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
```

## 📈 Monitoring et Logs

### Health Check
```bash
curl http://localhost:8002/health
```

### Métriques
- Endpoint de santé : `/health`
- Informations du service : `/`
- Documentation : `/docs`

## 🐛 Dépannage

### Problèmes courants

1. **Erreur de connexion à la base de données**
   - Vérifiez l'URL de la base de données
   - Assurez-vous que la base de données est accessible

2. **Erreur d'authentification**
   - Vérifiez que le service d'authentification est démarré
   - Validez l'URL du service d'authentification

3. **Erreur de permissions**
   - Vérifiez le token JWT
   - Confirmez les rôles utilisateur

### Logs
Les logs sont configurables via la variable `LOG_LEVEL`. Utilisez `DEBUG` pour un débogage détaillé.

## 📄 Licence

Ce projet fait partie de PresencePro et suit la même licence.

## 👥 Contribution

Pour contribuer au projet :
1. Forkez le repository
2. Créez une branche feature
3. Ajoutez des tests pour vos modifications
4. Assurez-vous que tous les tests passent
5. Soumettez une pull request
