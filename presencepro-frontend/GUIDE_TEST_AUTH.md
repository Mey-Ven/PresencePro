# Guide de Test - Authentification PresencePro

## 🔧 **Corrections Apportées**

### ✅ **1. Problème de Redirection Corrigé**
- **Avant** : `DashboardRedirect` redirigait toujours vers `/login`
- **Après** : Redirection intelligente selon le rôle de l'utilisateur connecté
- **Ajout** : Gestion des états de chargement et d'authentification

### ✅ **2. Contexte d'Authentification Optimisé**
- **Supprimé** : Appel à `getProfile()` qui échouait en mode démo
- **Ajouté** : Logs de débogage pour suivre l'authentification
- **Amélioré** : Gestion des erreurs et fallback

### ✅ **3. Page de Test Ajoutée**
- **URL** : `http://localhost:3000/test-auth`
- **Fonctions** : Test des services d'authentification
- **Debug** : Vérification des utilisateurs de démonstration

## 🧪 **Tests à Effectuer**

### **Test 1 : Page de Test d'Authentification**
1. Aller sur `http://localhost:3000/test-auth`
2. Cliquer sur "Tester Service Principal"
3. Vérifier que la connexion fonctionne
4. Cliquer sur "Afficher Utilisateurs Démo"
5. Vérifier que les 4 comptes sont listés

### **Test 2 : Connexion Admin**
1. Aller sur `http://localhost:3000/login`
2. Saisir : `admin@presencepro.com` / `admin123`
3. Cliquer sur "Se connecter"
4. **Résultat attendu** : Redirection vers `/admin/dashboard`
5. **Vérifier** : Dashboard admin avec graphiques

### **Test 3 : Connexion Enseignant**
1. Se déconnecter (bouton en haut à droite)
2. Saisir : `teacher@presencepro.com` / `teacher123`
3. Cliquer sur "Se connecter"
4. **Résultat attendu** : Redirection vers `/teacher/dashboard`
5. **Vérifier** : Dashboard enseignant avec planning

### **Test 4 : Connexion Étudiant**
1. Se déconnecter
2. Saisir : `student@presencepro.com` / `student123`
3. Cliquer sur "Se connecter"
4. **Résultat attendu** : Redirection vers `/student/dashboard`
5. **Vérifier** : Dashboard étudiant avec historique

### **Test 5 : Connexion Parent**
1. Se déconnecter
2. Saisir : `parent@presencepro.com` / `parent123`
3. Cliquer sur "Se connecter"
4. **Résultat attendu** : Redirection vers `/parent/dashboard`
5. **Vérifier** : Dashboard parent avec enfants

### **Test 6 : Navigation et Déconnexion**
1. Connecté avec n'importe quel compte
2. Cliquer sur les liens de la sidebar
3. Vérifier que la navigation fonctionne
4. Cliquer sur "Déconnexion" dans le header
5. **Résultat attendu** : Retour à `/login`

## 🐛 **Débogage**

### **Console du Navigateur**
Ouvrir les outils de développement (F12) et vérifier :
- ✅ `⚠️ Backend non disponible - Mode démonstration activé`
- ✅ `✅ Utilisateur connecté: [Prénom] [Nom]`
- ❌ Aucune erreur rouge

### **LocalStorage**
Dans l'onglet Application > Local Storage :
- ✅ `accessToken` : Token JWT
- ✅ `refreshToken` : Token de rafraîchissement
- ✅ `user` : Objet utilisateur JSON

### **Logs de Débogage**
```javascript
// Dans la console du navigateur
console.log('Auth Service:', window.authService);
console.log('Demo Users:', window.authService?.getDemoUsers());
```

## 🔍 **Diagnostic des Problèmes**

### **Problème : "Erreur de connexion"**
**Causes possibles :**
1. Service d'authentification non initialisé
2. Données de démonstration corrompues
3. Erreur dans le service mocké

**Solutions :**
1. Vérifier la console pour les erreurs
2. Tester sur `/test-auth`
3. Vider le localStorage et recharger

### **Problème : Redirection infinie**
**Causes possibles :**
1. État d'authentification incohérent
2. Rôle utilisateur non reconnu
3. Routes mal configurées

**Solutions :**
1. Vider le localStorage
2. Vérifier l'objet utilisateur
3. Redémarrer l'application

### **Problème : Dashboard vide**
**Causes possibles :**
1. Composant non importé
2. Route mal configurée
3. Erreur de compilation

**Solutions :**
1. Vérifier les imports dans App.tsx
2. Vérifier la console pour les erreurs
3. Redémarrer le serveur de développement

## ✅ **Checklist de Validation**

- [ ] Page de test accessible (`/test-auth`)
- [ ] Service d'authentification fonctionne
- [ ] 4 comptes de démonstration disponibles
- [ ] Connexion admin → Dashboard admin
- [ ] Connexion teacher → Dashboard teacher
- [ ] Connexion student → Dashboard student
- [ ] Connexion parent → Dashboard parent
- [ ] Navigation sidebar fonctionnelle
- [ ] Déconnexion fonctionnelle
- [ ] Redirection automatique selon le rôle
- [ ] Aucune erreur dans la console

## 🎯 **Résultat Attendu**

Après ces corrections, l'authentification devrait être **entièrement fonctionnelle** avec :

1. **Mode démonstration** automatique (backend non disponible)
2. **4 comptes de test** opérationnels
3. **Redirection intelligente** selon le rôle
4. **Dashboards complets** pour chaque rôle
5. **Navigation fluide** entre les sections
6. **Déconnexion** propre

Si tous les tests passent, l'application PresencePro Frontend est **prête pour la production** ! 🚀
