# 🎭 Notification Service - PresencePro

Service de notifications asynchrones pour l'envoi d'emails, SMS et notifications push lors d'événements dans l'écosystème PresencePro.

## 🚀 **Fonctionnalités**

### 📧 **Notifications par email**
- **Envoi via SMTP** ou **SendGrid**
- **Templates personnalisables** avec Jinja2
- **Support HTML** avec CSS inline automatique
- **Gestion des pièces jointes**
- **Retry automatique** en cas d'échec

### 📱 **Notifications SMS et Push**
- **SMS via Twilio**
- **Push notifications via Firebase**
- **Gestion des tokens d'appareils**
- **Notifications en lot**

### ⚡ **Traitement asynchrone**
- **Tâches Celery** avec Redis comme broker
- **Queues séparées** par type de notification
- **Retry intelligent** avec backoff exponentiel
- **Monitoring en temps réel** avec Flower

### 🎯 **Événements supportés**
- **Absence détectée** - Notification immédiate aux parents
- **Justification soumise/approuvée/rejetée** - Workflow complet
- **Message reçu** - Notifications de messagerie
- **Approbation parentale requise** - Workflow de validation
- **Validation administrative requise** - Processus d'approbation
- **Rapports quotidiens/hebdomadaires** - Digest automatiques

## 🏗️ **Architecture**

### **Technologies**
- **FastAPI** : Framework web moderne
- **Celery** : Tâches asynchrones distribuées
- **Redis** : Broker de messages et cache
- **SQLAlchemy** : ORM pour la persistance
- **Jinja2** : Moteur de templates
- **SendGrid/SMTP** : Envoi d'emails
- **Twilio** : Envoi de SMS
- **Firebase** : Notifications push

### **Structure du projet**
```
notification-service/
├── app/
│   ├── core/              # Configuration et Celery
│   ├── models/            # Modèles SQLAlchemy
│   ├── services/          # Services métier
│   ├── tasks/             # Tâches Celery
│   └── templates/         # Templates d'emails
├── templates/             # Templates Jinja2
├── logs/                  # Fichiers de log
├── init_service.py       # Initialisation
├── start_celery.py       # Démarrage Celery
├── test_service.py       # Tests automatisés
└── docker-compose.yml    # Configuration Docker
```

## 📊 **Modèles de données**

### **NotificationLog**
```python
{
    "notification_id": "uuid",
    "user_id": "string",
    "notification_type": "absence_detected|justification_approved|...",
    "channel": "email|sms|push",
    "priority": "low|normal|high|urgent",
    "subject": "string",
    "content": "text",
    "recipient_email": "email",
    "status": "pending|sent|failed|retry|cancelled",
    "retry_count": "integer",
    "created_at": "datetime",
    "sent_at": "datetime"
}
```

### **NotificationTemplate**
```python
{
    "template_id": "string",
    "name": "string",
    "notification_type": "string",
    "channel": "email|sms|push",
    "language": "fr|en",
    "subject_template": "string",
    "content_template": "text",
    "html_template": "text",
    "variables": "json",
    "is_active": "boolean",
    "is_default": "boolean"
}
```

### **UserPreference**
```python
{
    "user_id": "string",
    "email_enabled": "boolean",
    "sms_enabled": "boolean", 
    "push_enabled": "boolean",
    "absence_notifications": "boolean",
    "justification_notifications": "boolean",
    "message_notifications": "boolean",
    "immediate_alerts": "boolean",
    "daily_digest": "boolean",
    "weekly_report": "boolean",
    "quiet_hours_start": "time",
    "quiet_hours_end": "time",
    "timezone": "string",
    "language": "string"
}
```

## 🎯 **Événements et Templates**

### **Événements supportés**
- `absence_detected` - Absence détectée par le système
- `justification_submitted` - Justification soumise par l'étudiant
- `justification_approved` - Justification approuvée
- `justification_rejected` - Justification rejetée
- `parent_approval_required` - Approbation parentale nécessaire
- `admin_validation_required` - Validation administrative nécessaire
- `message_received` - Nouveau message reçu
- `attendance_alert` - Alerte de présence
- `weekly_report` - Rapport hebdomadaire
- `monthly_report` - Rapport mensuel

### **Templates par défaut**
- **absence_detected_email_fr** - Notification d'absence par email
- **justification_approved_email_fr** - Justification approuvée
- **message_received_email_fr** - Nouveau message reçu

## ⚡ **Tâches Celery**

### **Queues de traitement**
- **email** - Envoi d'emails
- **sms** - Envoi de SMS
- **push** - Notifications push
- **events** - Traitement d'événements

### **Tâches principales**
- `send_email_task` - Envoi d'email individuel
- `send_bulk_emails_task` - Envoi d'emails en lot
- `process_event` - Traitement d'événement
- `send_daily_digest` - Digest quotidien
- `send_weekly_report` - Rapport hebdomadaire
- `cleanup_old_notifications` - Nettoyage automatique

