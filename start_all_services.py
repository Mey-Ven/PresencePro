#!/usr/bin/env python3
"""
Script pour démarrer tous les services PresencePro
"""
import subprocess
import time
import sys
import os
import signal
from pathlib import Path


class ServiceManager:
    """Gestionnaire des services PresencePro"""
    
    def __init__(self):
        self.services = [
            {
                "name": "auth-service",
                "port": 8001,
                "path": "auth-service",
                "process": None
            },
            {
                "name": "user-service",
                "port": 8002,
                "path": "user-service",
                "process": None
            },
            {
                "name": "course-service",
                "port": 8003,
                "path": "course-service",
                "process": None
            },
            {
                "name": "face-recognition-service",
                "port": 8004,
                "path": "face-recognition-service",
                "process": None
            },
            {
                "name": "attendance-service",
                "port": 8005,
                "path": "attendance-service",
                "process": None
            }
        ]
        self.running = False
    
    def check_dependencies(self):
        """Vérifier les dépendances"""
        print("🔍 Vérification des dépendances...")
        
        for service in self.services:
            service_path = Path(service["path"])
            if not service_path.exists():
                print(f"❌ Service {service['name']} non trouvé dans {service_path}")
                return False
            
            requirements_file = service_path / "requirements.txt"
            if not requirements_file.exists():
                print(f"❌ Fichier requirements.txt manquant pour {service['name']}")
                return False
            
            main_file = service_path / "app" / "main.py"
            if not main_file.exists():
                print(f"❌ Fichier main.py manquant pour {service['name']}")
                return False
        
        print("✅ Toutes les dépendances sont présentes")
        return True
    
    def install_dependencies(self):
        """Installer les dépendances pour tous les services"""
        print("📦 Installation des dépendances...")
        
        for service in self.services:
            print(f"\n📦 Installation pour {service['name']}...")
            try:
                result = subprocess.run(
                    ["pip", "install", "-r", "requirements.txt"],
                    cwd=service["path"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ Dépendances installées pour {service['name']}")
                else:
                    print(f"❌ Erreur installation {service['name']}: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Erreur lors de l'installation pour {service['name']}: {e}")
                return False
        
        return True
    
    def initialize_databases(self):
        """Initialiser les bases de données"""
        print("\n🗄️ Initialisation des bases de données...")
        
        for service in self.services:
            init_script = Path(service["path"]) / "init_db.py"
            if init_script.exists():
                print(f"\n🗄️ Initialisation de la base pour {service['name']}...")
                try:
                    result = subprocess.run(
                        ["python", "init_db.py"],
                        cwd=service["path"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"✅ Base de données initialisée pour {service['name']}")
                    else:
                        print(f"⚠️  Avertissement pour {service['name']}: {result.stderr}")
                except Exception as e:
                    print(f"❌ Erreur initialisation DB pour {service['name']}: {e}")
    
    def start_service(self, service):
        """Démarrer un service"""
        print(f"🚀 Démarrage de {service['name']} sur le port {service['port']}...")
        
        try:
            process = subprocess.Popen(
                ["uvicorn", "app.main:app", "--reload", "--port", str(service["port"])],
                cwd=service["path"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            service["process"] = process
            return True
        except Exception as e:
            print(f"❌ Erreur démarrage {service['name']}: {e}")
            return False
    
    def stop_service(self, service):
        """Arrêter un service"""
        if service["process"]:
            print(f"🛑 Arrêt de {service['name']}...")
            service["process"].terminate()
            try:
                service["process"].wait(timeout=5)
            except subprocess.TimeoutExpired:
                service["process"].kill()
            service["process"] = None
    
    def start_all(self):
        """Démarrer tous les services"""
        print("🚀 Démarrage de tous les services PresencePro")
        print("=" * 60)
        
        if not self.check_dependencies():
            return False
        
        # Installer les dépendances
        if not self.install_dependencies():
            return False
        
        # Initialiser les bases de données
        self.initialize_databases()
        
        # Démarrer les services
        print("\n🚀 Démarrage des services...")
        for service in self.services:
            if not self.start_service(service):
                self.stop_all()
                return False
            time.sleep(2)  # Attendre entre les démarrages
        
        self.running = True
        print("\n🎉 Tous les services sont démarrés !")
        print("\n📋 Services disponibles:")
        for service in self.services:
            print(f"   • {service['name']}: http://localhost:{service['port']}/docs")
        
        return True
    
    def stop_all(self):
        """Arrêter tous les services"""
        print("\n🛑 Arrêt de tous les services...")
        for service in self.services:
            self.stop_service(service)
        self.running = False
        print("✅ Tous les services sont arrêtés")
    
    def status(self):
        """Afficher le statut des services"""
        print("\n📊 Statut des services:")
        for service in self.services:
            if service["process"] and service["process"].poll() is None:
                print(f"   • {service['name']}: ✅ En cours (PID: {service['process'].pid})")
            else:
                print(f"   • {service['name']}: ❌ Arrêté")
    
    def wait_for_interrupt(self):
        """Attendre l'interruption utilisateur"""
        try:
            print("\n⌨️  Appuyez sur Ctrl+C pour arrêter tous les services...")
            while self.running:
                time.sleep(1)
                # Vérifier si les processus sont toujours en vie
                for service in self.services:
                    if service["process"] and service["process"].poll() is not None:
                        print(f"⚠️  {service['name']} s'est arrêté de manière inattendue")
                        self.running = False
                        break
        except KeyboardInterrupt:
            print("\n\n🛑 Interruption détectée...")
            self.stop_all()


def signal_handler(sig, frame):
    """Gestionnaire de signal pour arrêt propre"""
    print("\n🛑 Signal d'arrêt reçu...")
    sys.exit(0)


def main():
    """Fonction principale"""
    # Configurer le gestionnaire de signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager = ServiceManager()
    
    print("🎯 PresencePro Service Manager")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            if manager.start_all():
                manager.wait_for_interrupt()
        elif command == "stop":
            manager.stop_all()
        elif command == "status":
            manager.status()
        elif command == "install":
            manager.install_dependencies()
        elif command == "init-db":
            manager.initialize_databases()
        else:
            print("Commandes disponibles:")
            print("  start    - Démarrer tous les services")
            print("  stop     - Arrêter tous les services")
            print("  status   - Afficher le statut")
            print("  install  - Installer les dépendances")
            print("  init-db  - Initialiser les bases de données")
    else:
        # Mode interactif par défaut
        if manager.start_all():
            manager.wait_for_interrupt()


if __name__ == "__main__":
    main()
