-- Script d'initialisation de la base de données PostgreSQL
-- pour le Statistics Service de PresencePro

-- Créer les extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Créer un utilisateur spécifique pour l'application (optionnel)
-- CREATE USER statistics_user WITH PASSWORD 'statistics_password';
-- GRANT ALL PRIVILEGES ON DATABASE presencepro_statistics TO statistics_user;

-- Configuration de la base de données
SET timezone = 'Europe/Paris';
SET default_text_search_config = 'pg_catalog.french';

-- Commentaires sur la base de données
COMMENT ON DATABASE presencepro_statistics IS 'Base de données des statistiques PresencePro - Service d''analyse et de reporting';

-- Les tables seront créées automatiquement par SQLAlchemy
-- Ce script sert principalement à configurer l'environnement

-- Créer des index de performance supplémentaires après la création des tables
-- (Ces commandes seront exécutées par l'application au démarrage)

-- Fonction pour nettoyer les anciennes données
CREATE OR REPLACE FUNCTION cleanup_old_statistics()
RETURNS void AS $$
BEGIN
    -- Supprimer les statistiques en cache expirées
    DELETE FROM statistics_cache 
    WHERE expires_at < NOW();
    
    -- Supprimer les anciens rapports (plus de 6 mois)
    DELETE FROM statistics_reports 
    WHERE created_at < NOW() - INTERVAL '6 months';
    
    -- Log de l'opération
    RAISE NOTICE 'Nettoyage des anciennes statistiques effectué à %', NOW();
END;
$$ LANGUAGE plpgsql;

-- Programmer le nettoyage automatique (nécessite pg_cron extension)
-- SELECT cron.schedule('cleanup-stats', '0 2 * * *', 'SELECT cleanup_old_statistics();');

-- Fonction pour calculer les statistiques de performance
CREATE OR REPLACE FUNCTION get_database_performance_stats()
RETURNS TABLE(
    table_name text,
    row_count bigint,
    table_size text,
    index_size text,
    total_size text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname||'.'||tablename as table_name,
        n_tup_ins + n_tup_upd + n_tup_del as row_count,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
        pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) + pg_indexes_size(schemaname||'.'||tablename)) as total_size
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
END;
$$ LANGUAGE plpgsql;

-- Vue pour les statistiques de cache
CREATE OR REPLACE VIEW cache_statistics AS
SELECT 
    statistic_type,
    entity_type,
    COUNT(*) as cache_entries,
    AVG(hit_count) as avg_hit_count,
    MAX(created_at) as last_cached,
    COUNT(CASE WHEN expires_at > NOW() THEN 1 END) as active_entries,
    COUNT(CASE WHEN expires_at <= NOW() THEN 1 END) as expired_entries
FROM statistics_cache
GROUP BY statistic_type, entity_type;

-- Vue pour les statistiques de rapports
CREATE OR REPLACE VIEW report_statistics AS
SELECT 
    report_type,
    entity_type,
    status,
    COUNT(*) as report_count,
    AVG(generation_time_seconds) as avg_generation_time,
    AVG(file_size_bytes) as avg_file_size,
    MAX(created_at) as last_generated
FROM statistics_reports
GROUP BY report_type, entity_type, status;

-- Fonction pour obtenir un résumé des données
CREATE OR REPLACE FUNCTION get_data_summary()
RETURNS TABLE(
    metric text,
    value bigint,
    description text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'total_attendance_records'::text,
        COALESCE((SELECT COUNT(*) FROM attendance_records), 0),
        'Nombre total d''enregistrements de présence'::text
    UNION ALL
    SELECT 
        'unique_students'::text,
        COALESCE((SELECT COUNT(DISTINCT student_id) FROM attendance_records), 0),
        'Nombre d''étudiants uniques'::text
    UNION ALL
    SELECT 
        'unique_courses'::text,
        COALESCE((SELECT COUNT(DISTINCT course_id) FROM attendance_records), 0),
        'Nombre de cours uniques'::text
    UNION ALL
    SELECT 
        'unique_classes'::text,
        COALESCE((SELECT COUNT(DISTINCT class_id) FROM attendance_records), 0),
        'Nombre de classes uniques'::text
    UNION ALL
    SELECT 
        'cached_statistics'::text,
        COALESCE((SELECT COUNT(*) FROM statistics_cache WHERE expires_at > NOW()), 0),
        'Statistiques en cache actives'::text
    UNION ALL
    SELECT 
        'generated_reports'::text,
        COALESCE((SELECT COUNT(*) FROM statistics_reports WHERE status = 'completed'), 0),
        'Rapports générés avec succès'::text;
END;
$$ LANGUAGE plpgsql;

-- Configuration des paramètres de performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Recharger la configuration
SELECT pg_reload_conf();

-- Message de fin
DO $$
BEGIN
    RAISE NOTICE '✅ Base de données Statistics Service initialisée avec succès!';
    RAISE NOTICE '📊 Fonctions utilitaires créées:';
    RAISE NOTICE '   - cleanup_old_statistics(): Nettoie les anciennes données';
    RAISE NOTICE '   - get_database_performance_stats(): Statistiques de performance';
    RAISE NOTICE '   - get_data_summary(): Résumé des données';
    RAISE NOTICE '📈 Vues créées:';
    RAISE NOTICE '   - cache_statistics: Statistiques du cache';
    RAISE NOTICE '   - report_statistics: Statistiques des rapports';
    RAISE NOTICE '🎭 PresencePro Statistics Service - Prêt pour l''analyse!';
END $$;
