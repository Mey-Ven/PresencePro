# Configuration SQLite - PresencePro User Service

Ce document décrit la configuration SQLite du service utilisateur PresencePro après le nettoyage complet des références Supabase.

## 🎯 Configuration Actuelle

### Base de Données
- **Type** : SQLite
- **Fichier** : `./presencepro_users.db`
- **URL de connexion** : `sqlite:///./presencepro_users.db`

### Avantages de SQLite
- ✅ **Simplicité** : Aucune installation de serveur requise
- ✅ **Performance** : Excellent pour le développement et les petites applications
- ✅ **Portabilité** : Base de données dans un seul fichier
- ✅ **Fiabilité** : Très stable et bien testé
- ✅ **Zéro configuration** : Fonctionne immédiatement

## 📁 Fichiers Modifiés

### Configuration
- `.env` : Configuré pour SQLite uniquement
- `alembic.ini` : URL SQLite définie

### Scripts
- `test_database.py` : Références Supabase supprimées, focus sur SQLite et PostgreSQL générique
- `init_db.py` : Fonctionne parfaitement avec SQLite

### Documentation
- `README.md` : Références Supabase supprimées
- `DEPLOYMENT.md` : Nettoyé des références Supabase
- `docker-compose.yml` : Configuration PostgreSQL générique

### Fichiers Supprimés
- `setup_postgresql.md` : Supprimé (spécifique à Supabase)

## 🚀 Utilisation

### Démarrage Rapide
```bash
# Initialiser la base de données
python init_db.py

# Lancer le service
uvicorn app.main:app --reload --port 8002

# Tester le service
python test_service.py
```

### Tests
```bash
# Test de connexion base de données
python test_database.py

# Tests unitaires
python -m pytest tests/ -v
```

## 🔄 Migration vers PostgreSQL (Optionnel)

Si vous souhaitez migrer vers PostgreSQL plus tard :

### 1. Installer PostgreSQL
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
```

### 2. Créer la base de données
```sql
CREATE DATABASE presencepro_users;
CREATE USER presencepro WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE presencepro_users TO presencepro;
```

### 3. Mettre à jour .env
```env
DATABASE_URL=postgresql://presencepro:your_password@localhost:5432/presencepro_users
```

### 4. Migrer les données
```bash
# Réinitialiser avec PostgreSQL
python init_db.py
```

## 📊 Données d'Exemple

Le service est livré avec des données d'exemple :

### Enseignants
- Marie Dupont (Mathématiques)
- Pierre Martin (Sciences)

### Étudiants
- Alice Johnson (6ème A)
- Bob Smith (6ème A)
- Charlie Brown (5ème B)

### Parents
- Robert Johnson (père d'Alice)
- Sarah Johnson (mère d'Alice)
- Michael Smith (père de Bob)

### Relations Parent-Élève
- Relations familiales configurées automatiquement

## 🔧 Maintenance

### Backup SQLite
```bash
# Copier le fichier de base de données
cp presencepro_users.db backup_$(date +%Y%m%d).db
```

### Réinitialisation
```bash
# Supprimer la base de données
rm presencepro_users.db

# Réinitialiser
python init_db.py
```

### Vérification de l'intégrité
```bash
# Tester la connexion
python test_database.py

# Vérifier le service
python test_service.py
```

## 🎉 État du Service

Le service utilisateur PresencePro est maintenant :

- ✅ **100% fonctionnel** avec SQLite
- ✅ **Nettoyé** de toutes les références Supabase
- ✅ **Prêt pour le développement** immédiat
- ✅ **Facilement migrable** vers PostgreSQL
- ✅ **Bien documenté** et testé

## 📝 Notes Importantes

1. **SQLite est parfait** pour le développement et les petites applications
2. **PostgreSQL recommandé** pour la production avec beaucoup d'utilisateurs
3. **Migration facile** : changez juste l'URL dans `.env`
4. **Pas de perte de fonctionnalités** : toutes les features fonctionnent avec SQLite

## 🔗 Liens Utiles

- **Documentation SQLite** : https://sqlite.org/docs.html
- **SQLAlchemy SQLite** : https://docs.sqlalchemy.org/en/20/dialects/sqlite.html
- **FastAPI Database** : https://fastapi.tiangolo.com/tutorial/sql-databases/

---

**Le service est prêt à être utilisé !** 🚀
