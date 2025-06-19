# 🎭 Face Recognition Service - PresencePro

Service de reconnaissance faciale en temps réel pour l'enregistrement automatique des présences dans le système PresencePro.

## 🚀 **Fonctionnalités**

### 🔍 **Reconnaissance Faciale**
- **Détection en temps réel** avec OpenCV et face_recognition
- **Encodage et stockage** des visages pour reconnaissance
- **Seuil de confiance configurable** pour la précision
- **Support multi-visages** dans une même image

### 📹 **Streaming Vidéo**
- **Stream en temps réel** depuis la webcam
- **Reconnaissance automatique** pendant le streaming
- **Annotations visuelles** des visages détectés
- **API REST** pour contrôler le streaming

### 🎯 **Intégration Système**
- **Enregistrement automatique** des présences
- **Intégration avec attendance-service** (à venir)
- **Logs détaillés** de toutes les reconnaissances
- **Statistiques** de performance

## 🏗️ **Architecture**

```
face-recognition-service/
├── app/
│   ├── core/              # Configuration et base de données
│   ├── models/            # Modèles SQLAlchemy et schémas Pydantic
│   ├── services/          # Logique métier
│   │   ├── face_recognition_service.py
│   │   ├── camera_service.py
│   │   └── attendance_integration.py
│   ├── routes/            # Endpoints API
│   │   ├── face_recognition.py
│   │   └── camera.py
│   └── main.py           # Application FastAPI
├── data/
│   ├── faces/            # Images de visages stockées
│   └── temp/             # Fichiers temporaires
├── tests/                # Tests unitaires
└── logs/                 # Fichiers de logs
```

## 📦 **Installation**

### **Prérequis**
- Python 3.8+
- Webcam connectée
- CMake (pour dlib)
- Visual Studio Build Tools (Windows) ou build-essential (Linux)

### **Installation des dépendances**
```bash
cd face-recognition-service
pip install -r requirements.txt
```

### **Initialisation**
```bash
python init_db.py
```

## 🚀 **Démarrage**

### **Mode Développement**
```bash
uvicorn app.main:app --reload --port 8004
```

### **Mode Production**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8004
```

### **Docker**
```bash
docker build -t presencepro/face-recognition-service .
docker run -p 8004:8004 --device=/dev/video0 presencepro/face-recognition-service
```

## 🔗 **API Endpoints**

### **🎭 Reconnaissance Faciale**

#### **POST** `/api/v1/face-recognition/detect`
Détecter et reconnaître les visages dans une image
```json
{
  "image_data": "base64_encoded_image",
  "camera_id": "default"
}
```

#### **POST** `/api/v1/face-recognition/train`
Entraîner le système avec de nouvelles images
```json
{
  "user_id": "user123",
  "name": "John Doe",
  "images": ["base64_image1", "base64_image2"]
}
```

#### **POST** `/api/v1/face-recognition/upload-face`
Upload d'image via formulaire multipart
- `user_id`: ID de l'utilisateur
- `name`: Nom de l'utilisateur
- `file`: Fichier image

#### **GET** `/api/v1/face-recognition/faces`
Lister les encodages de visages
- `user_id` (optionnel): Filtrer par utilisateur
- `active_only` (défaut: true): Seulement les actifs

#### **DELETE** `/api/v1/face-recognition/faces/{user_id}`
Supprimer tous les visages d'un utilisateur

#### **GET** `/api/v1/face-recognition/recognition-logs`
Récupérer les logs de reconnaissance
- `user_id` (optionnel): Filtrer par utilisateur
- `camera_id` (optionnel): Filtrer par caméra
- `limit` (défaut: 100): Nombre maximum de résultats

#### **GET** `/api/v1/face-recognition/stats`
Obtenir les statistiques de reconnaissance

### **📹 Caméra et Streaming**

#### **GET** `/api/v1/camera/status`
Obtenir le statut de la caméra

#### **POST** `/api/v1/camera/initialize`
Initialiser la caméra
```json
{
  "camera_index": 0
}
```

#### **GET** `/api/v1/camera/stream`
Stream vidéo en temps réel avec reconnaissance
- `with_recognition` (défaut: true): Activer la reconnaissance

#### **GET** `/api/v1/camera/capture`
Capturer une frame de la caméra

#### **POST** `/api/v1/camera/session/start`
Démarrer une session de caméra
```json
{
  "camera_id": "default"
}
```

#### **POST** `/api/v1/camera/session/stop`
Arrêter la session de caméra

### **🔧 Utilitaires**

#### **GET** `/health`
Vérification de santé du service

#### **GET** `/info`
Informations détaillées du service

#### **GET** `/test-camera`
Tester la caméra

## ⚙️ **Configuration**

### **Variables d'environnement (.env)**
```env
# Service
SERVICE_PORT=8004
DEBUG=True

