# 📊 Attendance Service - PresencePro

Le microservice **Attendance Service** est le cœur du système de gestion des présences de PresencePro. Il gère l'enregistrement, le suivi et l'analyse des présences et absences des étudiants.

## 🎯 **Fonctionnalités Principales**

### 📝 **Gestion des Présences**
- ✅ **Marquage de présence** manuel et automatique
- ✅ **Marquage en lot** pour les sessions de cours
- ✅ **Statuts multiples** : Présent, Absent, En retard, Excusé, Partiel
- ✅ **Méthodes d'enregistrement** : Manuel, Reconnaissance faciale, QR Code, RFID, API
- ✅ **Validation et modification** des présences
- ✅ **Horodatage précis** avec gestion des fuseaux horaires

### 🔗 **Intégration Reconnaissance Faciale**
- ✅ **Réception automatique** des données du face-recognition-service
- ✅ **Marquage automatique** basé sur la confiance de reconnaissance
- ✅ **Webhook** pour notifications en temps réel
- ✅ **Validation croisée** avec les emplois du temps

### 📊 **Rapports et Analytics**
- ✅ **Statistiques détaillées** par étudiant, cours, période
- ✅ **Tendances de présence** avec moyennes mobiles
- ✅ **Rapports comparatifs** entre cours
- ✅ **Analyse temporelle** (patterns horaires, jours de la semaine)
- ✅ **Export** Excel, CSV, PDF

### 🔔 **Système d'Alertes**
- ✅ **Détection automatique** des patterns d'absence
- ✅ **Alertes de retards fréquents**
- ✅ **Absences consécutives**
- ✅ **Notifications** configurables par seuils

### 🎓 **Sessions de Présence**
- ✅ **Gestion de sessions** avec début/fin automatique
- ✅ **Marquage automatique absent** après délai
- ✅ **Période de grâce** configurable
- ✅ **Statistiques de session** en temps réel

## 🏗️ **Architecture Technique**

### **Stack Technologique**
- **Framework** : FastAPI (Python 3.11+)
- **Base de données** : PostgreSQL avec SQLAlchemy ORM
- **Migrations** : Alembic
- **Validation** : Pydantic
- **Export** : Pandas, OpenPyXL
- **Containerisation** : Docker + Docker Compose

### **Structure du Projet**
```
attendance-service/
├── app/
│   ├── core/              # Configuration et base de données
│   │   ├── config.py      # Configuration centralisée
│   │   └── database.py    # Connexion PostgreSQL
│   ├── models/            # Modèles de données
│   │   ├── attendance.py  # Modèles SQLAlchemy
│   │   └── schemas.py     # Schémas Pydantic
│   ├── services/          # Logique métier
│   │   ├── attendance_service.py     # Gestion des présences
│   │   ├── integration_service.py    # Intégration services
│   │   ├── alert_service.py          # Système d'alertes
│   │   └── report_service.py         # Rapports avancés
│   ├── routes/            # Endpoints API
│   │   ├── attendance.py  # Routes principales
│   │   ├── alerts.py      # Routes alertes
│   │   └── reports.py     # Routes rapports
│   └── main.py           # Application FastAPI
├── alembic/              # Migrations de base de données
├── tests/                # Tests unitaires et d'intégration
├── init_db.py           # Script d'initialisation
├── test_service.py      # Tests automatisés
└── validate_integration.py  # Validation intégration
```

## 🚀 **Installation et Déploiement**

### **Prérequis**
- Python 3.11+
- PostgreSQL 13+
- Docker (optionnel)

### **Installation Locale**

1. **Cloner et naviguer**
```bash
cd attendance-service
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer la base de données**
```bash
# Créer la base de données PostgreSQL
createdb presencepro_attendance

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres
```

4. **Initialiser la base de données**
```bash
python init_db.py
```

5. **Démarrer le service**
```bash
uvicorn app.main:app --reload --port 8005
```

### **Déploiement Docker**

1. **Docker Compose (Recommandé)**
```bash
docker-compose up -d
```

2. **Docker manuel**
```bash
# Build
docker build -t presencepro/attendance-service .

