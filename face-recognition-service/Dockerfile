# Face Recognition Service Dockerfile
FROM python:3.9-slim

# Métadonnées
LABEL maintainer="PresencePro Team"
LABEL description="Face Recognition Service for PresencePro"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    # Outils de build
    build-essential \
    cmake \
    pkg-config \
    # Bibliothèques OpenCV
    libopencv-dev \
    python3-opencv \
    # Bibliothèques pour dlib
    libatlas-base-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    # Utilitaires
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash facerecog
USER facerecog
WORKDIR /home/facerecog

# Copier les requirements et installer les dépendances Python
COPY --chown=facerecog:facerecog requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY --chown=facerecog:facerecog . .

# Créer les répertoires nécessaires
RUN mkdir -p data/faces data/temp logs

# Exposer le port
EXPOSE 8004

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# Commande par défaut
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
