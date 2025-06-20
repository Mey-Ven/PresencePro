import { api, tokenStorage } from '../config/api';
import { mockAuthService } from './mockAuthService';
import {
  User,
  LoginCredentials,
  AuthResponse,
  ApiResponse
} from '../types';

// Endpoints de l'API d'authentification
const AUTH_ENDPOINTS = {
  LOGIN: '/api/v1/auth/login',
  REGISTER: '/api/v1/auth/register',
  REFRESH: '/api/v1/auth/refresh',
  LOGOUT: '/api/v1/auth/logout',
  PROFILE: '/api/v1/auth/profile',
  CHANGE_PASSWORD: '/api/v1/auth/change-password',
  FORGOT_PASSWORD: '/api/v1/auth/forgot-password',
  RESET_PASSWORD: '/api/v1/auth/reset-password',
  VERIFY_EMAIL: '/api/v1/auth/verify-email',
} as const;

// Interface pour l'inscription
export interface RegisterData {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  role: 'student' | 'teacher' | 'parent';
  phone?: string;
  // Champs spécifiques selon le rôle
  studentId?: string;
  teacherId?: string;
  parentId?: string;
  department?: string;
  subjects?: string[];
  childrenIds?: string[];
}

// Interface pour le changement de mot de passe
export interface ChangePasswordData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

// Interface pour la réinitialisation de mot de passe
export interface ResetPasswordData {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

// Service d'authentification
class AuthService {
  private isBackendAvailable: boolean | null = null;

  /**
   * Vérifier si le backend est disponible
   */
  private async checkBackendAvailability(): Promise<boolean> {
    if (this.isBackendAvailable !== null) {
      return this.isBackendAvailable;
    }

    try {
      // Tentative de ping du backend avec un timeout court
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);

      await fetch(`${process.env.REACT_APP_API_URL}/health`, {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      this.isBackendAvailable = true;
      console.log('✅ Backend disponible - Mode API activé');
      return true;
    } catch (error) {
      this.isBackendAvailable = false;
      console.log('⚠️ Backend non disponible - Mode démonstration activé');
      return false;
    }
  }
  /**
   * Connexion utilisateur
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Vérifier si le backend est disponible
    const backendAvailable = await this.checkBackendAvailability();

    if (!backendAvailable) {
      // Utiliser le service mocké
      const authData = await mockAuthService.login(credentials);

      // Sauvegarder les tokens et les informations utilisateur
      tokenStorage.setTokens(authData.accessToken, authData.refreshToken);
      localStorage.setItem('user', JSON.stringify(authData.user));

      return authData;
    }

    try {
      const response = await api.post<ApiResponse<AuthResponse>>(
        AUTH_ENDPOINTS.LOGIN,
        credentials
      );

      if (response.data.success && response.data.data) {
        const authData = response.data.data;

        // Sauvegarder les tokens et les informations utilisateur
        tokenStorage.setTokens(authData.accessToken, authData.refreshToken);
        localStorage.setItem('user', JSON.stringify(authData.user));

        return authData;
      } else {
        throw new Error(response.data.message || 'Erreur de connexion');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message ||
        error.message ||
        'Erreur de connexion'
      );
    }
  }

  /**
   * Inscription utilisateur
   */
  async register(userData: RegisterData): Promise<AuthResponse> {
    try {
      const response = await api.post<ApiResponse<AuthResponse>>(
        AUTH_ENDPOINTS.REGISTER,
        userData
      );

      if (response.data.success && response.data.data) {
        const authData = response.data.data;
        
        // Sauvegarder les tokens et les informations utilisateur
        tokenStorage.setTokens(authData.accessToken, authData.refreshToken);
        localStorage.setItem('user', JSON.stringify(authData.user));
        
        return authData;
      } else {
        throw new Error(response.data.message || 'Erreur d\'inscription');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Erreur d\'inscription'
      );
    }
  }

  /**
   * Déconnexion utilisateur
   */
  async logout(): Promise<void> {
    const backendAvailable = await this.checkBackendAvailability();

    if (!backendAvailable) {
      // Utiliser le service mocké
      await mockAuthService.logout();
      return;
    }

    try {
      const refreshToken = tokenStorage.getRefreshToken();

      if (refreshToken) {
        await api.post(AUTH_ENDPOINTS.LOGOUT, { refreshToken });
      }
    } catch (error) {
      // Ignorer les erreurs de déconnexion côté serveur
      console.warn('Erreur lors de la déconnexion côté serveur:', error);
    } finally {
      // Toujours nettoyer les données locales
      tokenStorage.clearTokens();
    }
  }

  /**
   * Rafraîchir le token d'accès
   */
  async refreshToken(): Promise<AuthResponse> {
    try {
      const refreshToken = tokenStorage.getRefreshToken();
      
      if (!refreshToken) {
        throw new Error('Aucun token de rafraîchissement disponible');
      }

      const response = await api.post<ApiResponse<AuthResponse>>(
        AUTH_ENDPOINTS.REFRESH,
        { refreshToken }
      );

      if (response.data.success && response.data.data) {
        const authData = response.data.data;
        
        // Mettre à jour les tokens
        tokenStorage.setTokens(authData.accessToken, authData.refreshToken);
        localStorage.setItem('user', JSON.stringify(authData.user));
        
        return authData;
      } else {
        throw new Error(response.data.message || 'Erreur de rafraîchissement');
      }
    } catch (error: any) {
      // En cas d'erreur, nettoyer les tokens
      tokenStorage.clearTokens();
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Erreur de rafraîchissement du token'
      );
    }
  }

