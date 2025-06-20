# 🎭 Statistics Service - PresencePro

Service de statistiques et d'analyse avancées pour l'écosystème PresencePro. Ce microservice génère des rapports détaillés, des graphiques interactifs et des exports de données pour tous les aspects de la gestion des présences.

## 🚀 **Fonctionnalités principales**

### 📊 **Statistiques individuelles**
- Taux de présence par étudiant avec tendances temporelles
- Évolution des absences et retards dans le temps
- Comparaison avec la moyenne de classe et percentiles
- Prédictions et alertes basées sur les patterns
- Classement et performance relative

### 🏫 **Statistiques de classe**
- Moyennes, médianes et écarts-types de présence
- Classement des étudiants avec anonymisation
- Comparaison entre différents cours et matières
- Identification automatique des étudiants à risque
- Tendances hebdomadaires et mensuelles détaillées

### 🌍 **Statistiques globales**
- Vue d'ensemble de l'établissement avec KPIs
- Comparaison entre classes et niveaux
- Tendances générales et saisonnalité
- Indicateurs de performance institutionnels
- Tableaux de bord exécutifs personnalisables

### 📈 **Génération de graphiques**
- **Graphiques en ligne** : Évolution temporelle des taux de présence
- **Graphiques en barres** : Comparaisons entre étudiants/classes/cours
- **Graphiques en secteurs** : Répartition présences/absences/retards
- **Cartes de chaleur** : Patterns de présence par jour/heure
- **Histogrammes** : Distribution des taux de présence
- **Box plots** : Analyse statistique des performances
- **Nuages de points** : Corrélations entre variables
- **Graphiques en aires** : Évolution cumulative

### 📤 **Export de données**
- **JSON** : Intégration avec systèmes externes
- **CSV** : Analyse dans Excel/Google Sheets
- **Excel (XLSX)** : Rapports formatés avec graphiques
- **PDF** : Rapports imprimables avec visualisations
- **Images haute résolution** : PNG, SVG pour présentations

## 🏗️ **Architecture technique**

### **Stack technologique**
- **FastAPI** : Framework web moderne avec documentation automatique
- **PostgreSQL** : Base de données relationnelle pour les statistiques
- **Redis** : Cache haute performance pour les calculs coûteux
- **Plotly** : Génération de graphiques interactifs
- **Matplotlib/Seaborn** : Graphiques statistiques avancés
- **Pandas/NumPy** : Analyse de données et calculs statistiques
- **SQLAlchemy** : ORM avec optimisations de requêtes

### **Structure du projet**
```
statistics-service/
├── app/
│   ├── core/                 # Configuration et base de données
│   │   ├── config.py         # Configuration centralisée
│   │   └── database.py       # PostgreSQL + Redis
│   ├── models/               # Modèles de données
│   │   └── statistics.py     # Modèles SQLAlchemy et Pydantic
│   ├── services/             # Services métier
│   │   ├── statistics_service.py    # Calculs statistiques
│   │   ├── chart_service.py         # Génération graphiques
│   │   └── integration_service.py   # Intégration services
│   ├── routes/               # Endpoints API
│   │   ├── statistics.py     # Routes principales
│   │   └── health.py         # Santé et monitoring
│   └── main.py              # Application FastAPI
├── exports/                  # Fichiers générés
│   ├── json/                # Exports JSON
│   └── charts/              # Graphiques générés
├── logs/                    # Fichiers de log
├── tests/                   # Tests automatisés
├── init_service.py         # Script d'initialisation
├── test_service.py         # Tests complets
├── Dockerfile              # Configuration Docker
├── docker-compose.yml      # Orchestration
└── README.md              # Documentation
```

## 🎯 **API Endpoints**

### **Statistiques**
- `GET /stats/student/{id}` - Statistiques individuelles d'un étudiant
- `GET /stats/class/{id}` - Statistiques d'une classe
- `GET /stats/global` - Statistiques globales de l'établissement

### **Graphiques**
- `POST /stats/charts/generate` - Générer un graphique personnalisé
- `GET /stats/charts/{chart_id}` - Télécharger un graphique

### **Exports**
- `POST /stats/export` - Exporter des données dans différents formats
- `GET /exports/{file_id}` - Télécharger un fichier exporté

### **Utilitaires**
- `GET /health` - Vérification de santé du service
- `GET /info` - Informations détaillées du service
- `GET /metrics` - Métriques pour monitoring
- `DELETE /stats/cache` - Vider le cache des statistiques

## 📊 **Types de statistiques disponibles**

| Type | Description | Utilisation |
|------|-------------|-------------|
| `attendance_rate` | Taux de présence en pourcentage | Indicateur principal |
| `absence_count` | Nombre total d'absences | Suivi quantitatif |
| `tardiness_count` | Nombre de retards | Ponctualité |
| `justified_absences` | Absences avec justification | Conformité |
| `unjustified_absences` | Absences sans justification | Alertes |
| `weekly_trends` | Évolution hebdomadaire | Tendances court terme |
| `monthly_trends` | Évolution mensuelle | Tendances long terme |
| `course_comparison` | Comparaison entre cours | Analyse matières |
| `student_ranking` | Classement des étudiants | Performance relative |
| `class_average` | Moyennes de classe | Benchmarking |

## 📈 **Types de graphiques**

