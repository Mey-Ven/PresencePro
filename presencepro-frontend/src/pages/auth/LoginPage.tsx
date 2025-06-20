import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { AuthLayout } from '../../components/common/Layout';
import { ButtonSpinner } from '../../components/common/LoadingSpinner';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { authService } from '../../services/authService';

// Interface pour les données du formulaire
interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

// Page de connexion
const LoginPage: React.FC = () => {
  const { login, isAuthenticated, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // État du formulaire
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formErrors, setFormErrors] = useState<Partial<LoginFormData>>({});
  const [isDemoMode, setIsDemoMode] = useState<boolean | null>(null);

  // Rediriger si déjà connecté
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      const from = (location.state as any)?.from || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate, location]);

  // Détecter le mode démonstration
  useEffect(() => {
    const checkDemoMode = async () => {
      try {
        const demoMode = await authService.isDemoMode();
        setIsDemoMode(demoMode);
      } catch (error) {
        console.error('Erreur lors de la détection du mode:', error);
        setIsDemoMode(true); // Par défaut, mode démo
      }
    };

    checkDemoMode();
  }, []);

  // Nettoyer les erreurs au changement
  useEffect(() => {
    if (error) {
      clearError();
    }
  }, [formData.email, formData.password, error, clearError]);

  // Gérer les changements dans le formulaire
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Nettoyer l'erreur du champ modifié
    if (formErrors[name as keyof LoginFormData]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  // Valider le formulaire
  const validateForm = (): boolean => {
    const errors: Partial<LoginFormData> = {};

    if (!formData.email.trim()) {
      errors.email = 'L\'email est requis';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Format d\'email invalide';
    }

    if (!formData.password) {
      errors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 6) {
      errors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Gérer la soumission du formulaire
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await login({
        email: formData.email.trim(),
        password: formData.password,
      });

      // La redirection sera gérée par l'effet useEffect
    } catch (error: any) {
      console.error('Erreur de connexion:', error);
      // L'erreur sera affichée par le contexte d'authentification
    } finally {
      setIsSubmitting(false);
    }
  };

  // Gérer la connexion avec "Se souvenir de moi"
  useEffect(() => {
    // Charger les données sauvegardées si "Se souvenir de moi" était coché
    const savedEmail = localStorage.getItem('rememberedEmail');
    if (savedEmail) {
      setFormData(prev => ({
        ...prev,
        email: savedEmail,
        rememberMe: true,
      }));
    }
  }, []);

  // Sauvegarder l'email si "Se souvenir de moi" est coché
  useEffect(() => {
    if (formData.rememberMe && formData.email) {
      localStorage.setItem('rememberedEmail', formData.email);
    } else {
      localStorage.removeItem('rememberedEmail');
    }
  }, [formData.rememberMe, formData.email]);

  return (
    <AuthLayout>
      <div className="min-h-screen flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full">
          <div className="card p-8">
            {/* Logo et titre */}
            <div className="text-center mb-8">
              <div className="mx-auto w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Connexion à PresencePro
              </h2>
              <p className="text-gray-600">
                Connectez-vous avec vos identifiants
              </p>
            </div>

            <form className="space-y-6" onSubmit={handleSubmit}>
              {/* Champ Email moderne */}
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
                  Adresse email
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                    </svg>
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className={`input pl-10 ${formErrors.email ? 'border-red-300' : ''}`}
                    placeholder="votre@email.com"
                  />
                  {formErrors.email && (
                    <p className="mt-2 text-sm text-red-600">{formErrors.email}</p>
                  )}
                </div>
              </div>

              {/* Champ Mot de passe moderne */}
              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                  Mot de passe
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={formData.password}
                    onChange={handleInputChange}
                    className={`input pl-10 pr-12 ${formErrors.password ? 'border-red-300' : ''}`}
                    placeholder="Votre mot de passe"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-gray-600 transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                  {formErrors.password && (
                    <p className="mt-2 text-sm text-red-600">{formErrors.password}</p>
                  )}
                </div>
              </div>

              {/* Options modernes */}
              <div className="flex items-center">
                <div className="relative">
                  <input
                    id="rememberMe"
                    name="rememberMe"
                    type="checkbox"
                    checked={formData.rememberMe}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                  />
                </div>
                <label htmlFor="rememberMe" className="ml-3 block text-sm font-medium text-gray-700">
                  Se souvenir de moi
                </label>
              </div>

              {/* Bouton de soumission moderne */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting || isLoading}
                  className="btn-primary w-full py-3 text-base font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <ButtonSpinner className="mr-2" />
                      Connexion en cours...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                      </svg>
                      Se connecter
                    </>
                  )}
                </button>
              </div>


            </form>

            {/* Informations de démonstration */}
            <div className="mt-8 p-6 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 className="text-sm font-bold text-gray-900">
                    Comptes de démonstration
                  </h3>
                </div>
                {isDemoMode !== null && (
                  <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                    isDemoMode
                      ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                      : 'bg-green-100 text-green-800 border border-green-200'
                  }`}>
                    {isDemoMode ? '🟡 Mode Démo' : '🟢 Mode API'}
                  </span>
                )}
              </div>

              {isDemoMode === null ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                  <p className="text-sm text-gray-600">Détection du mode en cours...</p>
                </div>
              ) : isDemoMode ? (
                <div>
                  <p className="text-sm text-gray-700 mb-4 font-medium">
                    🔧 Backend non disponible - Utilisation des données de démonstration
                  </p>
                  <div className="grid grid-cols-1 gap-3">
                    {authService.getDemoUsers().map((user, index) => (
                      <div key={index} className="bg-white p-3 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-sm font-bold text-gray-900">
                              {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                            </span>
                            <p className="text-xs text-gray-600">{user.email}</p>
                          </div>
                          <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                            {user.password}
                          </code>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <p className="text-sm text-gray-700 font-medium mb-1">
                    Connecté au backend PresencePro
                  </p>
                  <p className="text-xs text-gray-500">
                    Utilisez vos identifiants réels pour vous connecter
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
};

export default LoginPage;
