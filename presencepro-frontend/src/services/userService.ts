import { api } from '../config/api';
import { 
  User, 
  Student, 
  Teacher, 
  Parent, 
  Admin,
  ApiResponse, 
  PaginatedResponse,
  SearchFilters 
} from '../types';

// Endpoints de l'API utilisateur
const USER_ENDPOINTS = {
  USERS: '/api/v1/users',
  STUDENTS: '/api/v1/students',
  TEACHERS: '/api/v1/teachers',
  PARENTS: '/api/v1/parents',
  ADMINS: '/api/v1/admins',
} as const;

// Interface pour les filtres de recherche d'utilisateurs
export interface UserSearchFilters extends SearchFilters {
  role?: 'student' | 'teacher' | 'parent' | 'admin';
  isActive?: boolean;
  department?: string;
  classId?: string;
}

// Interface pour la création d'utilisateur
export interface CreateUserData {
  email: string;
  firstName: string;
  lastName: string;
  role: 'student' | 'teacher' | 'parent' | 'admin';
  phone?: string;
  address?: string;
  // Champs spécifiques selon le rôle
  studentId?: string;
  teacherId?: string;
  parentId?: string;
  adminId?: string;
  department?: string;
  subjects?: string[];
  childrenIds?: string[];
  permissions?: string[];
  classId?: string;
  enrollmentDate?: string;
  hireDate?: string;
}

// Service de gestion des utilisateurs
class UserService {
  /**
   * Récupérer tous les utilisateurs avec pagination et filtres
   */
  async getUsers(
    page: number = 1,
    limit: number = 10,
    filters?: UserSearchFilters
  ): Promise<PaginatedResponse<User>> {
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('limit', limit.toString());

      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, value.toString());
          }
        });
      }

      const response = await api.get<PaginatedResponse<User>>(
        `${USER_ENDPOINTS.USERS}?${params}`
      );

      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des utilisateurs'
      );
    }
  }

  /**
   * Récupérer un utilisateur par ID
   */
  async getUserById(id: string): Promise<User> {
    try {
      const response = await api.get<ApiResponse<User>>(
        `${USER_ENDPOINTS.USERS}/${id}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Utilisateur non trouvé');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération de l\'utilisateur'
      );
    }
  }

  /**
   * Créer un nouvel utilisateur
   */
  async createUser(userData: CreateUserData): Promise<User> {
    try {
      const response = await api.post<ApiResponse<User>>(
        USER_ENDPOINTS.USERS,
        userData
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors de la création');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la création de l\'utilisateur'
      );
    }
  }

  /**
   * Mettre à jour un utilisateur
   */
  async updateUser(id: string, userData: Partial<User>): Promise<User> {
    try {
      const response = await api.put<ApiResponse<User>>(
        `${USER_ENDPOINTS.USERS}/${id}`,
        userData
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors de la mise à jour');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la mise à jour de l\'utilisateur'
      );
    }
  }

  /**
   * Supprimer un utilisateur
   */
  async deleteUser(id: string): Promise<void> {
    try {
      const response = await api.delete<ApiResponse<void>>(
        `${USER_ENDPOINTS.USERS}/${id}`
      );

      if (!response.data.success) {
        throw new Error(response.data.message || 'Erreur lors de la suppression');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la suppression de l\'utilisateur'
      );
    }
  }

  /**
   * Activer/Désactiver un utilisateur
   */
  async toggleUserStatus(id: string, isActive: boolean): Promise<User> {
    try {
      const response = await api.patch<ApiResponse<User>>(
        `${USER_ENDPOINTS.USERS}/${id}/status`,
        { isActive }
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors du changement de statut');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors du changement de statut'
      );
    }
  }

  // ============================================================================
  // Méthodes spécifiques aux étudiants
  // ============================================================================

  /**
   * Récupérer tous les étudiants
   */
  async getStudents(
    page: number = 1,
    limit: number = 10,
    filters?: UserSearchFilters
  ): Promise<PaginatedResponse<Student>> {
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('limit', limit.toString());

      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, value.toString());
          }
        });
      }

      const response = await api.get<PaginatedResponse<Student>>(
        `${USER_ENDPOINTS.STUDENTS}?${params}`
      );

      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des étudiants'
      );
    }
  }

  /**
   * Récupérer un étudiant par ID
   */
  async getStudentById(id: string): Promise<Student> {
    try {
      const response = await api.get<ApiResponse<Student>>(
        `${USER_ENDPOINTS.STUDENTS}/${id}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Étudiant non trouvé');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération de l\'étudiant'
      );
    }
  }

  /**
   * Récupérer les étudiants d'une classe
   */
  async getStudentsByClass(classId: string): Promise<Student[]> {
    try {
      const response = await api.get<ApiResponse<Student[]>>(
        `${USER_ENDPOINTS.STUDENTS}/class/${classId}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Aucun étudiant trouvé');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des étudiants de la classe'
      );
    }
  }

  // ============================================================================
  // Méthodes spécifiques aux enseignants
  // ============================================================================

  /**
   * Récupérer tous les enseignants
   */
  async getTeachers(
    page: number = 1,
    limit: number = 10,
    filters?: UserSearchFilters
  ): Promise<PaginatedResponse<Teacher>> {
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('limit', limit.toString());

      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, value.toString());
          }
        });
      }

      const response = await api.get<PaginatedResponse<Teacher>>(
        `${USER_ENDPOINTS.TEACHERS}?${params}`
      );

      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des enseignants'
      );
    }
  }

  /**
   * Récupérer un enseignant par ID
   */
  async getTeacherById(id: string): Promise<Teacher> {
    try {
      const response = await api.get<ApiResponse<Teacher>>(
        `${USER_ENDPOINTS.TEACHERS}/${id}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Enseignant non trouvé');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération de l\'enseignant'
      );
    }
  }

  // ============================================================================
  // Méthodes spécifiques aux parents
  // ============================================================================

  /**
   * Récupérer tous les parents
   */
  async getParents(
    page: number = 1,
    limit: number = 10,
    filters?: UserSearchFilters
  ): Promise<PaginatedResponse<Parent>> {
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('limit', limit.toString());

      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, value.toString());
          }
        });
      }

      const response = await api.get<PaginatedResponse<Parent>>(
        `${USER_ENDPOINTS.PARENTS}?${params}`
      );

      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des parents'
      );
    }
  }

  /**
   * Récupérer un parent par ID
   */
  async getParentById(id: string): Promise<Parent> {
    try {
      const response = await api.get<ApiResponse<Parent>>(
        `${USER_ENDPOINTS.PARENTS}/${id}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Parent non trouvé');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération du parent'
      );
    }
  }

  /**
   * Importer des utilisateurs depuis un fichier
   */
  async importUsers(file: File, userType: 'student' | 'teacher' | 'parent'): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('userType', userType);

      const response = await api.post<ApiResponse<any>>(
        `${USER_ENDPOINTS.USERS}/import`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors de l\'importation');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de l\'importation des utilisateurs'
      );
    }
  }
}

// Export de l'instance du service
export const userService = new UserService();
export default userService;