# Caméra
CAMERA_INDEX=0
VIDEO_WIDTH=640
VIDEO_HEIGHT=480
VIDEO_FPS=30

# Reconnaissance
FACE_DETECTION_MODEL=hog
FACE_RECOGNITION_TOLERANCE=0.6
RECOGNITION_CONFIDENCE_THRESHOLD=0.7

# Intégration
AUTH_SERVICE_URL=http://localhost:8001
USER_SERVICE_URL=http://localhost:8002
ATTENDANCE_SERVICE_URL=http://localhost:8005
```

### **Modèles de détection**
- `hog`: Plus rapide, moins précis
- `cnn`: Plus lent, plus précis (nécessite GPU)

## 🧪 **Tests**

### **Tests automatisés**
```bash
python test_service.py
```

### **Tests unitaires**
```bash
pytest tests/ -v
```

### **Test manuel de la caméra**
```bash
curl http://localhost:8004/test-camera
```

## 📊 **Monitoring**

### **Métriques disponibles**
- Nombre total d'encodages
- Nombre de reconnaissances
- Taux de succès
- Sessions de caméra actives

### **Logs**
Les logs sont stockés dans `./logs/face_recognition.log`

## 🔗 **Intégration avec PresencePro**

### **Flux de reconnaissance automatique**
1. **Détection** de visage via webcam
2. **Reconnaissance** contre la base de données
3. **Enregistrement automatique** de la présence
4. **Notification** au système PresencePro

### **Services intégrés**
- **auth-service**: Authentification
- **user-service**: Informations utilisateurs
- **attendance-service**: Enregistrement présences

## 🐳 **Déploiement Docker**

### **Dockerfile**
```dockerfile
FROM python:3.9-slim
# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    cmake \
    libopencv-dev \
    python3-opencv
# ... (voir Dockerfile complet)
```

### **Docker Compose**
```yaml
services:
  face-recognition-service:
    build: .
    ports: ["8004:8004"]
    devices: ["/dev/video0:/dev/video0"]
    environment:
      - CAMERA_INDEX=0
```

## 🔧 **Dépannage**

### **Problèmes courants**

#### **Caméra non détectée**
- Vérifiez que la webcam est connectée
- Testez avec: `curl http://localhost:8004/test-camera`
- Changez l'index de caméra dans la configuration

#### **Erreur d'installation dlib**
```bash
# Ubuntu/Debian
sudo apt-get install cmake libopencv-dev

# macOS
brew install cmake

# Windows
# Installez Visual Studio Build Tools
```

#### **Performance lente**
- Réduisez la résolution vidéo
- Augmentez `FRAME_SKIP` dans la configuration
- Utilisez le modèle `hog` au lieu de `cnn`

## 📈 **Performance**

### **Optimisations**
- **Frame skipping**: Traite 1 frame sur N
- **Threading**: Reconnaissance en arrière-plan
- **Cache**: Résultats récents en mémoire
- **Résolution adaptative**: Ajustement automatique

### **Benchmarks typiques**
- **Détection**: ~50ms par frame (hog)
- **Reconnaissance**: ~100ms par visage
- **Streaming**: 15-30 FPS selon la configuration

## 🔒 **Sécurité**

### **Bonnes pratiques**
- Stockage sécurisé des encodages
- Logs d'accès détaillés
- Validation des entrées
- Rate limiting sur les APIs

## 📝 **Changelog**

### **v1.0.0**
- ✅ Reconnaissance faciale en temps réel
- ✅ Streaming vidéo avec annotations
- ✅ API REST complète
- ✅ Intégration PresencePro
- ✅ Documentation complète

## 🤝 **Contribution**

1. Fork le projet
2. Créez une branche feature
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 **Licence**

Ce projet fait partie de PresencePro - Système de gestion de présence scolaire.

---

**🎭 Face Recognition Service - Reconnaissance faciale intelligente pour PresencePro**
