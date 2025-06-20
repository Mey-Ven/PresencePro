# PresencePro Admin Panel

## 📋 Description

Le **PresencePro Admin Panel** est une application frontend React.js moderne conçue pour l'administration du système de gestion des présences scolaires PresencePro. Cette interface permet aux administrateurs et enseignants de gérer efficacement les utilisateurs, les présences, les justifications et de consulter des statistiques détaillées.

## ✨ Fonctionnalités

### 🎯 **Tableau de bord**
- Vue d'ensemble des statistiques principales
- Graphiques interactifs (Chart.js)
- KPIs en temps réel
- Tendances et analyses

### 👥 **Gestion des utilisateurs**
- CRUD complet pour tous les types d'utilisateurs
- Gestion des rôles (Admin, Enseignant, Étudiant, Parent)
- Import/Export en masse
- Recherche et filtrage avancés

### 📅 **Gestion des présences**
- Consultation des registres de présence
- Marquage manuel des présences
- Filtrage par date, classe, statut
- Export des données

### 📄 **Gestion des justifications**
- Workflow de validation des absences
- Approbation/Rejet des demandes
- Gestion des documents joints
- Notifications automatiques

### 📊 **Statistiques et rapports**
- Graphiques dynamiques et interactifs
- Comparaisons par classe/étudiant
- Export multi-formats (PDF, Excel, CSV)
- Analyses de tendances

### ⚙️ **Paramètres système**
- Configuration de l'application
- Monitoring des microservices
- Gestion du profil utilisateur
- Informations système

## 🛠️ Technologies utilisées

### **Frontend**
- **React 18** avec TypeScript
- **React Router** pour la navigation
- **Bootstrap 5** + **React Bootstrap** pour l'UI
- **Chart.js** + **React Chart.js 2** pour les graphiques
- **Axios** pour les appels API
- **React Toastify** pour les notifications

### **Outils de développement**
- **Create React App** avec template TypeScript
- **ESLint** pour la qualité du code
- **CSS personnalisé** avec variables CSS
- **Font Awesome** pour les icônes

## 🚀 Installation et démarrage

### **Prérequis**
- Node.js 16+ et npm
- Les microservices PresencePro en cours d'exécution

### **Installation**
```bash
# Cloner le repository
git clone https://github.com/Mey-Ven/PresencePro.git
cd PresencePro/admin-panel-service

# Installer les dépendances
npm install

# Démarrer en mode développement
npm start
```

L'application sera accessible sur `http://localhost:3000`

### **Scripts disponibles**
```bash
npm start          # Démarrage en mode développement
npm run build      # Build de production
npm test           # Exécution des tests
npm run eject      # Éjection de la configuration CRA
```

## 🏗️ Architecture

### **Structure des dossiers**
```
src/
├── components/          # Composants réutilisables
│   ├── Auth/           # Authentification
│   ├── Layout/         # Layout principal
│   ├── Dashboard/      # Composants du tableau de bord
│   ├── Users/          # Gestion des utilisateurs
│   ├── Attendance/     # Gestion des présences
│   ├── Justifications/ # Gestion des justifications
│   ├── Statistics/     # Composants statistiques
│   └── Common/         # Composants communs
├── contexts/           # Contextes React
│   ├── AuthContext.tsx # Gestion de l'authentification
│   └── AppContext.tsx  # État global de l'application
├── hooks/              # Hooks personnalisés
├── pages/              # Pages principales
├── services/           # Services API
│   ├── api.ts          # Configuration Axios
│   ├── authService.ts  # Service d'authentification
│   ├── userService.ts  # Service utilisateurs
│   └── statisticsService.ts # Service statistiques
├── types/              # Types TypeScript
├── utils/              # Utilitaires
└── App.tsx            # Composant principal
```

### **Gestion d'état**
- **Context API** pour l'état global
- **useReducer** pour la logique complexe
- **localStorage** pour la persistance

### **Intégration API**
- Communication avec 9 microservices
- Gestion centralisée des erreurs
- Intercepteurs Axios pour l'authentification
- Retry automatique et cache

## 🔧 Configuration

### **Variables d'environnement**
Créer un fichier `.env` :
```env
REACT_APP_AUTH_SERVICE_URL=http://localhost:8001
REACT_APP_USER_SERVICE_URL=http://localhost:8002
REACT_APP_COURSE_SERVICE_URL=http://localhost:8003
REACT_APP_FACE_RECOGNITION_SERVICE_URL=http://localhost:8004
REACT_APP_ATTENDANCE_SERVICE_URL=http://localhost:8005
REACT_APP_JUSTIFICATION_SERVICE_URL=http://localhost:8006
REACT_APP_MESSAGING_SERVICE_URL=http://localhost:8007
REACT_APP_NOTIFICATION_SERVICE_URL=http://localhost:8008
REACT_APP_STATISTICS_SERVICE_URL=http://localhost:8009
```

### **Proxy de développement**
Le fichier `package.json` inclut un proxy vers `http://localhost:8001` pour le développement.

## 🎨 Interface utilisateur

### **Design System**
- **Couleurs principales** : Dégradé violet-bleu (#667eea → #764ba2)
- **Typographie** : Inter (Google Fonts)
- **Composants** : Bootstrap 5 avec personnalisations
- **Icônes** : Font Awesome 6
- **Responsive** : Mobile-first design

### **Thèmes**
- Mode clair (par défaut)
- Mode sombre (en développement)
- Personnalisation via CSS variables

## 🔐 Authentification

### **Système de rôles**
- **Admin** : Accès complet à toutes les fonctionnalités
- **Teacher** : Gestion des présences et consultation
- **Student** : Accès limité (futur)
- **Parent** : Consultation des enfants (futur)

### **Sécurité**
- JWT tokens avec refresh automatique
- Routes protégées par rôle
- Déconnexion automatique en cas d'expiration
- Validation côté client et serveur

## 📱 Responsive Design

L'application est entièrement responsive et optimisée pour :
- **Desktop** : Interface complète avec sidebar
- **Tablet** : Adaptation des composants
- **Mobile** : Sidebar collapsible, navigation optimisée

## 🧪 Tests

```bash
# Exécuter les tests
npm test

# Coverage des tests
npm run test:coverage
```

## 📦 Build et déploiement

### **Build de production**
```bash
npm run build
```

### **Déploiement**
- Build statique dans le dossier `build/`
- Compatible avec tous les serveurs web
- Optimisations automatiques (minification, tree-shaking)

## 🔄 Intégration avec les microservices

L'application communique avec 9 microservices :
1. **auth-service** (8001) - Authentification
2. **user-service** (8002) - Gestion des utilisateurs
3. **course-service** (8003) - Gestion des cours
4. **face-recognition-service** (8004) - Reconnaissance faciale
5. **attendance-service** (8005) - Gestion des présences
6. **justification-service** (8006) - Justifications d'absence
7. **messaging-service** (8007) - Messagerie
8. **notification-service** (8008) - Notifications
9. **statistics-service** (8009) - Statistiques et rapports

## 🐛 Dépannage

### **Problèmes courants**
1. **Erreur de proxy** : Vérifier que les microservices sont démarrés
2. **Erreur d'authentification** : Vider le localStorage et se reconnecter
3. **Erreur de build** : Supprimer `node_modules` et réinstaller

### **Logs et debugging**
- Console du navigateur pour les erreurs frontend
- Network tab pour les erreurs API
- React Developer Tools pour le debugging

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Mehdi Rahaoui** - Développeur PresencePro

---

**PresencePro Admin Panel** - Interface d'administration moderne pour la gestion des présences scolaires 🎓
