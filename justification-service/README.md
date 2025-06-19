# 📋 Justification Service - PresencePro

Service de gestion des justifications d'absence pour l'écosystème PresencePro.

## 🎯 **Fonctionnalités**

### 📝 **Gestion Complète des Justifications**
- ✅ **Soumission de justifications** par les étudiants
- ✅ **Approbation parentale** avec workflow configurable
- ✅ **Validation administrative** par les enseignants/administrateurs
- ✅ **Gestion de documents** avec upload de pièces justificatives
- ✅ **Historique complet** des modifications et actions
- ✅ **Templates prédéfinis** pour faciliter la création

### 🔄 **Workflow d'Approbation**
1. **Étudiant** crée une justification d'absence
2. **Soumission** pour approbation
3. **Parents** approuvent ou rejettent (optionnel)
4. **Administration** valide ou rejette
5. **Notification** automatique du service de présences

### 🔗 **Intégration Services**
- **attendance-service** : Mise à jour automatique des présences
- **user-service** : Validation des utilisateurs et relations parent-enfant
- **auth-service** : Authentification et autorisation
- **course-service** : Validation des cours et emplois du temps

## 🏗️ **Architecture**

### **Structure du Projet**
```
justification-service/
├── app/
│   ├── core/              # Configuration et base de données
│   ├── models/            # Modèles SQLAlchemy et schémas Pydantic
│   ├── services/          # Logique métier
│   ├── routes/            # Endpoints API REST
│   └── utils/             # Utilitaires
├── alembic/               # Migrations de base de données
├── uploads/               # Stockage des documents
├── tests/                 # Tests unitaires et d'intégration
├── init_db.py            # Script d'initialisation
├── test_service.py       # Tests automatisés
└── docker-compose.yml    # Configuration Docker
```

### **Technologies**
- **FastAPI** : Framework web moderne et performant
- **PostgreSQL** : Base de données principale (SQLite pour développement)
- **SQLAlchemy** : ORM avec Alembic pour les migrations
- **Pydantic** : Validation et sérialisation des données
- **HTTPX** : Client HTTP pour intégration services

## 🚀 **Installation et Démarrage**

### **Prérequis**
- Python 3.11+
- PostgreSQL (optionnel, SQLite par défaut)
- Docker et Docker Compose (optionnel)

### **Installation Locale**

1. **Cloner le repository**
```bash
git clone https://github.com/Mey-Ven/PresencePro.git
cd PresencePro/justification-service
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Initialiser la base de données**
```bash
python init_db.py
```

5. **Démarrer le service**
```bash
uvicorn app.main:app --reload --port 8006
```

### **Démarrage avec Docker**

1. **Démarrage simple (SQLite)**
```bash
docker-compose up justification-service-dev
```

2. **Démarrage avec PostgreSQL**
```bash
docker-compose up justification-service postgres
```

3. **Démarrage en arrière-plan**
```bash
docker-compose up -d
```

## 📊 **API REST**

### **Endpoints Principaux**

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/v1/justifications/create` | Créer une justification |
| `POST` | `/api/v1/justifications/{id}/submit` | Soumettre pour approbation |
| `POST` | `/api/v1/justifications/{id}/approve-parent` | Approbation parentale |
| `POST` | `/api/v1/justifications/{id}/validate-admin` | Validation administrative |
| `GET` | `/api/v1/justifications/{id}` | Récupérer une justification |
| `GET` | `/api/v1/justifications/student/{id}` | Justifications d'un étudiant |
| `GET` | `/api/v1/justifications/pending/approvals` | Approbations en attente |
| `GET` | `/api/v1/justifications/pending/validations` | Validations en attente |
| `GET` | `/api/v1/justifications/status/{id}` | Statut d'une justification |
| `POST` | `/api/v1/justifications/{id}/documents` | Upload de document |
| `GET` | `/api/v1/justifications/{id}/documents` | Documents d'une justification |

### **Documentation Interactive**
- **Swagger UI** : http://localhost:8006/docs
- **ReDoc** : http://localhost:8006/redoc

## 🔧 **Configuration**

### **Variables d'Environnement**

```env
# Service
SERVICE_NAME=justification-service
SERVICE_VERSION=1.0.0
SERVICE_PORT=8006
DEBUG=True

# Base de données
DATABASE_URL=sqlite:///./justifications.db
# ou PostgreSQL: postgresql://user:pass@localhost:5432/db

# Services externes
AUTH_SERVICE_URL=http://localhost:8001
USER_SERVICE_URL=http://localhost:8002
COURSE_SERVICE_URL=http://localhost:8003
ATTENDANCE_SERVICE_URL=http://localhost:8005

# Configuration justifications
MAX_JUSTIFICATION_DAYS=7
AUTO_EXPIRE_DAYS=30
REQUIRE_PARENT_APPROVAL=True
REQUIRE_ADMIN_VALIDATION=True

# Upload de fichiers
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,doc,docx
```