## 🚀 **Installation et démarrage**

### **Prérequis**
- Python 3.9+
- Redis 6.0+
- SQLite ou PostgreSQL
- Docker (optionnel)

### **Installation locale**
```bash
# Cloner le repository
git clone https://github.com/Mey-Ven/PresencePro.git
cd PresencePro/notification-service

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env .env.local
# Éditer .env avec vos paramètres

# Initialiser le service
python init_service.py

# Démarrer Redis (dans un terminal séparé)
redis-server

# Démarrer le worker Celery (dans un terminal séparé)
python start_celery.py worker

# Démarrer le scheduler Celery Beat (dans un terminal séparé)
python start_celery.py beat

# Démarrer le service FastAPI
uvicorn app.main:app --reload --port 8008
```

### **Avec Docker**
```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f notification-service

# Arrêter les services
docker-compose down
```

## 🧪 **Tests**

### **Tests automatisés**
```bash
# Exécuter les tests
python test_service.py

# Tests spécifiques
python init_service.py test-email
python init_service.py stats
```

### **Tests manuels**
```bash
# Vérifier la santé
curl http://localhost:8008/health

# Informations du service
curl http://localhost:8008/info

# Tester un événement (mode debug)
curl -X POST http://localhost:8008/test/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "absence_detected",
    "source_service": "test",
    "data": {
      "student_name": "Alice Martin",
      "parent_name": "Marie Martin",
      "absence_date": "2025-06-20",
      "parent_emails": ["parent@test.com"]
    }
  }'
```

## ⚙️ **Configuration**

### **Variables d'environnement**
```env
# Service
SERVICE_PORT=8008
DEBUG=True

# Base de données
DATABASE_URL=sqlite:///./notifications.db

# Redis et Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Email - SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@presencepro.com

# Email - SendGrid
SENDGRID_API_KEY=your-sendgrid-key
USE_SENDGRID=False

# SMS - Twilio
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
SMS_ENABLED=False

# Push - Firebase
FIREBASE_SERVER_KEY=your-firebase-key
PUSH_NOTIFICATIONS_ENABLED=False

# Services externes
AUTH_SERVICE_URL=http://localhost:8001
USER_SERVICE_URL=http://localhost:8002
ATTENDANCE_SERVICE_URL=http://localhost:8005
JUSTIFICATION_SERVICE_URL=http://localhost:8006
MESSAGING_SERVICE_URL=http://localhost:8007
```

## 🔗 **Intégration PresencePro**

### **Écoute d'événements**
Le service écoute automatiquement les événements Redis publiés par :
- **attendance-service** : Détection d'absences
- **justification-service** : Workflow de justifications
- **messaging-service** : Nouveaux messages

### **Format d'événement**
```json
{
  "event_type": "absence_detected",
  "source_service": "attendance-service",
  "data": {
    "student_id": "student_001",
    "student_name": "Alice Martin",
    "parent_name": "Marie Martin",
    "absence_date": "2025-06-20",
    "absence_time": "09:00",
    "course_name": "Mathématiques",
    "teacher_name": "Prof. Dupont",
    "parent_emails": ["marie.martin@email.com"]
  },
  "timestamp": "2025-06-20T09:00:00Z"
}
```

## 📈 **Monitoring**

### **Health checks**
- Statut de la base de données
- Connexion Redis
- Workers Celery actifs
- Écoute d'événements

### **Flower (Monitoring Celery)**
```bash
# Démarrer Flower
python start_celery.py flower

# Accéder à l'interface
http://localhost:5555
```

### **Métriques**
- Nombre de notifications envoyées
- Taux de succès par canal
- Temps de traitement moyen
- Taille des queues

## 🔧 **Développement**

### **Ajouter un nouveau type d'événement**
1. Ajouter le type dans `NotificationType`
2. Créer le template dans `template_service.py`
3. Ajouter le handler dans `event_tasks.py`
4. Tester avec `/test/event`

### **Ajouter un nouveau canal**
1. Créer le service dans `services/`
2. Ajouter les tâches dans `tasks/`
3. Mettre à jour la configuration
4. Ajouter les tests

## 📝 **TODO / Améliorations**

- [ ] **Interface d'administration** : Dashboard de gestion
- [ ] **Notifications push** : Intégration Firebase complète
- [ ] **Templates visuels** : Éditeur WYSIWYG
- [ ] **A/B Testing** : Test de templates
- [ ] **Analytics** : Tableaux de bord détaillés
- [ ] **Webhooks sortants** : Notifications vers services externes
- [ ] **Chiffrement** : Chiffrement des données sensibles
- [ ] **Multi-tenant** : Support multi-établissement

## 📞 **Support**

Pour toute question ou problème :
- **Documentation** : http://localhost:8008/docs
- **Health check** : http://localhost:8008/health
- **Monitoring Celery** : http://localhost:5555
- **Logs** : `./logs/notifications.log`

---

**🎭 PresencePro Notification Service** - Notifications intelligentes pour l'éducation
