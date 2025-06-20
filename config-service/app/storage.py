"""
Gestionnaires de stockage pour les configurations
"""
import json
import os
import yaml
import aiofiles
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
import consul
import redis.asyncio as redis
import structlog
from datetime import datetime

from .config import settings
from .security import security_manager

logger = structlog.get_logger()


class ConfigStorage(ABC):
    """Interface abstraite pour le stockage des configurations"""
    
    @abstractmethod
    async def get_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Récupérer la configuration d'un service"""
        pass
    
    @abstractmethod
    async def set_config(self, service_name: str, config_data: Dict[str, Any]) -> bool:
        """Sauvegarder la configuration d'un service"""
        pass
    
    @abstractmethod
    async def delete_config(self, service_name: str) -> bool:
        """Supprimer la configuration d'un service"""
        pass
    
    @abstractmethod
    async def list_services(self) -> List[str]:
        """Lister tous les services avec des configurations"""
        pass
    
    @abstractmethod
    async def backup_config(self, service_name: str) -> bool:
        """Créer une sauvegarde de la configuration"""
        pass


class FileConfigStorage(ConfigStorage):
    """Stockage des configurations dans des fichiers"""
    
    def __init__(self):
        self.base_path = Path(settings.config_base_path)
        self.backup_path = Path(settings.backup_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Créer les répertoires nécessaires"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        if settings.enable_config_backup:
            self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def _get_config_file_path(self, service_name: str) -> Path:
        """Obtenir le chemin du fichier de configuration"""
        return self.base_path / f"{service_name}.json"
    
    def _get_backup_file_path(self, service_name: str) -> Path:
        """Obtenir le chemin du fichier de sauvegarde"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.backup_path / f"{service_name}_{timestamp}.json"
    
    async def get_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Récupérer la configuration d'un service depuis un fichier"""
        config_file = self._get_config_file_path(service_name)
        
        if not config_file.exists():
            # Retourner la configuration par défaut si le fichier n'existe pas
            default_configs = settings.default_service_configs
            if service_name in default_configs:
                logger.info(f"Using default config for {service_name}")
                return default_configs[service_name]
            return None
        
        try:
            async with aiofiles.open(config_file, 'r') as f:
                content = await f.read()
                config_data = json.loads(content)
                
                # Déchiffrer les données sensibles
                return security_manager.decrypt_config(config_data)
                
        except Exception as e:
            logger.error(f"Failed to read config for {service_name}", error=str(e))
            return None
    
    async def set_config(self, service_name: str, config_data: Dict[str, Any]) -> bool:
        """Sauvegarder la configuration d'un service dans un fichier"""
        try:
            # Créer une sauvegarde si activée
            if settings.enable_config_backup:
                await self.backup_config(service_name)
            
            # Chiffrer les données sensibles
            encrypted_config = security_manager.encrypt_config(config_data)
            
            # Ajouter des métadonnées
            encrypted_config['_metadata'] = {
                'service_name': service_name,
                'updated_at': datetime.utcnow().isoformat(),
                'version': encrypted_config.get('_metadata', {}).get('version', 1) + 1,
                'hash': security_manager.hash_data(json.dumps(config_data, sort_keys=True))
            }
            
            config_file = self._get_config_file_path(service_name)
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(encrypted_config, indent=2))
            
            logger.info(f"Config saved for {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config for {service_name}", error=str(e))
            return False
    
    async def delete_config(self, service_name: str) -> bool:
        """Supprimer la configuration d'un service"""
        try:
            # Créer une sauvegarde avant suppression
            if settings.enable_config_backup:
                await self.backup_config(service_name)
            
            config_file = self._get_config_file_path(service_name)
            if config_file.exists():
                config_file.unlink()
                logger.info(f"Config deleted for {service_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete config for {service_name}", error=str(e))
            return False
    
    async def list_services(self) -> List[str]:
        """Lister tous les services avec des configurations"""
        try:
            services = []
            for config_file in self.base_path.glob("*.json"):
                service_name = config_file.stem
                services.append(service_name)
            
            # Ajouter les services avec configurations par défaut
            for service in settings.supported_services:
                if service not in services:
                    services.append(service)
            
            return sorted(services)
            
        except Exception as e:
            logger.error("Failed to list services", error=str(e))
            return []
    
    async def backup_config(self, service_name: str) -> bool:
        """Créer une sauvegarde de la configuration"""
        if not settings.enable_config_backup:
            return True
        
        try:
            config_file = self._get_config_file_path(service_name)
            if not config_file.exists():
                return True
            
            backup_file = self._get_backup_file_path(service_name)
            
            async with aiofiles.open(config_file, 'r') as src:
                content = await src.read()
            
            async with aiofiles.open(backup_file, 'w') as dst:
                await dst.write(content)
            
            logger.info(f"Config backup created for {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup config for {service_name}", error=str(e))
            return False


