#!/usr/bin/env python3
"""
Script de démarrage du Config Service
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.config_host,
        port=settings.config_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
        access_log=True
    )
