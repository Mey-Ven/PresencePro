import React, { useState } from 'react';
import { authService } from '../services/authService';
import { mockAuthService } from '../services/mockAuthService';

const TestAuth: React.FC = () => {
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const testMockAuth = async () => {
    setLoading(true);
    setResult('');
    
    try {
      console.log('🧪 Test du service d\'authentification mocké...');
      
      // Test de connexion avec admin
      const credentials = {
        email: 'admin@presencepro.com',
        password: 'admin123'
      };
      
      console.log('📧 Tentative de connexion avec:', credentials);
      
      const authData = await mockAuthService.login(credentials);
      
      console.log('✅ Connexion réussie:', authData);
      
      setResult(`✅ Connexion réussie !
Utilisateur: ${authData.user.firstName} ${authData.user.lastName}
Email: ${authData.user.email}
Rôle: ${authData.user.role}
Token: ${authData.accessToken.substring(0, 20)}...`);
      
    } catch (error: any) {
      console.error('❌ Erreur de connexion:', error);
      setResult(`❌ Erreur: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testAuthService = async () => {
    setLoading(true);
    setResult('');
    
    try {
      console.log('🧪 Test du service d\'authentification principal...');
      
      // Test de connexion avec admin
      const credentials = {
        email: 'admin@presencepro.com',
        password: 'admin123'
      };
      
      console.log('📧 Tentative de connexion avec:', credentials);
      
      const authData = await authService.login(credentials);
      
      console.log('✅ Connexion réussie:', authData);
      
      setResult(`✅ Connexion réussie !
Utilisateur: ${authData.user.firstName} ${authData.user.lastName}
Email: ${authData.user.email}
Rôle: ${authData.user.role}
Token: ${authData.accessToken.substring(0, 20)}...`);
      
    } catch (error: any) {
      console.error('❌ Erreur de connexion:', error);
      setResult(`❌ Erreur: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testDemoUsers = () => {
    try {
      const demoUsers = authService.getDemoUsers();
      console.log('👥 Utilisateurs de démonstration:', demoUsers);
      
      setResult(`👥 Utilisateurs de démonstration:
${demoUsers.map(user => `${user.role}: ${user.email} / ${user.password}`).join('\n')}`);
    } catch (error: any) {
      console.error('❌ Erreur:', error);
      setResult(`❌ Erreur: ${error.message}`);
    }
  };

  const checkBackend = async () => {
    setLoading(true);
    setResult('');
    
    try {
      const isDemoMode = await authService.isDemoMode();
      setResult(`🔍 Mode détecté: ${isDemoMode ? 'DÉMONSTRATION' : 'API'}`);
    } catch (error: any) {
      console.error('❌ Erreur:', error);
      setResult(`❌ Erreur: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Test d'Authentification
        </h1>
        
        <div className="space-y-4">
          <button
            onClick={testMockAuth}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Test en cours...' : 'Tester Service Mocké'}
          </button>
          
          <button
            onClick={testAuthService}
            disabled={loading}
            className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? 'Test en cours...' : 'Tester Service Principal'}
          </button>
          
          <button
            onClick={testDemoUsers}
            disabled={loading}
            className="w-full bg-purple-600 text-white py-2 px-4 rounded hover:bg-purple-700 disabled:opacity-50"
          >
            Afficher Utilisateurs Démo
          </button>
          
          <button
            onClick={checkBackend}
            disabled={loading}
            className="w-full bg-yellow-600 text-white py-2 px-4 rounded hover:bg-yellow-700 disabled:opacity-50"
          >
            {loading ? 'Vérification...' : 'Vérifier Backend'}
          </button>
        </div>
        
        {result && (
          <div className="mt-6 p-4 bg-gray-50 rounded border">
            <h3 className="font-medium text-gray-900 mb-2">Résultat:</h3>
            <pre className="text-sm text-gray-700 whitespace-pre-wrap">{result}</pre>
          </div>
        )}
        
        <div className="mt-6 text-center">
          <a
            href="/"
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            ← Retour à l'application
          </a>
        </div>
      </div>
    </div>
  );
};

export default TestAuth;
