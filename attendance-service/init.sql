-- Script d'initialisation de la base de données PostgreSQL
-- pour le service de présences PresencePro

-- Créer la base de données si elle n'existe pas
-- (Cette commande sera exécutée automatiquement par Docker)

-- Créer des extensions utiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Créer un utilisateur spécifique pour l'application (optionnel)
-- CREATE USER presencepro_attendance WITH PASSWORD 'attendance_password';
-- GRANT ALL PRIVILEGES ON DATABASE presencepro_attendance TO presencepro_attendance;

-- Commentaires sur la base de données
COMMENT ON DATABASE presencepro_attendance IS 'Base de données pour le service de gestion des présences PresencePro';

-- Les tables seront créées automatiquement par SQLAlchemy/Alembic
