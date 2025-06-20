# Dockerfile pour le messaging-service
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="PresencePro Team"
LABEL description="Service de messagerie en temps réel pour PresencePro"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Créer un utilisateur non-root
RUN groupadd -r messaging && useradd -r -g messaging messaging

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app/ ./app/
COPY init_db.py .
COPY test_service.py .

# Créer les répertoires nécessaires
RUN mkdir -p logs uploads && \
    chown -R messaging:messaging /app

# Changer vers l'utilisateur non-root
USER messaging

# Exposer le port
EXPOSE 8007

# Commande de santé
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8007/health', timeout=5)" || exit 1

# Commande par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
