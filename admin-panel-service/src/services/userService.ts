import { userApi, apiCall, formatQueryParams, buildPaginationParams } from './api';
import { User, Student, Teacher, Parent, Class, PaginatedResponse, UserFilters } from '../types';

export interface CreateUserData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'teacher' | 'student' | 'parent';
  is_active?: boolean;
}

export interface UpdateUserData {
  email?: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
}

export interface CreateStudentData {
  user_id: string;
  student_number: string;
  class_id: string;
  parent_id?: string;
  enrollment_date: string;
}

export interface CreateTeacherData {
  user_id: string;
  employee_number: string;
  department: string;
  hire_date: string;
}

export interface CreateParentData {
  user_id: string;
  phone: string;
  address: string;
  emergency_contact: string;
}

class UserService {
  // === Gestion des utilisateurs ===
  
  // Obtenir tous les utilisateurs avec pagination et filtres
  async getUsers(page: number = 1, pageSize: number = 20, filters?: UserFilters): Promise<PaginatedResponse<User>> {
    const params = {
      ...buildPaginationParams(page, pageSize),
      ...filters,
    };
    
    const queryString = formatQueryParams(params);
    return await apiCall(() =>
      userApi.get<PaginatedResponse<User>>(`/api/v1/users?${queryString}`)
    );
  }

  // Obtenir un utilisateur par ID
  async getUserById(id: string): Promise<User> {
    return await apiCall(() =>
      userApi.get<User>(`/api/v1/users/${id}`)
    );
  }

  // Créer un nouvel utilisateur
  async createUser(userData: CreateUserData): Promise<User> {
    return await apiCall(() =>
      userApi.post<User>('/api/v1/users', userData)
    );
  }

  // Mettre à jour un utilisateur
  async updateUser(id: string, userData: UpdateUserData): Promise<User> {
    return await apiCall(() =>
      userApi.put<User>(`/api/v1/users/${id}`, userData)
    );
  }

  // Supprimer un utilisateur
  async deleteUser(id: string): Promise<void> {
    await apiCall(() =>
      userApi.delete(`/api/v1/users/${id}`)
    );
  }

  // Activer/désactiver un utilisateur
  async toggleUserStatus(id: string): Promise<User> {
    return await apiCall(() =>
      userApi.patch<User>(`/api/v1/users/${id}/toggle-status`)
    );
  }

  // === Gestion des étudiants ===
  
  // Obtenir tous les étudiants
  async getStudents(page: number = 1, pageSize: number = 20, classId?: string): Promise<PaginatedResponse<Student>> {
    const params = {
      ...buildPaginationParams(page, pageSize),
      ...(classId && { class_id: classId }),
    };
    
    const queryString = formatQueryParams(params);
    return await apiCall(() =>
      userApi.get<PaginatedResponse<Student>>(`/api/v1/students?${queryString}`)
    );
  }

  // Obtenir un étudiant par ID
  async getStudentById(id: string): Promise<Student> {
    return await apiCall(() =>
      userApi.get<Student>(`/api/v1/students/${id}`)
    );
  }

  // Créer un nouvel étudiant
  async createStudent(studentData: CreateStudentData): Promise<Student> {
    return await apiCall(() =>
      userApi.post<Student>('/api/v1/students', studentData)
    );
  }

  // Mettre à jour un étudiant
  async updateStudent(id: string, studentData: Partial<CreateStudentData>): Promise<Student> {
    return await apiCall(() =>
      userApi.put<Student>(`/api/v1/students/${id}`, studentData)
    );
  }

  // Supprimer un étudiant
  async deleteStudent(id: string): Promise<void> {
    await apiCall(() =>
      userApi.delete(`/api/v1/students/${id}`)
    );
  }

  // Obtenir les étudiants d'une classe
  async getStudentsByClass(classId: string): Promise<Student[]> {
    return await apiCall(() =>
      userApi.get<Student[]>(`/api/v1/classes/${classId}/students`)
    );
  }

  // === Gestion des enseignants ===
  
