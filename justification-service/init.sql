-- Script d'initialisation de la base de données PostgreSQL
-- pour le service de justifications PresencePro

-- Créer la base de données si elle n'existe pas
-- (Cette commande sera exécutée par docker-entrypoint-initdb.d)

-- Créer les extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Créer un utilisateur pour l'application (optionnel)
-- CREATE USER justification_user WITH PASSWORD 'justification_password';
-- GRANT ALL PRIVILEGES ON DATABASE presencepro_justifications TO justification_user;

-- Commentaires sur la base de données
COMMENT ON DATABASE presencepro_justifications IS 'Base de données pour le service de justifications PresencePro';

-- Les tables seront créées automatiquement par Alembic/SQLAlchemy
-- lors du démarrage de l'application
