# PresencePro Course Service

Service de gestion des cours et emplois du temps pour l'application PresencePro. Ce microservice gère les cours, les emplois du temps et l'attribution des enseignants et étudiants aux cours.

## 🚀 Fonctionnalités

### Gestion des Cours
- **CRUD complet** : Création, consultation, mise à jour, suppression des cours
- **Recherche avancée** : Par nom, code, matière, niveau
- **Filtres multiples** : Matière, niveau, année académique, semestre, statut
- **Statistiques** : Nombre d'étudiants, enseignants, créneaux horaires

### Gestion des Emplois du Temps
- **Créneaux horaires** : Définition des horaires de cours
- **Gestion des salles** : Attribution et vérification des conflits
- **Planning hebdomadaire** : Vue d'ensemble des emplois du temps
- **Planning enseignant** : Emploi du temps spécifique par enseignant

### Attribution des Cours
- **Attribution enseignants** : Assignation des enseignants aux cours
- **Inscription étudiants** : Gestion des inscriptions aux cours
- **Gestion des capacités** : Respect des limites d'étudiants par cours
- **Périodes de validité** : Gestion des dates de début et fin d'attribution

### Sécurité
- **Authentification JWT** via le service d'authentification
- **Autorisation par rôles** (Admin, Teacher, Parent, Student)
- **Permissions granulaires** selon le type d'utilisateur

## 📋 Prérequis

- Python 3.12+
- PostgreSQL 15+
- Service d'authentification PresencePro (port 8001)
- Service utilisateur PresencePro (port 8002)

## 🛠️ Installation

### 1. Cloner et installer les dépendances

```bash
cd course-service
pip install -r requirements.txt
```

### 2. Configuration

Créer un fichier `.env` :

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/presencepro_courses

# Service Configuration
SERVICE_NAME=course-service
SERVICE_VERSION=1.0.0
SERVICE_PORT=8003

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256

# External Services
AUTH_SERVICE_URL=http://localhost:8001
USER_SERVICE_URL=http://localhost:8002

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://localhost:8002"]

# Logs
LOG_LEVEL=INFO
```

### 3. Initialiser la base de données

```bash
python init_db.py
```

### 4. Lancer le service

```bash
uvicorn app.main:app --reload --port 8003
```

## 📚 Documentation API

Une fois le service lancé, accédez à :
- **Swagger UI** : http://localhost:8003/docs
- **ReDoc** : http://localhost:8003/redoc

## 🔗 Endpoints Principaux

### Cours (`/courses`)
- `POST /courses/` - Créer un cours (Admin)
- `GET /courses/` - Lister les cours avec filtres
- `GET /courses/search` - Rechercher des cours
- `GET /courses/{id}` - Détails d'un cours
- `GET /courses/{id}/complete` - Cours avec emplois du temps et attributions
- `GET /courses/{id}/stats` - Statistiques d'un cours
- `PUT /courses/{id}` - Modifier un cours (Admin)
- `DELETE /courses/{id}` - Supprimer un cours (Admin)
- `GET /courses/teacher/{teacher_id}` - Cours d'un enseignant
- `GET /courses/student/{student_id}` - Cours d'un étudiant

### Emplois du Temps (`/schedules`)
- `POST /schedules/` - Créer un créneau horaire (Admin)
- `GET /schedules/{id}` - Détails d'un créneau
- `GET /schedules/course/{course_id}` - Créneaux d'un cours
- `GET /schedules/day/{day}` - Créneaux d'un jour
- `GET /schedules/room/{room}` - Créneaux d'une salle
- `GET /schedules/weekly` - Planning hebdomadaire
- `GET /schedules/teacher/{teacher_id}/weekly` - Planning enseignant
- `PUT /schedules/{id}` - Modifier un créneau (Admin)
- `DELETE /schedules/{id}` - Supprimer un créneau (Admin)

### Attributions (`/assignments`)
- `POST /assignments/` - Créer une attribution (Admin)
- `POST /assignments/multiple` - Attributions multiples (Admin)
- `GET /assignments/{id}` - Détails d'une attribution
- `GET /assignments/course/{course_id}` - Attributions d'un cours
- `GET /assignments/course/{course_id}/teachers` - Enseignants d'un cours
- `GET /assignments/course/{course_id}/students` - Étudiants d'un cours
- `GET /assignments/user/{user_id}` - Attributions d'un utilisateur
- `PUT /assignments/{id}` - Modifier une attribution (Admin)
- `DELETE /assignments/{id}` - Supprimer une attribution (Admin)
- `DELETE /assignments/course/{course_id}/user/{user_id}` - Retirer un utilisateur

## 🔐 Authentification

Le service utilise des tokens JWT fournis par le service d'authentification.

### Headers requis
```
Authorization: Bearer <jwt_token>
```

### Hiérarchie des rôles
1. **Admin** : Accès complet (CRUD sur tous les éléments)
2. **Teacher** : Lecture de tous les cours, modification de ses propres données
3. **Parent** : Lecture des cours de ses enfants
4. **Student** : Lecture de ses propres cours

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
# Tests des cours
python -m pytest tests/test_courses.py -v

# Tests des services
python -m pytest tests/test_services.py -v
```