# Run
docker run -p 8005:8005 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  presencepro/attendance-service
```

## 📡 **API REST**

### **Endpoints Principaux**

#### **🎯 Gestion des Présences** (`/api/v1/attendance`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/mark` | Marquer une présence |
| `POST` | `/bulk-mark` | Marquer plusieurs présences |
| `GET` | `/student/{id}` | Présences d'un étudiant |
| `GET` | `/course/{id}` | Présences d'un cours |
| `PUT` | `/{id}` | Modifier une présence |
| `GET` | `/stats` | Statistiques de présence |
| `POST` | `/face-recognition` | Endpoint reconnaissance faciale |

#### **🔔 Alertes** (`/api/v1/alerts`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/student/{id}` | Alertes d'un étudiant |
| `POST` | `/{id}/read` | Marquer alerte comme lue |
| `POST` | `/{id}/resolve` | Résoudre une alerte |
| `POST` | `/check-patterns/{id}` | Vérifier patterns d'absence |
| `GET` | `/pending/count` | Compter alertes en attente |

#### **📊 Rapports** (`/api/v1/reports`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/student/{id}` | Rapport détaillé étudiant |
| `GET` | `/course/{id}` | Rapport détaillé cours |
| `POST` | `/export` | Exporter données (Excel/CSV) |
| `GET` | `/dashboard/stats` | Statistiques tableau de bord |

### **Exemples d'Utilisation**

#### **Marquer une Présence**
```bash
curl -X POST "http://localhost:8005/api/v1/attendance/mark" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_001",
    "course_id": 1,
    "status": "present",
    "method": "manual",
    "notes": "Présence normale"
  }'
```

#### **Récupérer les Présences d'un Étudiant**
```bash
curl "http://localhost:8005/api/v1/attendance/student/student_001?limit=10"
```

#### **Générer un Rapport**
```bash
curl "http://localhost:8005/api/v1/reports/student/student_001?start_date=2024-01-01&end_date=2024-01-31"
```

## 🔗 **Intégration avec les Services**

### **Services Intégrés**
- **auth-service** (8001) : Authentification et autorisation
- **user-service** (8002) : Validation des utilisateurs
- **course-service** (8003) : Validation des cours et emplois du temps
- **face-recognition-service** (8004) : Reconnaissance faciale automatique

### **Flux d'Intégration**

#### **Reconnaissance Faciale Automatique**
1. Face-recognition-service détecte un visage
2. Reconnaissance et identification de l'étudiant
3. Envoi automatique vers attendance-service
4. Validation avec course-service (cours actuel)
5. Marquage automatique de la présence
6. Génération d'alertes si nécessaire

#### **Validation Croisée**
- Vérification existence étudiant (user-service)
- Validation cours actif (course-service)
- Contrôle inscription étudiant au cours
- Vérification emploi du temps

## 📊 **Modèles de Données**

### **Attendance (Présences)**
```python
{
  "id": 1,
  "student_id": "student_001",
  "course_id": 1,
  "schedule_id": 1,
  "status": "present|absent|late|excused|partial",
  "method": "manual|face_recognition|qr_code|rfid|api",
  "scheduled_start_time": "2024-01-15T09:00:00Z",
  "actual_arrival_time": "2024-01-15T09:05:00Z",
  "confidence_score": 0.95,
  "location": "Salle A101",
  "notes": "Présence normale",
  "is_validated": true,
  "created_at": "2024-01-15T09:05:00Z"
}
```

