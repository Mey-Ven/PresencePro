# Guide de Déploiement - Service Utilisateur PresencePro

Ce guide détaille les étapes pour déployer le service utilisateur PresencePro en production.

## 🎯 Prérequis

### Environnement
- Python 3.12+
- PostgreSQL 15+ (recommandé) ou SQLite (développement)
- Service d'authentification PresencePro déployé
- Reverse proxy (Nginx recommandé)

### Dépendances
- FastAPI
- SQLAlchemy
- Alembic
- psycopg2-binary (pour PostgreSQL)

## 🚀 Déploiement avec Docker

### 1. Préparation

```bash
# Cloner le repository
git clone <repository-url>
cd user-service

# Créer le fichier .env de production
cp .env.example .env.production
```

### 2. Configuration Production

Éditer `.env.production` :

```env
# Database - PostgreSQL Production
DATABASE_URL=postgresql://username:password@db-host:5432/presencepro_users

# Service Configuration
SERVICE_NAME=user-service
SERVICE_VERSION=1.0.0
SERVICE_PORT=8002

# Security - IMPORTANT: Changer en production
SECRET_KEY=your-very-secure-secret-key-change-this
ALGORITHM=HS256

# External Services
AUTH_SERVICE_URL=https://auth.presencepro.com

# CORS - Ajuster selon vos domaines
CORS_ORIGINS=["https://app.presencepro.com", "https://admin.presencepro.com"]

# Logs
LOG_LEVEL=INFO
```

### 3. Build et Déploiement Docker

```bash
# Build de l'image
docker build -t presencepro/user-service:latest .

# Déploiement avec Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Docker Compose Production

Créer `docker-compose.prod.yml` :

```yaml
version: '3.8'

services:
  user-service:
    image: presencepro/user-service:latest
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - presencepro-network

networks:
  presencepro-network:
    external: true
```

## 🐧 Déploiement sur Serveur Linux

### 1. Installation des Dépendances

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip postgresql-client nginx

# CentOS/RHEL
sudo yum install python3.12 python3.12-venv python3-pip postgresql nginx
```

### 2. Configuration de l'Application

```bash
# Créer un utilisateur dédié
sudo useradd -m -s /bin/bash presencepro
sudo su - presencepro

# Cloner et configurer
git clone <repository-url> /home/presencepro/user-service
cd /home/presencepro/user-service

# Environnement virtuel
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec les bonnes valeurs

# Initialiser la base de données
python init_db.py
```

### 3. Service Systemd

Créer `/etc/systemd/system/presencepro-user.service` :

```ini
[Unit]
Description=PresencePro User Service
After=network.target postgresql.service

[Service]
Type=exec
User=presencepro
Group=presencepro
WorkingDirectory=/home/presencepro/user-service
Environment=PATH=/home/presencepro/user-service/venv/bin
ExecStart=/home/presencepro/user-service/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8002
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable presencepro-user
sudo systemctl start presencepro-user
sudo systemctl status presencepro-user
```

### 4. Configuration Nginx

Créer `/etc/nginx/sites-available/presencepro-user` :

```nginx
server {
    listen 80;
    server_name user-api.presencepro.com;

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8002/health;
        access_log off;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/presencepro-user /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL avec Let's Encrypt

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir le certificat
sudo certbot --nginx -d user-api.presencepro.com

# Vérifier le renouvellement automatique
sudo certbot renew --dry-run
```

## 🗄️ Configuration Base de Données

### PostgreSQL

```sql
-- Créer la base de données
CREATE DATABASE presencepro_users;
CREATE USER presencepro_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE presencepro_users TO presencepro_user;

-- Se connecter à la base
\c presencepro_users;
GRANT ALL ON SCHEMA public TO presencepro_user;
```

### Migrations

```bash
# Appliquer les migrations
cd /home/presencepro/user-service
source venv/bin/activate
alembic upgrade head
```

## 📊 Monitoring et Logs

### 1. Logs

```bash
# Logs du service
sudo journalctl -u presencepro-user -f

# Logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Monitoring

```bash
# Status du service
sudo systemctl status presencepro-user

# Health check
curl http://localhost:8002/health

# Métriques
curl http://localhost:8002/
```

### 3. Logrotate

Créer `/etc/logrotate.d/presencepro-user` :

```
/var/log/presencepro-user/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 presencepro presencepro
    postrotate
        systemctl reload presencepro-user
    endscript
}
```

## 🔒 Sécurité

### 1. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Bloquer l'accès direct au port 8002
sudo ufw deny 8002
```

### 2. Variables d'Environnement

- ✅ Utiliser des secrets forts pour `SECRET_KEY`
- ✅ Configurer `CORS_ORIGINS` strictement
- ✅ Utiliser HTTPS en production
- ✅ Limiter les permissions de la base de données

### 3. Backup

```bash
# Script de backup PostgreSQL
#!/bin/bash
BACKUP_DIR="/backup/presencepro"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U presencepro_user presencepro_users > $BACKUP_DIR/users_$DATE.sql
find $BACKUP_DIR -name "users_*.sql" -mtime +7 -delete
```

## 🔄 Mise à Jour

### 1. Déploiement Rolling

```bash
# Backup de la base de données
pg_dump presencepro_users > backup_$(date +%Y%m%d).sql

# Mise à jour du code
cd /home/presencepro/user-service
git pull origin main

# Mise à jour des dépendances
source venv/bin/activate
pip install -r requirements.txt

# Migrations
alembic upgrade head

# Redémarrage du service
sudo systemctl restart presencepro-user
```

### 2. Vérification

```bash
# Vérifier le service
sudo systemctl status presencepro-user
curl http://localhost:8002/health

# Vérifier les logs
sudo journalctl -u presencepro-user --since "5 minutes ago"
```

## 🚨 Dépannage

### Problèmes Courants

1. **Service ne démarre pas**
   ```bash
   sudo journalctl -u presencepro-user -n 50
   ```

2. **Erreur de base de données**
   ```bash
   # Vérifier la connexion
   psql -h localhost -U presencepro_user -d presencepro_users
   ```

3. **Erreur 502 Nginx**
   ```bash
   # Vérifier que le service écoute
   sudo netstat -tlnp | grep 8002
   ```

### Commandes Utiles

```bash
# Redémarrer tous les services
sudo systemctl restart presencepro-user nginx

# Vérifier les ports
sudo ss -tlnp | grep -E ':(80|443|8002)'

# Test de connectivité
curl -I http://localhost:8002/health
```

## 📋 Checklist de Déploiement

- [ ] Base de données configurée et accessible
- [ ] Variables d'environnement définies
- [ ] Service d'authentification accessible
- [ ] Migrations appliquées
- [ ] Service systemd configuré et démarré
- [ ] Nginx configuré avec SSL
- [ ] Firewall configuré
- [ ] Monitoring en place
- [ ] Backup configuré
- [ ] Tests de santé passants

## 📞 Support

En cas de problème :
1. Vérifier les logs du service
2. Tester les endpoints de santé
3. Valider la configuration réseau
4. Contacter l'équipe de développement

---

**Note** : Ce guide suppose un déploiement sur Ubuntu/Debian. Adaptez les commandes selon votre distribution Linux.
