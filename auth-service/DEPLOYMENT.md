# 🚀 Guide de Déploiement - PresencePro Auth Service

## 📋 Options de Base de Données

### 🔧 Option 1 : SQLite (Développement Local)
```bash
# Utiliser la configuration actuelle
cp .env.example .env
# Modifier DATABASE_URL=sqlite:///./presencepro_auth.db

# Initialiser
python init_db.py
uvicorn app.main:app --reload --port 8001
```

### ☁️ Option 2 : Supabase (Production)

#### Étape 1 : Créer un projet Supabase
1. Allez sur [supabase.com](https://supabase.com)
2. Créez un nouveau projet
3. Notez votre **Project Reference** et **Database Password**

#### Étape 2 : Configuration automatique
```bash
python setup_supabase.py
# Suivez les instructions pour configurer Supabase
```

#### Étape 3 : Utiliser Supabase
```bash
# Copier la configuration de production
cp .env.production .env

# Initialiser la base de données
python init_db.py

# Lancer le service
uvicorn app.main:app --port 8001
```

## 🐳 Déploiement Docker

### Développement Local
```bash
# Avec SQLite
docker-compose up -d

# Logs
docker-compose logs -f auth-service
```

### Production avec Supabase
```bash
# Modifier docker-compose.yml avec vos variables Supabase
# Puis lancer
docker-compose -f docker-compose.prod.yml up -d
```

## 🌐 Déploiement Cloud

### Heroku
```bash
# Créer l'app
heroku create presencepro-auth

# Variables d'environnement
heroku config:set DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres"
heroku config:set SECRET_KEY="your-secret-key-32-chars-minimum"

# Déployer
git push heroku main
```

### Railway
```bash
# Connecter le repo
railway login
railway link

# Variables d'environnement
railway variables set DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres"
railway variables set SECRET_KEY="your-secret-key-32-chars-minimum"

# Déployer
railway up
```

### Render
1. Connectez votre repo GitHub
2. Configurez les variables d'environnement
3. Déployez automatiquement

## 🔐 Configuration de Sécurité

### Variables d'Environnement Requises
```bash
DATABASE_URL=postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres
SECRET_KEY=your-super-secret-key-minimum-32-characters-for-jwt-security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=False
```

### Sécurité en Production
1. **Changez le SECRET_KEY** (minimum 32 caractères)
2. **Utilisez HTTPS** uniquement
3. **Configurez CORS** pour votre domaine
4. **Activez les logs** de sécurité
5. **Limitez les tentatives** de connexion

## 📊 Monitoring et Logs

### Health Check
```bash
curl http://your-domain.com/health
```

### Logs Application
```bash
# Docker
docker-compose logs -f auth-service

# Heroku
heroku logs --tail -a presencepro-auth

# Railway
railway logs
```

### Métriques
- Endpoint `/health` pour les health checks
- Logs structurés avec uvicorn
- Monitoring des erreurs d'authentification

## 🧪 Tests en Production

### Test de Base
```bash
# Health check
curl https://your-domain.com/health

# Documentation API
curl https://your-domain.com/docs
```

### Test Complet
```bash
# Utiliser le script de démonstration
python demo_service.py demo
```

## 🔄 Migration de Données

### De SQLite vers Supabase
```bash
# Exporter les données SQLite
python export_data.py

# Importer vers Supabase
python import_to_supabase.py
```

### Sauvegarde Supabase
```bash
# Backup automatique via Supabase Dashboard
# Ou utiliser pg_dump
pg_dump "postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres" > backup.sql
```

## 🚨 Dépannage

### Erreurs Communes

#### Erreur de Connexion DB
```bash
# Vérifier les credentials
python -c "from app.database import engine; engine.connect()"
```

#### Erreur JWT
```bash
# Vérifier la longueur du SECRET_KEY (min 32 chars)
python -c "from app.config import settings; print(len(settings.secret_key))"
```

#### Erreur CORS
```bash
# Modifier app/main.py pour votre domaine
allow_origins=["https://your-frontend-domain.com"]
```

## 📞 Support

- **Documentation API** : `/docs`
- **Health Check** : `/health`
- **Logs** : Vérifiez les logs de votre plateforme
- **Issues** : Créez une issue dans le repo

## 🎯 Checklist de Déploiement

- [ ] Base de données configurée (SQLite/Supabase)
- [ ] Variables d'environnement définies
- [ ] SECRET_KEY changé (production)
- [ ] Tables créées (`python init_db.py`)
- [ ] Utilisateur admin créé
- [ ] Service démarré et accessible
- [ ] Health check fonctionnel
- [ ] Tests API passent
- [ ] HTTPS configuré (production)
- [ ] CORS configuré
- [ ] Monitoring activé