### **AttendanceAlert (Alertes)**
```python
{
  "id": 1,
  "alert_type": "high_absence_rate",
  "severity": "high",
  "student_id": "student_001",
  "course_id": 1,
  "title": "Taux d'absence élevé",
  "message": "Taux d'absence de 40% sur les 4 dernières semaines",
  "is_read": false,
  "is_resolved": false,
  "created_at": "2024-01-15T10:00:00Z"
}
```

## 🧪 **Tests et Validation**

### **Tests Automatisés**
```bash
# Tests complets du service
python test_service.py

# Validation de l'intégration
python validate_integration.py

# Tests unitaires (si pytest installé)
pytest tests/ -v
```

### **Tests Couverts**
- ✅ Marquage de présence (individuel et en lot)
- ✅ Récupération des données
- ✅ Génération de rapports
- ✅ Système d'alertes
- ✅ Intégration reconnaissance faciale
- ✅ Validation croisée avec autres services

## ⚙️ **Configuration**

### **Variables d'Environnement**
```env
# Service
SERVICE_PORT=8005
DEBUG=True

# Base de données
DATABASE_URL=postgresql://postgres:password@localhost:5432/presencepro_attendance

# Intégration services
AUTH_SERVICE_URL=http://localhost:8001
USER_SERVICE_URL=http://localhost:8002
COURSE_SERVICE_URL=http://localhost:8003
FACE_RECOGNITION_SERVICE_URL=http://localhost:8004

# Configuration présences
ATTENDANCE_GRACE_PERIOD_MINUTES=15
LATE_THRESHOLD_MINUTES=10
AUTO_MARK_ABSENT_HOURS=2

# Timezone
DEFAULT_TIMEZONE=Europe/Paris
```

### **Règles de Présence Configurables**
- **Période de grâce** : Temps accordé après le début du cours
- **Seuil de retard** : Délai pour considérer un retard
- **Marquage automatique absent** : Délai avant marquage automatique
- **Seuils d'alertes** : Taux d'absence/retard pour déclencher alertes

## 📈 **Monitoring et Logs**

### **Health Checks**
```bash
curl http://localhost:8005/health
```

### **Métriques Disponibles**
- Total des présences enregistrées
- Sessions actives
- Alertes en attente
- Statut de la base de données
- Connectivité avec les autres services

### **Logs Structurés**
- Niveau configurable (DEBUG, INFO, WARNING, ERROR)
- Rotation automatique des fichiers
- Format JSON pour intégration monitoring

## 🔒 **Sécurité**

### **Authentification**
- Intégration avec auth-service pour validation JWT
- Vérification des permissions par rôle
- Audit trail complet des modifications

### **Validation des Données**
- Schémas Pydantic pour validation entrées
- Sanitisation des données utilisateur
- Contrôles d'intégrité référentielle

## 🚀 **Performance**

### **Optimisations**
- Index de base de données sur les champs fréquents
- Cache des résultats de validation
- Traitement asynchrone des alertes
- Pagination des résultats volumineux

### **Limites**
- Maximum 1000 présences par requête bulk
- Export limité à 10000 enregistrements
- Cache des rapports pendant 5 minutes

## 🔄 **Roadmap**

### **Fonctionnalités Prévues**
- [ ] **Notifications push** pour alertes critiques
- [ ] **Machine Learning** pour prédiction d'absences
- [ ] **API GraphQL** pour requêtes complexes
- [ ] **Synchronisation offline** pour applications mobiles
- [ ] **Intégration calendrier** (Google Calendar, Outlook)

### **Améliorations Techniques**
- [ ] **Redis** pour cache distribué
- [ ] **Elasticsearch** pour recherche avancée
- [ ] **Prometheus** pour métriques détaillées
- [ ] **Kubernetes** pour déploiement cloud

---

## 📞 **Support**

- **Documentation API** : http://localhost:8005/docs
- **Health Check** : http://localhost:8005/health
- **Service Info** : http://localhost:8005/info

**🎊 Le Attendance Service est maintenant prêt à gérer toutes vos présences avec précision et intelligence !** 📊