## 📋 **Modèles de Données**

### **Justification**
```python
{
    "id": 1,
    "student_id": "student_001",
    "course_id": 1,
    "title": "Absence pour rendez-vous médical",
    "description": "Rendez-vous médical urgent...",
    "justification_type": "medical",
    "priority": "high",
    "absence_start_date": "2024-01-15T08:00:00Z",
    "absence_end_date": "2024-01-15T18:00:00Z",
    "status": "admin_approved",
    "parent_approval_required": true,
    "admin_validation_required": true,
    "created_at": "2024-01-14T10:00:00Z"
}
```

### **Statuts de Justification**
- `draft` : Brouillon
- `submitted` : Soumise
- `parent_pending` : En attente d'approbation parentale
- `parent_approved` : Approuvée par les parents
- `parent_rejected` : Rejetée par les parents
- `admin_pending` : En attente de validation administrative
- `admin_approved` : Validée par l'administration
- `admin_rejected` : Rejetée par l'administration
- `expired` : Expirée
- `cancelled` : Annulée

### **Types de Justification**
- `medical` : Médical
- `family` : Familial
- `transport` : Transport
- `personal` : Personnel
- `academic` : Académique
- `other` : Autre

## 🧪 **Tests**

### **Tests Automatisés**
```bash
# Tester le service
python test_service.py

# Tests avec pytest
pytest tests/

# Tests avec couverture
pytest --cov=app tests/
```

### **Tests d'Intégration**
```bash
# Vérifier l'intégration avec les autres services
python -c "
from app.services.integration_service import IntegrationService
service = IntegrationService()
print('Auth:', service.is_service_available('auth'))
print('User:', service.is_service_available('user'))
print('Course:', service.is_service_available('course'))
print('Attendance:', service.is_service_available('attendance'))
"
```

## 📈 **Monitoring**

### **Health Check**
```bash
curl http://localhost:8006/health
```

### **Informations du Service**
```bash
curl http://localhost:8006/info
```

### **Métriques**
- Total des justifications
- Approbations en attente
- Validations en attente
- Statut de la base de données
- Répertoire d'upload accessible

## 🔒 **Sécurité**

### **Authentification**
- Intégration avec `auth-service` pour la validation des tokens JWT
- Vérification des rôles et permissions

### **Autorisation**
- **Étudiants** : Peuvent créer et modifier leurs justifications
- **Parents** : Peuvent approuver les justifications de leurs enfants
- **Administrateurs** : Peuvent valider toutes les justifications

### **Upload de Fichiers**
- Validation des types de fichiers autorisés
- Limitation de la taille des fichiers
- Stockage sécurisé avec noms de fichiers uniques

## 🔄 **Intégration avec PresencePro**

### **Workflow Complet**
1. **Étudiant absent** détecté par `attendance-service`
2. **Création de justification** via `justification-service`
3. **Validation des données** avec `user-service` et `course-service`
4. **Workflow d'approbation** parents → administration
5. **Mise à jour automatique** de la présence dans `attendance-service`

### **Notifications**
- Webhook vers `attendance-service` lors de la validation
- Notifications par email (configuration SMTP)
- Intégration avec système de notifications push

## 🚀 **Déploiement Production**

### **Docker Compose Production**
```yaml
services:
  justification-service:
    image: presencepro/justification-service:latest
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
    volumes:
      - justification_uploads:/app/uploads
    networks:
      - presencepro-network
```

### **Variables d'Environnement Production**
```env
DEBUG=False
DATABASE_URL=postgresql://user:password@postgres:5432/presencepro_justifications
SECRET_KEY=your-super-secret-key-change-in-production
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📞 **Support**

### **Logs**
```bash
# Voir les logs du service
docker-compose logs justification-service

# Logs en temps réel
docker-compose logs -f justification-service
```

### **Debugging**
```bash
# Mode debug avec hot reload
docker-compose --profile dev up justification-service-dev
```

---

## 🎉 **Le service de justifications est maintenant prêt !**

**Port** : 8006  
**Documentation** : http://localhost:8006/docs  
**Health Check** : http://localhost:8006/health  

Le service s'intègre parfaitement avec l'écosystème PresencePro pour une gestion complète des justifications d'absence avec workflow d'approbation intelligent.