| Type | Usage | Format |
|------|-------|--------|
| `line_chart` | Évolutions temporelles | Tendances |
| `bar_chart` | Comparaisons | Classements |
| `pie_chart` | Répartitions | Proportions |
| `heatmap` | Patterns complexes | Corrélations |
| `histogram` | Distributions | Statistiques |
| `box_plot` | Analyses statistiques | Outliers |
| `scatter_plot` | Corrélations | Relations |
| `area_chart` | Évolutions cumulatives | Volumes |

## 🚀 **Installation et démarrage**

### **Prérequis**
- Python 3.9+
- PostgreSQL 12+
- Redis 6+ (optionnel, pour le cache)

### **Installation locale**
```bash
# Cloner le repository
git clone https://github.com/Mey-Ven/PresencePro.git
cd PresencePro/statistics-service

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Initialiser le service
python init_service.py init

# Démarrer le service
uvicorn app.main:app --reload --port 8009
```

### **Avec Docker**
```bash
# Démarrer avec docker-compose
docker-compose up -d

# Ou construire l'image
docker build -t statistics-service .
docker run -p 8009:8009 statistics-service
```

## ⚙️ **Configuration**

### **Variables d'environnement principales**
```env
# Service
SERVICE_PORT=8009
DEBUG=True

# Base de données PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/presencepro_stats
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=presencepro_statistics
DATABASE_USER=postgres
DATABASE_PASSWORD=password

# Redis (cache)
REDIS_URL=redis://localhost:6379/1
CACHE_ENABLED=True
CACHE_TTL=3600

# Intégration services
AUTH_SERVICE_URL=http://localhost:8001
USER_SERVICE_URL=http://localhost:8002
COURSE_SERVICE_URL=http://localhost:8003
ATTENDANCE_SERVICE_URL=http://localhost:8005

# Graphiques
CHART_WIDTH=1200
CHART_HEIGHT=800
CHART_FORMAT=png
CHART_THEME=plotly_white

# Performance
MAX_PERIOD_DAYS=365
QUERY_TIMEOUT_SECONDS=30
BATCH_SIZE=1000
```

## 🧪 **Tests et validation**

### **Tests automatisés**
```bash
# Tests complets
python test_service.py

# Tests spécifiques
python init_service.py test-stats
python init_service.py test-charts
python init_service.py health
```

### **Génération de données d'exemple**
```bash
# Créer des données d'exemple pour les tests
python init_service.py sample-data

# Synchroniser avec attendance-service
python init_service.py sync
```

## 📊 **Exemples d'utilisation**

### **Statistiques d'un étudiant**
```bash
curl "http://localhost:8009/stats/student/student_001?start_date=2024-01-01&end_date=2024-01-31&include_trends=true"
```

### **Génération d'un graphique**
```bash
curl -X POST "http://localhost:8009/stats/charts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "chart_type": "line_chart",
    "data_source": "student_student_001",
    "title": "Évolution du taux de présence",
    "export_format": "png"
  }'
```

### **Export de données**
```bash
curl -X POST "http://localhost:8009/stats/export" \
  -H "Content-Type: application/json" \
  -d '{
    "data_type": "student_stats",
    "format": "xlsx",
    "entity_type": "student",
    "entity_id": "student_001",
    "include_charts": true
  }'
```

## 🔗 **Intégration PresencePro**

Le service s'intègre avec l'écosystème PresencePro :

- **attendance-service** : Source des données de présence
- **user-service** : Informations des étudiants et enseignants
- **course-service** : Données des cours et classes
- **justification-service** : Justifications d'absence
- **auth-service** : Authentification et permissions
- **notification-service** : Envoi de rapports automatiques

## 📈 **Performance et optimisation**

### **Cache Redis**
- Cache des calculs statistiques coûteux
- TTL configurable par type de données
- Invalidation intelligente lors des mises à jour

### **Optimisations base de données**
- Index sur les colonnes fréquemment requêtées
- Vues matérialisées pour les agrégations
- Requêtes optimisées avec EXPLAIN ANALYZE

### **Traitement asynchrone**
- Calculs longs en arrière-plan
- Pagination pour les gros volumes
- Rate limiting pour la protection

## 🔒 **Sécurité**

- Validation JWT avec auth-service
- Contrôle d'accès basé sur les rôles
- Validation des paramètres d'entrée
- Protection contre l'injection SQL
- Rate limiting des API

## 📊 **Monitoring**

### **Métriques disponibles**
- Temps de réponse des requêtes
- Taux de hit du cache Redis
- Nombre de calculs par type
- Utilisation des ressources

### **Health checks**
- Connexion base de données
- Connexion Redis
- Services externes
- Espace disque pour exports

## 🚀 **Déploiement en production**

### **Docker Compose**
```yaml
version: '3.8'
services:
  statistics-service:
    build: .
    ports:
      - "8009:8009"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/stats
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - postgres
      - redis
```

### **Kubernetes**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: statistics-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: statistics-service
  template:
    spec:
      containers:
      - name: statistics-service
        image: statistics-service:latest
        ports:
        - containerPort: 8009
```

## 📝 **Changelog**

### Version 1.0.0
- ✅ Calculs statistiques de base
- ✅ Génération de graphiques Plotly
- ✅ Export multi-formats
- ✅ Cache Redis
- ✅ Intégration services PresencePro
- ✅ Documentation complète
- ✅ Tests automatisés

## 🤝 **Contribution**

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 **Licence**

Ce projet fait partie de l'écosystème PresencePro.

---

**🎭 PresencePro Statistics Service** - Intelligence analytique pour l'éducation moderne
