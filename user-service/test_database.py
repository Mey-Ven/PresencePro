"""
Script pour tester la connexion à différentes bases de données
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import psycopg2
from urllib.parse import urlparse


def test_sqlite_connection():
    """Test de connexion SQLite"""
    print("🔍 Test de connexion SQLite...")
    try:
        db_url = "sqlite:///./test_connection.db"
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ SQLite : Connexion réussie")
            return True
    except Exception as e:
        print(f"❌ SQLite : Erreur - {e}")
        return False
    finally:
        # Nettoyer le fichier de test
        if os.path.exists("test_connection.db"):
            os.remove("test_connection.db")


def test_postgresql_connection(db_url):
    """Test de connexion PostgreSQL"""
    print(f"🔍 Test de connexion PostgreSQL...")
    print(f"   URL: {db_url}")
    
    try:
        # Parser l'URL pour extraire les composants
        parsed = urlparse(db_url)
        host = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path[1:]  # Enlever le '/' initial
        username = parsed.username
        password = parsed.password
        
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Database: {database}")
        print(f"   User: {username}")
        
        # Test avec psycopg2 directement
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL : Connexion réussie")
        print(f"   Version: {version[0]}")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL : Erreur de connexion - {e}")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL : Erreur inattendue - {e}")
        return False


def test_sqlalchemy_connection(db_url):
    """Test de connexion avec SQLAlchemy"""
    print(f"🔍 Test SQLAlchemy...")
    try:
        engine = create_engine(db_url, connect_args={"connect_timeout": 10})
        
        with engine.connect() as conn:
            if "sqlite" in db_url:
                result = conn.execute(text("SELECT sqlite_version()"))
            else:
                result = conn.execute(text("SELECT version()"))
            
            version = result.fetchone()
            print("✅ SQLAlchemy : Connexion réussie")
            print(f"   Version: {version[0]}")
            return True
            
    except OperationalError as e:
        print(f"❌ SQLAlchemy : Erreur - {e}")
        return False
    except Exception as e:
        print(f"❌ SQLAlchemy : Erreur inattendue - {e}")
        return False


def test_postgresql_urls():
    """Test de différentes URLs PostgreSQL"""
    print("🔍 Test de différentes configurations PostgreSQL...")

    # URLs à tester
    postgresql_urls = [
        # PostgreSQL local standard
        "postgresql://postgres:password@localhost:5432/postgres",

        # PostgreSQL avec base de données spécifique
        "postgresql://postgres:password@localhost:5432/presencepro_users",

        # PostgreSQL avec utilisateur spécifique
        "postgresql://presencepro:presencepro123@localhost:5432/presencepro_users",
    ]

    for i, url in enumerate(postgresql_urls, 1):
        print(f"\n--- Test URL PostgreSQL #{i} ---")
        if test_postgresql_connection(url):
            print(f"🎉 URL #{i} fonctionne !")
            return url
        else:
            print(f"❌ URL #{i} ne fonctionne pas")

    return None


def main():
    """Fonction principale de test"""
    print("🧪 Test de Connexions Base de Données - PresencePro User Service")
    print("=" * 70)
    
    # Test SQLite
    print("\n1. Test SQLite (local)")
    print("-" * 30)
    sqlite_ok = test_sqlite_connection()
    
    # Test PostgreSQL local (si disponible)
    print("\n2. Test PostgreSQL Local")
    print("-" * 30)
    local_pg_url = "postgresql://postgres:password@localhost:5432/postgres"
    local_pg_ok = test_postgresql_connection(local_pg_url)
    
    # Test PostgreSQL
    print("\n3. Test PostgreSQL")
    print("-" * 30)
    working_postgresql_url = test_postgresql_urls()

    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)

    print(f"SQLite Local:      {'✅ OK' if sqlite_ok else '❌ ERREUR'}")
    print(f"PostgreSQL Local:  {'✅ OK' if local_pg_ok else '❌ ERREUR'}")
    print(f"PostgreSQL URLs:   {'✅ OK' if working_postgresql_url else '❌ ERREUR'}")

    if working_postgresql_url:
        print(f"\n🎉 URL PostgreSQL fonctionnelle trouvée:")
        print(f"   {working_postgresql_url}")
        print("\n📝 Pour utiliser PostgreSQL, mettez à jour votre .env:")
        print(f"   DATABASE_URL={working_postgresql_url}")

    # Recommandations
    print("\n💡 RECOMMANDATIONS")
    print("-" * 30)

    if working_postgresql_url:
        print("✅ Utilisez PostgreSQL pour la production")
        print("✅ Gardez SQLite pour le développement local")
    elif local_pg_ok:
        print("✅ Utilisez PostgreSQL local pour le développement")
        print("⚠️  Configurez PostgreSQL pour la production")
    elif sqlite_ok:
        print("✅ Utilisez SQLite pour le développement")
        print("⚠️  Configurez PostgreSQL pour la production")
    else:
        print("❌ Aucune base de données fonctionnelle trouvée")
        print("🔧 Vérifiez votre configuration")


if __name__ == "__main__":
    main()
