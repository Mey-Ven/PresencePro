import React, { createContext, useContext, useReducer, useEffect, useCallback, ReactNode } from 'react';
import { User, AuthState, LoginCredentials } from '../types';
import { authService, RegisterData } from '../services/authService';
import toast from 'react-hot-toast';

// Types pour les actions du reducer
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; accessToken: string; refreshToken: string } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'CLEAR_ERROR' };

// Interface pour le contexte
interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => Promise<void>;
  clearError: () => void;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
}

// État initial
const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Reducer pour gérer l'état d'authentification
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };

    case 'AUTH_LOGOUT':
      return {
        ...initialState,
        isLoading: false,
      };

    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
};

// Création du contexte
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Props pour le provider
interface AuthProviderProps {
  children: ReactNode;
}

// Provider du contexte d'authentification
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Fonction de déconnexion
  const logout = useCallback(async (): Promise<void> => {
    try {
      await authService.logout();
      dispatch({ type: 'AUTH_LOGOUT' });
      toast.success('Déconnexion réussie');
    } catch (error: any) {
      console.error('Erreur lors de la déconnexion:', error);
      // Même en cas d'erreur, on déconnecte localement
      dispatch({ type: 'AUTH_LOGOUT' });
      toast.error('Erreur lors de la déconnexion');
    }
  }, []);

  // Initialisation - Vérifier si l'utilisateur est déjà connecté
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          // Récupérer les informations utilisateur depuis le localStorage
          const user = authService.getCurrentUser();
          const accessToken = localStorage.getItem('accessToken');
          const refreshToken = localStorage.getItem('refreshToken');

          if (user && accessToken && refreshToken) {
            dispatch({
              type: 'AUTH_SUCCESS',
              payload: { user, accessToken, refreshToken },
            });

            // En mode démo, on ne vérifie pas le profil côté serveur
            // car le service mocké ne supporte pas getProfile()
            console.log('✅ Utilisateur connecté:', user.firstName, user.lastName);
          } else {
            dispatch({ type: 'AUTH_LOGOUT' });
          }
        } else {
          dispatch({ type: 'AUTH_LOGOUT' });
        }
      } catch (error) {
        console.error('Erreur lors de l\'initialisation de l\'authentification:', error);
        dispatch({ type: 'AUTH_LOGOUT' });
      }
    };

    initializeAuth();
  }, [logout]);

  // Fonction de connexion
  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      dispatch({ type: 'AUTH_START' });

      const authData = await authService.login(credentials);

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: authData.user,
          accessToken: authData.accessToken,
          refreshToken: authData.refreshToken,
        },
      });

      toast.success(`Bienvenue, ${authData.user.firstName} !`);
    } catch (error: any) {
      const errorMessage = error.message || 'Erreur de connexion';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    }
  };

  // Fonction d'inscription
  const register = async (userData: RegisterData): Promise<void> => {
    try {
      dispatch({ type: 'AUTH_START' });

      const authData = await authService.register(userData);

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: authData.user,
          accessToken: authData.accessToken,
          refreshToken: authData.refreshToken,
        },
      });

      toast.success(`Inscription réussie ! Bienvenue, ${authData.user.firstName} !`);
    } catch (error: any) {
      const errorMessage = error.message || 'Erreur d\'inscription';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    }
  };



  // Fonction de mise à jour du profil
  const updateProfile = async (userData: Partial<User>): Promise<void> => {
    try {
      const updatedUser = await authService.updateProfile(userData);
      dispatch({ type: 'UPDATE_USER', payload: updatedUser });
      toast.success('Profil mis à jour avec succès');
    } catch (error: any) {
      const errorMessage = error.message || 'Erreur de mise à jour du profil';
      toast.error(errorMessage);
      throw error;
    }
  };

  // Fonction pour effacer les erreurs
  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Fonction pour vérifier un rôle spécifique
  const hasRole = (role: string): boolean => {
    return state.user?.role === role;
  };

  // Fonction pour vérifier plusieurs rôles
  const hasAnyRole = (roles: string[]): boolean => {
    return state.user ? roles.includes(state.user.role) : false;
  };

  // Valeur du contexte
  const contextValue: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    clearError,
    hasRole,
    hasAnyRole,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook pour utiliser le contexte d'authentification
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  
  return context;
};

// Hook pour vérifier l'authentification
export const useRequireAuth = (redirectTo: string = '/login') => {
  const auth = useAuth();
  
  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      window.location.href = redirectTo;
    }
  }, [auth.isAuthenticated, auth.isLoading, redirectTo]);
  
  return auth;
};

// Hook pour vérifier les rôles
export const useRequireRole = (
  allowedRoles: string[],
  redirectTo: string = '/unauthorized'
) => {
  const auth = useAuth();
  
  useEffect(() => {
    if (!auth.isLoading && auth.isAuthenticated && !auth.hasAnyRole(allowedRoles)) {
      window.location.href = redirectTo;
    }
  }, [auth, allowedRoles, redirectTo]);
  
  return auth;
};

export default AuthContext;