## 📊 Modèles de Données

### Course (Cours)
```python
{
    "id": 1,
    "name": "Mathématiques Avancées",
    "code": "MATH001",
    "description": "Cours de mathématiques niveau 6ème",
    "subject": "Mathématiques",
    "level": "6ème",
    "credits": 3,
    "max_students": 25,
    "status": "active",
    "academic_year": "2023-2024",
    "semester": "Semestre 1",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
}
```

### Schedule (Emploi du Temps)
```python
{
    "id": 1,
    "course_id": 1,
    "day_of_week": "monday",
    "start_time": "08:00:00",
    "end_time": "09:30:00",
    "room": "A101",
    "building": "Bâtiment A",
    "start_date": "2023-09-01",
    "end_date": "2024-01-31",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
}
```

### CourseAssignment (Attribution)
```python
{
    "id": 1,
    "course_id": 1,
    "user_id": "teacher1",
    "assignment_type": "teacher",
    "is_primary": true,
    "assigned_at": "2023-01-01T00:00:00",
    "valid_from": "2023-09-01",
    "valid_to": "2024-06-30",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
}
```

## 🔧 Configuration Avancée

### Base de données PostgreSQL
```bash
# Créer la base de données
createdb presencepro_courses

# Configurer l'utilisateur
psql presencepro_courses
CREATE USER course_user WITH PASSWORD 'course_password';
GRANT ALL PRIVILEGES ON DATABASE presencepro_courses TO course_user;
```

### Migrations Alembic
```bash
# Créer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head
```

## 🚀 Déploiement

### Docker
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  course-service:
    build: .
    ports:
      - "8003:8003"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/presencepro_courses
      - AUTH_SERVICE_URL=http://auth-service:8001
      - USER_SERVICE_URL=http://user-service:8002
    depends_on:
      - db
      - auth-service
      - user-service
```

## 🤝 Intégration avec d'autres services

### Service d'authentification
- Vérification des tokens JWT
- Validation des permissions utilisateur

### Service utilisateur
- Récupération des informations utilisateur
- Validation de l'existence des utilisateurs

## 📈 Monitoring et Logs

### Health Check
```bash
curl http://localhost:8003/health
```

### Métriques
- Endpoint de santé : `/health`
- Informations du service : `/`
- Documentation : `/docs`

## 🐛 Dépannage

### Problèmes courants

1. **Erreur de connexion à la base de données**
   - Vérifiez l'URL PostgreSQL
   - Assurez-vous que PostgreSQL est démarré

2. **Erreur d'authentification**
   - Vérifiez que le service d'authentification est accessible
   - Validez l'URL du service d'authentification

3. **Conflits d'horaires**
   - Vérifiez les créneaux existants pour la même salle
   - Utilisez des salles différentes ou des horaires différents

## 📄 Licence

Ce projet fait partie de PresencePro et suit la même licence.

## 👥 Contribution

Pour contribuer au projet :
1. Forkez le repository
2. Créez une branche feature
3. Ajoutez des tests pour vos modifications
4. Assurez-vous que tous les tests passent
5. Soumettez une pull request