class ConsulConfigStorage(ConfigStorage):
    """Stockage des configurations dans Consul"""
    
    def __init__(self):
        self.consul_client = consul.Consul(
            host=settings.consul_host,
            port=settings.consul_port,
            token=settings.consul_token
        )
        self.key_prefix = "presencepro/config/"
    
    def _get_consul_key(self, service_name: str) -> str:
        """Obtenir la clé Consul pour un service"""
        return f"{self.key_prefix}{service_name}"
    
    async def get_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Récupérer la configuration depuis Consul"""
        try:
            key = self._get_consul_key(service_name)
            index, data = self.consul_client.kv.get(key)
            
            if data is None:
                # Retourner la configuration par défaut
                default_configs = settings.default_service_configs
                if service_name in default_configs:
                    return default_configs[service_name]
                return None
            
            config_data = json.loads(data['Value'].decode())
            return security_manager.decrypt_config(config_data)
            
        except Exception as e:
            logger.error(f"Failed to get config from Consul for {service_name}", error=str(e))
            return None
    
    async def set_config(self, service_name: str, config_data: Dict[str, Any]) -> bool:
        """Sauvegarder la configuration dans Consul"""
        try:
            encrypted_config = security_manager.encrypt_config(config_data)
            key = self._get_consul_key(service_name)
            
            success = self.consul_client.kv.put(
                key, 
                json.dumps(encrypted_config)
            )
            
            if success:
                logger.info(f"Config saved to Consul for {service_name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to save config to Consul for {service_name}", error=str(e))
            return False
    
    async def delete_config(self, service_name: str) -> bool:
        """Supprimer la configuration de Consul"""
        try:
            key = self._get_consul_key(service_name)
            success = self.consul_client.kv.delete(key)
            
            if success:
                logger.info(f"Config deleted from Consul for {service_name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete config from Consul for {service_name}", error=str(e))
            return False
    
    async def list_services(self) -> List[str]:
        """Lister tous les services dans Consul"""
        try:
            index, keys = self.consul_client.kv.get(self.key_prefix, keys=True)
            
            if keys is None:
                return settings.supported_services
            
            services = []
            for key in keys:
                service_name = key.replace(self.key_prefix, '')
                services.append(service_name)
            
            return sorted(services)
            
        except Exception as e:
            logger.error("Failed to list services from Consul", error=str(e))
            return settings.supported_services
    
    async def backup_config(self, service_name: str) -> bool:
        """Consul gère ses propres sauvegardes"""
        return True


class RedisConfigStorage(ConfigStorage):
    """Stockage des configurations dans Redis"""
    
    def __init__(self):
        self.redis_client = None
        self.key_prefix = "presencepro:config:"
    
    async def _get_redis_client(self):
        """Obtenir le client Redis"""
        if self.redis_client is None:
            self.redis_client = redis.from_url(settings.redis_url)
        return self.redis_client
    
    def _get_redis_key(self, service_name: str) -> str:
        """Obtenir la clé Redis pour un service"""
        return f"{self.key_prefix}{service_name}"
    
    async def get_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Récupérer la configuration depuis Redis"""
        try:
            client = await self._get_redis_client()
            key = self._get_redis_key(service_name)
            data = await client.get(key)
            
            if data is None:
                # Retourner la configuration par défaut
                default_configs = settings.default_service_configs
                if service_name in default_configs:
                    return default_configs[service_name]
                return None
            
            config_data = json.loads(data)
            return security_manager.decrypt_config(config_data)
            
        except Exception as e:
            logger.error(f"Failed to get config from Redis for {service_name}", error=str(e))
            return None
    
    async def set_config(self, service_name: str, config_data: Dict[str, Any]) -> bool:
        """Sauvegarder la configuration dans Redis"""
        try:
            client = await self._get_redis_client()
            encrypted_config = security_manager.encrypt_config(config_data)
            key = self._get_redis_key(service_name)
            
            await client.set(key, json.dumps(encrypted_config))
            logger.info(f"Config saved to Redis for {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config to Redis for {service_name}", error=str(e))
            return False
    
    async def delete_config(self, service_name: str) -> bool:
        """Supprimer la configuration de Redis"""
        try:
            client = await self._get_redis_client()
            key = self._get_redis_key(service_name)
            result = await client.delete(key)
            
            if result:
                logger.info(f"Config deleted from Redis for {service_name}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to delete config from Redis for {service_name}", error=str(e))
            return False
    
    async def list_services(self) -> List[str]:
        """Lister tous les services dans Redis"""
        try:
            client = await self._get_redis_client()
            pattern = f"{self.key_prefix}*"
            keys = await client.keys(pattern)
            
            services = []
            for key in keys:
                service_name = key.decode().replace(self.key_prefix, '')
                services.append(service_name)
            
            # Ajouter les services par défaut
            for service in settings.supported_services:
                if service not in services:
                    services.append(service)
            
            return sorted(services)
            
        except Exception as e:
            logger.error("Failed to list services from Redis", error=str(e))
            return settings.supported_services
    
    async def backup_config(self, service_name: str) -> bool:
        """Redis peut utiliser ses mécanismes de persistance"""
        return True


def get_storage_backend() -> ConfigStorage:
    """Factory pour obtenir le backend de stockage approprié"""
    storage_type = settings.config_storage_type.lower()
    
    if storage_type == "consul":
        return ConsulConfigStorage()
    elif storage_type == "redis":
        return RedisConfigStorage()
    else:  # default to file
        return FileConfigStorage()


# Instance globale du backend de stockage
storage_backend = get_storage_backend()
