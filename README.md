# PresencePro

Système de gestion de présence scolaire basé sur une architecture microservices avec FastAPI et SQLite.

## 🏗️ Architecture

PresencePro est construit avec une architecture microservices modulaire :

### Services Disponibles

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| **auth-service** | 8001 | Authentification et autorisation | ✅ Complet |
| **user-service** | 8002 | Gestion des utilisateurs (étudiants, enseignants, parents) | ✅ Complet |

### Services Prévus
- **attendance-service** : Gestion des présences
- **notification-service** : Notifications et alertes
- **report-service** : Rapports et statistiques
- **schedule-service** : Gestion des emplois du temps

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.12+
- FastAPI
- SQLite (inclus)

### Installation

1. **Cloner le repository**
```bash
git clone https://github.com/Mey-Ven/PresencePro.git
cd PresencePro
```

2. **Service d'authentification**
```bash
cd auth-service
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --port 8001
```

3. **Service utilisateur**
```bash
cd user-service
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --port 8002
```

### Accès aux Services

- **Auth Service** : http://localhost:8001/docs
- **User Service** : http://localhost:8002/docs

## 👥 Utilisateurs par Défaut

### Service d'Authentification
- **Admin** : `admin` / `admin123`
- **Enseignant** : `teacher1` / `teacher123`
- **Parent** : `parent1` / `parent123`
- **Étudiant** : `student1` / `student123`

### Données d'Exemple
Le système est livré avec des données d'exemple pour tester toutes les fonctionnalités.

## 🔐 Authentification

1. **Connexion** via `/login` sur le service d'authentification
2. **Récupération du token JWT**
3. **Utilisation du token** dans les headers : `Authorization: Bearer <token>`

## 📚 Documentation

### Services
- [Auth Service](./auth-service/README.md) - Documentation complète du service d'authentification
- [User Service](./user-service/README.md) - Documentation complète du service utilisateur

### Guides
- [Déploiement](./user-service/DEPLOYMENT.md) - Guide de déploiement en production
- [Configuration SQLite](./user-service/SQLITE_CONFIGURATION.md) - Configuration base de données

## 🧪 Tests

### Tests Automatisés
```bash
# Service d'authentification
cd auth-service
python -m pytest tests/ -v

# Service utilisateur
cd user-service
python -m pytest tests/ -v
```

### Tests Manuels
```bash
# Test des services
cd auth-service && python test_service.py
cd user-service && python test_service.py
```

## 🐳 Docker

### Déploiement avec Docker Compose
```bash
# Lancer tous les services
docker-compose up -d

# Logs
docker-compose logs -f
```

## 🔧 Configuration

### Variables d'Environnement

Chaque service utilise un fichier `.env` pour la configuration :

```env
# Base de données
DATABASE_URL=sqlite:///./database.db

# Sécurité
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Services
AUTH_SERVICE_URL=http://localhost:8001
```

## 📊 Fonctionnalités

### ✅ Implémentées
- **Authentification JWT** complète
- **Gestion des rôles** (Admin, Teacher, Parent, Student)
- **CRUD Utilisateurs** (Étudiants, Enseignants, Parents)
- **Relations Parent-Élève**
- **API REST** documentée
- **Tests unitaires** et d'intégration

### 🚧 En Développement
- Gestion des présences
- Notifications en temps réel
- Rapports et statistiques
- Interface web

## 🛠️ Technologies

- **Backend** : FastAPI, SQLAlchemy, Alembic
- **Base de données** : SQLite (dev), PostgreSQL (prod)
- **Authentification** : JWT, bcrypt
- **Tests** : pytest, httpx
- **Documentation** : Swagger/OpenAPI automatique
- **Déploiement** : Docker, Docker Compose

## 📈 Roadmap

### Phase 1 - Services de Base ✅
- [x] Service d'authentification
- [x] Service utilisateur
- [x] Documentation et tests

### Phase 2 - Fonctionnalités Métier 🚧
- [ ] Service de présence
- [ ] Service de notifications
- [ ] Service de rapports

### Phase 3 - Interface et Avancé 📋
- [ ] Interface web React
- [ ] API Gateway
- [ ] Monitoring et logs
- [ ] CI/CD

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

- **Issues** : https://github.com/Mey-Ven/PresencePro/issues
- **Discussions** : https://github.com/Mey-Ven/PresencePro/discussions

## 🎯 Objectifs du Projet

PresencePro vise à fournir une solution complète et moderne pour la gestion de présence scolaire avec :

- **Simplicité d'utilisation** pour tous les utilisateurs
- **Fiabilité** et performance
- **Extensibilité** via l'architecture microservices
- **Sécurité** avec authentification robuste
- **Facilité de déploiement** et maintenance

---

**Développé avec ❤️ pour l'éducation moderne**
