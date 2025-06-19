from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .routes import router
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Auth Service...")

    # Create database tables only if not in test mode
    import os
    if not os.getenv("TESTING"):
        Base.metadata.create_all(bind=engine)
        print("📊 Database tables created/verified")

    yield

    # Shutdown
    print("🛑 Shutting down Auth Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Authentication and Authorization Service for PresencePro",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1/auth", tags=["Authentication"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "PresencePro Auth Service",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "database": "connected",
        "timestamp": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
