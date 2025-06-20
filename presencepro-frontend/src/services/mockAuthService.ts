import { User, LoginCredentials, AuthResponse } from '../types';

// Utilisateurs de démonstration
const DEMO_USERS: Record<string, { user: User; password: string }> = {
  'admin@presencepro.com': {
    password: 'admin123',
    user: {
      id: '1',
      email: 'admin@presencepro.com',
      firstName: 'Admin',
      lastName: 'PresencePro',
      role: 'admin',
      isActive: true,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      profilePicture: undefined,
      phone: '+33123456789',
      address: '123 Rue de l\'Administration, Paris',
    }
  },
  'teacher@presencepro.com': {
    password: 'teacher123',
    user: {
      id: '2',
      email: 'teacher@presencepro.com',
      firstName: 'Marie',
      lastName: 'Dupont',
      role: 'teacher',
      isActive: true,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      profilePicture: undefined,
      phone: '+33123456790',
      address: '456 Avenue des Enseignants, Lyon',
    }
  },
  'student@presencepro.com': {
    password: 'student123',
    user: {
      id: '3',
      email: 'student@presencepro.com',
      firstName: 'Jean',
      lastName: 'Martin',
      role: 'student',
      isActive: true,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      profilePicture: undefined,
      phone: '+33123456791',
      address: '789 Rue des Étudiants, Marseille',
    }
  },
  'parent@presencepro.com': {
    password: 'parent123',
    user: {
      id: '4',
      email: 'parent@presencepro.com',
      firstName: 'Sophie',
      lastName: 'Moreau',
      role: 'parent',
      isActive: true,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      profilePicture: undefined,
      phone: '+33123456792',
      address: '321 Boulevard des Parents, Toulouse',
    }
  }
};

// Simulation d'un délai réseau
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Génération de tokens factices
const generateToken = (user: User): string => {
  return `mock_token_${user.id}_${Date.now()}`;
};

// Service d'authentification mocké
class MockAuthService {
  /**
   * Connexion utilisateur (version mockée)
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Simulation d'un délai réseau
    await delay(800);

    const { email, password } = credentials;
    const userRecord = DEMO_USERS[email.toLowerCase()];

    if (!userRecord) {
      throw new Error('Adresse email non trouvée');
    }

    if (userRecord.password !== password) {
      throw new Error('Mot de passe incorrect');
    }

    const accessToken = generateToken(userRecord.user);
    const refreshToken = generateToken(userRecord.user);

    return {
      user: userRecord.user,
      accessToken,
      refreshToken,
      expiresIn: 3600, // 1 heure en secondes
    };
  }

  /**
   * Déconnexion utilisateur (version mockée)
   */
  async logout(): Promise<void> {
    await delay(200);
    // Simulation de la déconnexion
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }

  /**
   * Rafraîchir le token d'accès (version mockée)
   */
  async refreshToken(): Promise<AuthResponse> {
    await delay(300);
    
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      throw new Error('Aucun utilisateur connecté');
    }

    const user = JSON.parse(userStr);
    const accessToken = generateToken(user);
    const refreshToken = generateToken(user);

    return {
      user,
      accessToken,
      refreshToken,
      expiresIn: 3600, // 1 heure en secondes
    };
  }

  /**
   * Obtenir le profil utilisateur actuel (version mockée)
   */
  async getProfile(): Promise<User> {
    await delay(300);
    
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      throw new Error('Aucun utilisateur connecté');
    }

    return JSON.parse(userStr);
  }

  /**
   * Mettre à jour le profil utilisateur (version mockée)
   */
  async updateProfile(userData: Partial<User>): Promise<User> {
    await delay(500);
    
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      throw new Error('Aucun utilisateur connecté');
    }

    const currentUser = JSON.parse(userStr);
    const updatedUser = { ...currentUser, ...userData };
    
    localStorage.setItem('user', JSON.stringify(updatedUser));
    
    return updatedUser;
  }

  /**
   * Vérifier si l'utilisateur est connecté
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('accessToken');
    const user = localStorage.getItem('user');
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
   * Obtenir la liste des utilisateurs de démonstration (pour affichage)
   */
  getDemoUsers(): Array<{ email: string; password: string; role: string; name: string }> {
    return Object.entries(DEMO_USERS).map(([email, data]) => ({
      email,
      password: data.password,
      role: data.user.role,
      name: `${data.user.firstName} ${data.user.lastName}`,
    }));
  }
}

// Export de l'instance du service mocké
export const mockAuthService = new MockAuthService();
export default mockAuthService;