  // Obtenir tous les enseignants
  async getTeachers(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Teacher>> {
    const params = buildPaginationParams(page, pageSize);
    const queryString = formatQueryParams(params);
    
    return await apiCall(() =>
      userApi.get<PaginatedResponse<Teacher>>(`/api/v1/teachers?${queryString}`)
    );
  }

  // Obtenir un enseignant par ID
  async getTeacherById(id: string): Promise<Teacher> {
    return await apiCall(() =>
      userApi.get<Teacher>(`/api/v1/teachers/${id}`)
    );
  }

  // Créer un nouvel enseignant
  async createTeacher(teacherData: CreateTeacherData): Promise<Teacher> {
    return await apiCall(() =>
      userApi.post<Teacher>('/api/v1/teachers', teacherData)
    );
  }

  // Mettre à jour un enseignant
  async updateTeacher(id: string, teacherData: Partial<CreateTeacherData>): Promise<Teacher> {
    return await apiCall(() =>
      userApi.put<Teacher>(`/api/v1/teachers/${id}`, teacherData)
    );
  }

  // Supprimer un enseignant
  async deleteTeacher(id: string): Promise<void> {
    await apiCall(() =>
      userApi.delete(`/api/v1/teachers/${id}`)
    );
  }

  // === Gestion des parents ===
  
  // Obtenir tous les parents
  async getParents(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Parent>> {
    const params = buildPaginationParams(page, pageSize);
    const queryString = formatQueryParams(params);
    
    return await apiCall(() =>
      userApi.get<PaginatedResponse<Parent>>(`/api/v1/parents?${queryString}`)
    );
  }

  // Obtenir un parent par ID
  async getParentById(id: string): Promise<Parent> {
    return await apiCall(() =>
      userApi.get<Parent>(`/api/v1/parents/${id}`)
    );
  }

  // Créer un nouveau parent
  async createParent(parentData: CreateParentData): Promise<Parent> {
    return await apiCall(() =>
      userApi.post<Parent>('/api/v1/parents', parentData)
    );
  }

  // Mettre à jour un parent
  async updateParent(id: string, parentData: Partial<CreateParentData>): Promise<Parent> {
    return await apiCall(() =>
      userApi.put<Parent>(`/api/v1/parents/${id}`, parentData)
    );
  }

  // Supprimer un parent
  async deleteParent(id: string): Promise<void> {
    await apiCall(() =>
      userApi.delete(`/api/v1/parents/${id}`)
    );
  }

  // Associer un parent à un étudiant
  async linkParentToStudent(parentId: string, studentId: string): Promise<void> {
    await apiCall(() =>
      userApi.post(`/api/v1/parents/${parentId}/students/${studentId}`)
    );
  }

  // Dissocier un parent d'un étudiant
  async unlinkParentFromStudent(parentId: string, studentId: string): Promise<void> {
    await apiCall(() =>
      userApi.delete(`/api/v1/parents/${parentId}/students/${studentId}`)
    );
  }

  // === Fonctions utilitaires ===
  
  // Rechercher des utilisateurs
  async searchUsers(query: string, role?: string): Promise<User[]> {
    const params = {
      search: query,
      ...(role && { role }),
    };
    
    const queryString = formatQueryParams(params);
    return await apiCall(() =>
      userApi.get<User[]>(`/api/v1/users/search?${queryString}`)
    );
  }

  // Obtenir les statistiques des utilisateurs
  async getUserStats(): Promise<{
    total_users: number;
    active_users: number;
    students_count: number;
    teachers_count: number;
    parents_count: number;
    admins_count: number;
  }> {
    return await apiCall(() =>
      userApi.get('/api/v1/users/stats')
    );
  }

  // Exporter la liste des utilisateurs
  async exportUsers(format: 'csv' | 'xlsx' = 'xlsx', filters?: UserFilters): Promise<Blob> {
    const params = {
      format,
      ...filters,
    };
    
    const queryString = formatQueryParams(params);
    const response = await userApi.get(`/api/v1/users/export?${queryString}`, {
      responseType: 'blob',
    });
    
    return response.data;
  }

  // Importer des utilisateurs depuis un fichier
  async importUsers(file: File): Promise<{
    success_count: number;
    error_count: number;
    errors: string[];
  }> {
    const formData = new FormData();
    formData.append('file', file);
    
    return await apiCall(() =>
      userApi.post('/api/v1/users/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    );
  }

  // Réinitialiser le mot de passe d'un utilisateur
  async resetUserPassword(userId: string): Promise<{ temporary_password: string }> {
    return await apiCall(() =>
      userApi.post<{ temporary_password: string }>(`/api/v1/users/${userId}/reset-password`)
    );
  }

  // Envoyer un email de bienvenue
  async sendWelcomeEmail(userId: string): Promise<void> {
    await apiCall(() =>
      userApi.post(`/api/v1/users/${userId}/send-welcome-email`)
    );
  }
}

export const userService = new UserService();
export default userService;
