import { authApi, apiCall } from './api';
import { User, LoginCredentials, ApiResponse } from '../types';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'teacher' | 'student' | 'parent';
}

class AuthService {
  // Connexion utilisateur
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await apiCall(() =>
      authApi.post<LoginResponse>('/api/v1/auth/login', credentials)
    );
    
    // Stocker le token et les données utilisateur
    localStorage.setItem('auth_token', response.access_token);
    localStorage.setItem('user_data', JSON.stringify(response.user));
    
    return response;
  }

  // Déconnexion utilisateur
  async logout(): Promise<void> {
    try {
      await apiCall(() => authApi.post('/api/v1/auth/logout'));
    } catch (error) {
      // Même si l'API échoue, on nettoie le localStorage
      console.warn('Erreur lors de la déconnexion:', error);
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    }
  }

  // Inscription d'un nouvel utilisateur
  async register(userData: RegisterData): Promise<User> {
    return await apiCall(() =>
      authApi.post<User>('/api/v1/auth/register', userData)
    );
  }

  // Vérification du token actuel
  async verifyToken(): Promise<User> {
    return await apiCall(() =>
      authApi.get<User>('/api/v1/auth/me')
    );
  }

  // Rafraîchissement du token
  async refreshToken(): Promise<LoginResponse> {
    const response = await apiCall(() =>
      authApi.post<LoginResponse>('/api/v1/auth/refresh')
    );
    
    localStorage.setItem('auth_token', response.access_token);
    localStorage.setItem('user_data', JSON.stringify(response.user));
    
    return response;
  }

  // Changement de mot de passe
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiCall(() =>
      authApi.post('/api/v1/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      })
    );
  }

  // Demande de réinitialisation de mot de passe
  async requestPasswordReset(email: string): Promise<void> {
    await apiCall(() =>
      authApi.post('/api/v1/auth/password-reset-request', { email })
    );
  }

  // Réinitialisation de mot de passe avec token
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiCall(() =>
      authApi.post('/api/v1/auth/password-reset', {
        token,
        new_password: newPassword,
      })
    );
  }

  // Vérification des permissions
  async checkPermission(permission: string): Promise<boolean> {
    try {
      const response = await apiCall(() =>
        authApi.get<{ has_permission: boolean }>(`/api/v1/auth/permissions/${permission}`)
      );
      return response.has_permission;
    } catch (error) {
      return false;
    }
  }

  // Obtenir les rôles disponibles
  async getRoles(): Promise<string[]> {
    return await apiCall(() =>
      authApi.get<string[]>('/api/v1/auth/roles')
    );
  }

  // Obtenir les permissions d'un rôle
  async getRolePermissions(role: string): Promise<string[]> {
    return await apiCall(() =>
      authApi.get<string[]>(`/api/v1/auth/roles/${role}/permissions`)
    );
  }

  // Vérifier si l'utilisateur est connecté
  isAuthenticated(): boolean {
    const token = localStorage.getItem('auth_token');
    const userData = localStorage.getItem('user_data');
    return !!(token && userData);
  }

  // Obtenir l'utilisateur actuel depuis le localStorage
  getCurrentUser(): User | null {
    const userData = localStorage.getItem('user_data');
    if (userData) {
      try {
        return JSON.parse(userData);
      } catch (error) {
        console.error('Erreur lors du parsing des données utilisateur:', error);
        return null;
      }
    }
    return null;
  }

  // Obtenir le token actuel
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  // Vérifier si l'utilisateur a un rôle spécifique
  hasRole(role: string): boolean {
    const user = this.getCurrentUser();
    return user?.role === role;
  }

  // Vérifier si l'utilisateur est admin
  isAdmin(): boolean {
    return this.hasRole('admin');
  }

  // Vérifier si l'utilisateur est enseignant
  isTeacher(): boolean {
    return this.hasRole('teacher');
  }

  // Vérifier si l'utilisateur est étudiant
  isStudent(): boolean {
    return this.hasRole('student');
  }

  // Vérifier si l'utilisateur est parent
  isParent(): boolean {
    return this.hasRole('parent');
  }

  // Mise à jour du profil utilisateur
  async updateProfile(profileData: Partial<User>): Promise<User> {
    const response = await apiCall(() =>
      authApi.put<User>('/api/v1/auth/profile', profileData)
    );
    
    // Mettre à jour les données dans le localStorage
    localStorage.setItem('user_data', JSON.stringify(response));
    
    return response;
  }

  // Activation/désactivation de l'authentification à deux facteurs
  async enable2FA(): Promise<{ qr_code: string; secret: string }> {
    return await apiCall(() =>
      authApi.post<{ qr_code: string; secret: string }>('/api/v1/auth/2fa/enable')
    );
  }

  async disable2FA(): Promise<void> {
    await apiCall(() =>
      authApi.post('/api/v1/auth/2fa/disable')
    );
  }

  async verify2FA(code: string): Promise<void> {
    await apiCall(() =>
      authApi.post('/api/v1/auth/2fa/verify', { code })
    );
  }

  // Obtenir l'historique des connexions
  async getLoginHistory(): Promise<any[]> {
    return await apiCall(() =>
      authApi.get<any[]>('/api/v1/auth/login-history')
    );
  }

  // Révoquer toutes les sessions
  async revokeAllSessions(): Promise<void> {
    await apiCall(() =>
      authApi.post('/api/v1/auth/revoke-all-sessions')
    );
  }
}

export const authService = new AuthService();
export default authService;
