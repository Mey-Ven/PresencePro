# PresencePro Gateway Service

## 📋 Description

Le **Gateway Service** est le point d'entrée unique pour tous les microservices de l'écosystème PresencePro. Il agit comme un reverse proxy intelligent avec authentification, autorisation, rate limiting et monitoring intégrés.

## ✨ Fonctionnalités

### 🔐 **Authentification et Autorisation**
- Vérification des tokens JWT
- Gestion des rôles (Admin, Teacher, Student, Parent)
- Contrôle d'accès basé sur les routes
- Headers de contexte utilisateur pour les services

### 🚦 **Proxy Intelligent**
- Routage automatique vers les microservices
- Retry automatique avec backoff exponentiel
- Load balancing (futur)
- Circuit breaker pattern (futur)

### 🛡️ **Sécurité**
- Rate limiting par IP et utilisateur
- Headers de sécurité automatiques
- CORS configuré
- Protection contre les attaques communes

### 📊 **Monitoring et Observabilité**
- Métriques Prometheus intégrées
- Logging structuré avec correlation IDs
- Health checks des services
- Tracing des requêtes

### ⚡ **Performance**
- Cache Redis pour le rate limiting
- Connexions HTTP persistantes
- Compression automatique
- Timeouts configurables

## 🏗️ Architecture

### **Services intégrés**
- **auth-service** (8001) - Authentification
- **user-service** (8002) - Gestion des utilisateurs
- **course-service** (8003) - Gestion des cours
- **face-recognition-service** (8004) - Reconnaissance faciale
- **attendance-service** (8005) - Gestion des présences
- **justification-service** (8006) - Justifications d'absence
- **messaging-service** (8007) - Messagerie
- **notification-service** (8008) - Notifications
- **statistics-service** (8009) - Statistiques et rapports

### **Routage des requêtes**
```
Client → Gateway (8000) → Service approprié (800X)
```

## 🚀 Installation et démarrage

### **Prérequis**
- Python 3.11+
- Redis (optionnel, pour rate limiting)
- Les microservices PresencePro

### **Installation**
```bash
# Cloner le repository
git clone https://github.com/Mey-Ven/PresencePro.git
cd PresencePro/gateway-service

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
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Mode production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
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
# Configuration du Gateway
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
ENVIRONMENT=development

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (Rate Limiting)
REDIS_URL=redis://localhost:6379/0

# Services URLs
AUTH_SERVICE_URL=http://localhost:8001
USER_SERVICE_URL=http://localhost:8002
# ... autres services

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST=20

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### **Routage des services**
Le gateway route automatiquement les requêtes selon les préfixes :
- `/api/v1/auth/*` → auth-service
- `/api/v1/users/*` → user-service
- `/api/v1/attendance/*` → attendance-service
- etc.

## 🔐 Authentification

### **Routes publiques**
- `/api/v1/auth/login`
- `/api/v1/auth/register`
- `/health`
- `/docs`

### **Routes protégées par rôle**
- **Admin uniquement** : `/api/v1/users/*`, `/api/v1/stats/global`
- **Teacher + Admin** : `/api/v1/attendance/*`, `/api/v1/justifications/*`
- **Authentifié** : Autres routes

### **Headers de contexte**
Le gateway ajoute automatiquement ces headers aux requêtes :
```
X-User-ID: user_id
X-User-Email: user@example.com
X-User-Role: admin
X-User-Permissions: read,write,admin
X-Gateway-Request-ID: unique_request_id
```

## 📊 Monitoring

### **Endpoints de santé**
- `GET /health` - Santé du gateway
- `GET /health/services` - Santé de tous les services
- `GET /metrics` - Métriques Prometheus

### **Métriques disponibles**
- `gateway_requests_total` - Nombre total de requêtes
- `gateway_request_duration_seconds` - Durée des requêtes
- `gateway_active_connections` - Connexions actives

### **Prometheus + Grafana**
```bash
# Démarrer le stack de monitoring
docker-compose up prometheus grafana

# Accéder à Grafana
http://localhost:3001 (admin/admin)
```

## 🛡️ Sécurité

### **Rate Limiting**
- 100 requêtes/minute par IP
- 20 requêtes en burst
- Basé sur Redis pour la persistance

### **Headers de sécurité**
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
```

### **CORS**
Configuré pour accepter les requêtes depuis :
- http://localhost:3000 (React app)
- Autres origines configurables

## 🧪 Tests

### **Exécuter les tests**
```bash
# Tests unitaires
pytest

# Avec coverage
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_gateway.py -v
```

### **Types de tests**
- Tests d'authentification
- Tests de routage
- Tests de rate limiting
- Tests de santé des services
- Tests de sécurité

## 📈 Performance

### **Optimisations**
- Connexions HTTP persistantes
- Pool de connexions configuré
- Timeouts appropriés
- Retry avec backoff exponentiel

### **Benchmarks**
```bash
# Test de charge avec wrk
wrk -t12 -c400 -d30s http://localhost:8000/health

# Test avec Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health
```

## 🔄 Déploiement

### **Production**
```bash
# Variables d'environnement de production
ENVIRONMENT=production
JWT_SECRET_KEY=<strong-secret-key>
REDIS_URL=redis://redis-cluster:6379

# Démarrage avec Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Docker Swarm / Kubernetes**
Fichiers de configuration disponibles dans `/deploy/`

## 🐛 Dépannage

### **Problèmes courants**
1. **Service indisponible (503)** : Vérifier que les microservices sont démarrés
2. **Rate limit (429)** : Attendre ou augmenter les limites
3. **Token invalide (401)** : Vérifier la configuration JWT
4. **Accès refusé (403)** : Vérifier les rôles utilisateur

### **Logs**
```bash
# Logs en temps réel
docker-compose logs -f gateway-service

# Logs avec niveau de détail
LOG_LEVEL=DEBUG python run.py
```

## 📚 API Documentation

### **Documentation interactive**
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

### **Endpoints principaux**
- `GET /health` - Santé du service
- `GET /gateway/info` - Informations du gateway
- `GET /metrics` - Métriques Prometheus
- `ANY /{path:path}` - Proxy vers les services

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Ajouter des tests pour les nouvelles fonctionnalités
4. S'assurer que tous les tests passent
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

---

**PresencePro Gateway Service** - Point d'entrée sécurisé et intelligent pour l'écosystème PresencePro 🚀