  /**
   * Obtenir le profil utilisateur actuel
   */
  async getProfile(): Promise<User> {
    try {
      const response = await api.get<ApiResponse<User>>(AUTH_ENDPOINTS.PROFILE);

      if (response.data.success && response.data.data) {
        const user = response.data.data;
        
        // Mettre à jour les informations utilisateur en local
        localStorage.setItem('user', JSON.stringify(user));
        
        return user;
      } else {
        throw new Error(response.data.message || 'Erreur de récupération du profil');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Erreur de récupération du profil'
      );
    }
  }

  /**
   * Mettre à jour le profil utilisateur
   */
  async updateProfile(userData: Partial<User>): Promise<User> {
    try {
      const response = await api.put<ApiResponse<User>>(
        AUTH_ENDPOINTS.PROFILE,
        userData
      );

      if (response.data.success && response.data.data) {
        const user = response.data.data;
        
        // Mettre à jour les informations utilisateur en local
        localStorage.setItem('user', JSON.stringify(user));
        
        return user;
      } else {
        throw new Error(response.data.message || 'Erreur de mise à jour du profil');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Erreur de mise à jour du profil'
      );
    }
  }

  /**
   * Changer le mot de passe
   */
  async changePassword(passwordData: ChangePasswordData): Promise<void> {
    try {
      const response = await api.post<ApiResponse<void>>(
        AUTH_ENDPOINTS.CHANGE_PASSWORD,
        passwordData
      );

      if (!response.data.success) {
        throw new Error(response.data.message || 'Erreur de changement de mot de passe');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Erreur de changement de mot de passe'
      );
    }
  }

  /**
   * Demander une réinitialisation de mot de passe
   */
  async forgotPassword(email: string): Promise<void> {
    try {
      const response = await api.post<ApiResponse<void>>(
        AUTH_ENDPOINTS.FORGOT_PASSWORD,
        { email }
      );

      if (!response.data.success) {
        throw new Error(response.data.message || 'Erreur de demande de réinitialisation');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Erreur de demande de réinitialisation'
      );
    }
  }

  /**
   * Réinitialiser le mot de passe
   */
  async resetPassword(resetData: ResetPasswordData): Promise<void> {
    try {
      const response = await api.post<ApiResponse<void>>(
        AUTH_ENDPOINTS.RESET_PASSWORD,
        resetData
      );

      if (!response.data.success) {
        throw new Error(response.data.message || 'Erreur de réinitialisation');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Erreur de réinitialisation du mot de passe'
      );
    }
  }

  /**
   * Vérifier l'email
   */
  async verifyEmail(token: string): Promise<void> {
    try {
      const response = await api.post<ApiResponse<void>>(
        AUTH_ENDPOINTS.VERIFY_EMAIL,
        { token }
      );

      if (!response.data.success) {
        throw new Error(response.data.message || 'Erreur de vérification d\'email');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Erreur de vérification d\'email'
      );
    }
  }

  /**
   * Vérifier si l'utilisateur est connecté
   */
  isAuthenticated(): boolean {
    const token = tokenStorage.getAccessToken();
    const user = this.getCurrentUser();
    return !!(token && user);
  }

  /**
   * Obtenir l'utilisateur actuel depuis le localStorage
   */
  getCurrentUser(): User | null {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'utilisateur:', error);
      return null;
    }
  }

  /**
   * Obtenir le rôle de l'utilisateur actuel
   */
  getCurrentUserRole(): string | null {
    const user = this.getCurrentUser();
    return user?.role || null;
  }

  /**
   * Vérifier si l'utilisateur a un rôle spécifique
   */
  hasRole(role: string): boolean {
    const userRole = this.getCurrentUserRole();
    return userRole === role;
  }

  /**
   * Vérifier si l'utilisateur a l'un des rôles spécifiés
   */
  hasAnyRole(roles: string[]): boolean {
    const userRole = this.getCurrentUserRole();
    return userRole ? roles.includes(userRole) : false;
  }

  /**
   * Obtenir les utilisateurs de démonstration
   */
  getDemoUsers() {
    return mockAuthService.getDemoUsers();
  }

  /**
   * Vérifier si l'application est en mode démonstration
   */
  async isDemoMode(): Promise<boolean> {
    return !(await this.checkBackendAvailability());
  }
}

// Export de l'instance du service
export const authService = new AuthService();
export default authService;
