#!/usr/bin/env python3
"""
Script de démarrage du Gateway Service
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.gateway_host,
        port=settings.gateway_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
        access_log=True
    )
