import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, AuthState, LoginCredentials, ApiError } from '../types';
import authService from '../services/authService';
import { toast } from 'react-toastify';

// Types pour les actions
type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE'; payload: ApiError }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'SET_LOADING'; payload: boolean };

// État initial
const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
};

// Reducer pour gérer l'état d'authentification
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
      };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    default:
      return state;
  }
};

// Interface du contexte
interface AuthContextType {
  state: AuthState;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
  checkAuth: () => Promise<void>;
  isAdmin: () => boolean;
  isTeacher: () => boolean;
  isStudent: () => boolean;
  isParent: () => boolean;
  hasRole: (role: string) => boolean;
}

// Création du contexte
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Hook pour utiliser le contexte
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
};

// Props du provider
interface AuthProviderProps {
  children: ReactNode;
}

// Provider du contexte d'authentification
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Vérifier l'authentification au chargement
  useEffect(() => {
    checkAuth();
  }, []);

  // Fonction de connexion
  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      dispatch({ type: 'LOGIN_START' });
      
      const response = await authService.login(credentials);
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: response.user,
          token: response.access_token,
        },
      });
      
      toast.success(`Bienvenue ${response.user.first_name} !`);
    } catch (error) {
      const apiError = error as ApiError;
      dispatch({ type: 'LOGIN_FAILURE', payload: apiError });
      toast.error(apiError.message || 'Erreur de connexion');
      throw error;
    }
  };

  // Fonction de déconnexion
  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
      dispatch({ type: 'LOGOUT' });
      toast.info('Vous avez été déconnecté');
    } catch (error) {
      // Même si l'API échoue, on déconnecte localement
      dispatch({ type: 'LOGOUT' });
      console.error('Erreur lors de la déconnexion:', error);
    }
  };

  // Fonction de mise à jour du profil utilisateur
  const updateUser = async (userData: Partial<User>): Promise<void> => {
    try {
      const updatedUser = await authService.updateProfile(userData);
      dispatch({ type: 'UPDATE_USER', payload: updatedUser });
      toast.success('Profil mis à jour avec succès');
    } catch (error) {
      const apiError = error as ApiError;
      toast.error(apiError.message || 'Erreur lors de la mise à jour du profil');
      throw error;
    }
  };

  // Vérifier l'authentification
  const checkAuth = async (): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      if (!authService.isAuthenticated()) {
        dispatch({ type: 'LOGOUT' });
        return;
      }

      // Vérifier la validité du token
      const user = await authService.verifyToken();
      const token = authService.getToken();
      
      if (user && token) {
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: { user, token },
        });
      } else {
        dispatch({ type: 'LOGOUT' });
      }
    } catch (error) {
      console.error('Erreur lors de la vérification de l\'authentification:', error);
      dispatch({ type: 'LOGOUT' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Fonctions utilitaires pour vérifier les rôles
  const isAdmin = (): boolean => {
    return state.user?.role === 'admin';
  };

  const isTeacher = (): boolean => {
    return state.user?.role === 'teacher';
  };

  const isStudent = (): boolean => {
    return state.user?.role === 'student';
  };

  const isParent = (): boolean => {
    return state.user?.role === 'parent';
  };

  const hasRole = (role: string): boolean => {
    return state.user?.role === role;
  };

  // Valeur du contexte
  const contextValue: AuthContextType = {
    state,
    login,
    logout,
    updateUser,
    checkAuth,
    isAdmin,
    isTeacher,
    isStudent,
    isParent,
    hasRole,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
