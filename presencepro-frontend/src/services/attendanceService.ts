import { api } from '../config/api';
import { 
  AttendanceRecord, 
  AttendanceSession, 
  AttendanceStatus,
  ApiResponse, 
  PaginatedResponse,
  SearchFilters 
} from '../types';

// Endpoints de l'API de présence
const ATTENDANCE_ENDPOINTS = {
  ATTENDANCE: '/api/v1/attendance',
  SESSIONS: '/api/v1/attendance/sessions',
  MARK: '/api/v1/attendance/mark',
  BULK_MARK: '/api/v1/attendance/bulk-mark',
  STUDENT: '/api/v1/attendance/student',
  COURSE: '/api/v1/attendance/course',
  CLASS: '/api/v1/attendance/class',
  REPORTS: '/api/v1/attendance/reports',
} as const;

// Interface pour les filtres de recherche de présences
export interface AttendanceSearchFilters extends SearchFilters {
  studentId?: string;
  courseId?: string;
  classId?: string;
  teacherId?: string;
  status?: AttendanceStatus;
  dateFrom?: string;
  dateTo?: string;
}

// Interface pour marquer une présence
export interface MarkAttendanceData {
  studentId: string;
  courseId: string;
  status: AttendanceStatus;
  date?: string;
  notes?: string;
}

// Interface pour marquer plusieurs présences
export interface BulkMarkAttendanceData {
  courseId: string;
  date: string;
  records: {
    studentId: string;
    status: AttendanceStatus;
    notes?: string;
  }[];
}

// Interface pour créer une session de présence
export interface CreateSessionData {
  courseId: string;
  date: string;
  startTime: string;
  endTime: string;
}

// Interface pour les rapports de présence
export interface AttendanceReportFilters {
  type: 'student' | 'class' | 'course' | 'teacher';
  targetId: string;
  dateFrom: string;
  dateTo: string;
  format?: 'json' | 'csv' | 'pdf';
}

// Service de gestion des présences
class AttendanceService {
  /**
   * Récupérer tous les enregistrements de présence avec pagination et filtres
   */
  async getAttendanceRecords(
    page: number = 1,
    limit: number = 10,
    filters?: AttendanceSearchFilters
  ): Promise<PaginatedResponse<AttendanceRecord>> {
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

      const response = await api.get<PaginatedResponse<AttendanceRecord>>(
        `${ATTENDANCE_ENDPOINTS.ATTENDANCE}?${params}`
      );

      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des présences'
      );
    }
  }

  /**
   * Récupérer un enregistrement de présence par ID
   */
  async getAttendanceById(id: string): Promise<AttendanceRecord> {
    try {
      const response = await api.get<ApiResponse<AttendanceRecord>>(
        `${ATTENDANCE_ENDPOINTS.ATTENDANCE}/${id}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Enregistrement non trouvé');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération de l\'enregistrement'
      );
    }
  }

  /**
   * Marquer la présence d'un étudiant
   */
  async markAttendance(attendanceData: MarkAttendanceData): Promise<AttendanceRecord> {
    try {
      const response = await api.post<ApiResponse<AttendanceRecord>>(
        ATTENDANCE_ENDPOINTS.MARK,
        attendanceData
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors du marquage');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors du marquage de la présence'
      );
    }
  }

  /**
   * Marquer la présence de plusieurs étudiants en une fois
   */
  async bulkMarkAttendance(bulkData: BulkMarkAttendanceData): Promise<AttendanceRecord[]> {
    try {
      const response = await api.post<ApiResponse<AttendanceRecord[]>>(
        ATTENDANCE_ENDPOINTS.BULK_MARK,
        bulkData
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors du marquage en lot');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors du marquage en lot des présences'
      );
    }
  }

  /**
   * Mettre à jour un enregistrement de présence
   */
  async updateAttendance(
    id: string, 
    updateData: Partial<AttendanceRecord>
  ): Promise<AttendanceRecord> {
    try {
      const response = await api.put<ApiResponse<AttendanceRecord>>(
        `${ATTENDANCE_ENDPOINTS.ATTENDANCE}/${id}`,
        updateData
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors de la mise à jour');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la mise à jour de la présence'
      );
    }
  }

  /**
   * Supprimer un enregistrement de présence
   */
  async deleteAttendance(id: string): Promise<void> {
    try {
      const response = await api.delete<ApiResponse<void>>(
        `${ATTENDANCE_ENDPOINTS.ATTENDANCE}/${id}`
      );

      if (!response.data.success) {
        throw new Error(response.data.message || 'Erreur lors de la suppression');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la suppression de l\'enregistrement'
      );
    }
  }

  // ============================================================================
  // Gestion des sessions de présence
  // ============================================================================

  /**
   * Récupérer toutes les sessions de présence
   */
  async getAttendanceSessions(
    page: number = 1,
    limit: number = 10,
    filters?: AttendanceSearchFilters
  ): Promise<PaginatedResponse<AttendanceSession>> {
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

      const response = await api.get<PaginatedResponse<AttendanceSession>>(
        `${ATTENDANCE_ENDPOINTS.SESSIONS}?${params}`
      );

      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des sessions'
      );
    }
  }

  /**
   * Créer une nouvelle session de présence
   */
  async createAttendanceSession(sessionData: CreateSessionData): Promise<AttendanceSession> {
    try {
      const response = await api.post<ApiResponse<AttendanceSession>>(
        ATTENDANCE_ENDPOINTS.SESSIONS,
        sessionData
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors de la création');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la création de la session'
      );
    }
  }

  /**
   * Récupérer une session de présence par ID
   */
  async getAttendanceSessionById(id: string): Promise<AttendanceSession> {
    try {
      const response = await api.get<ApiResponse<AttendanceSession>>(
        `${ATTENDANCE_ENDPOINTS.SESSIONS}/${id}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Session non trouvée');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération de la session'
      );
    }
  }

  /**
   * Finaliser une session de présence
   */
  async completeAttendanceSession(id: string): Promise<AttendanceSession> {
    try {
      const response = await api.patch<ApiResponse<AttendanceSession>>(
        `${ATTENDANCE_ENDPOINTS.SESSIONS}/${id}/complete`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors de la finalisation');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la finalisation de la session'
      );
    }
  }

  // ============================================================================
  // Requêtes spécifiques par entité
  // ============================================================================

  /**
   * Récupérer les présences d'un étudiant
   */
  async getStudentAttendance(
    studentId: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<AttendanceRecord[]> {
    try {
      const params = new URLSearchParams();
      if (dateFrom) params.append('dateFrom', dateFrom);
      if (dateTo) params.append('dateTo', dateTo);

      const response = await api.get<ApiResponse<AttendanceRecord[]>>(
        `${ATTENDANCE_ENDPOINTS.STUDENT}/${studentId}?${params}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Aucune présence trouvée');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des présences de l\'étudiant'
      );
    }
  }

  /**
   * Récupérer les présences d'un cours
   */
  async getCourseAttendance(
    courseId: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<AttendanceRecord[]> {
    try {
      const params = new URLSearchParams();
      if (dateFrom) params.append('dateFrom', dateFrom);
      if (dateTo) params.append('dateTo', dateTo);

      const response = await api.get<ApiResponse<AttendanceRecord[]>>(
        `${ATTENDANCE_ENDPOINTS.COURSE}/${courseId}?${params}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Aucune présence trouvée');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des présences du cours'
      );
    }
  }

  /**
   * Récupérer les présences d'une classe
   */
  async getClassAttendance(
    classId: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<AttendanceRecord[]> {
    try {
      const params = new URLSearchParams();
      if (dateFrom) params.append('dateFrom', dateFrom);
      if (dateTo) params.append('dateTo', dateTo);

      const response = await api.get<ApiResponse<AttendanceRecord[]>>(
        `${ATTENDANCE_ENDPOINTS.CLASS}/${classId}?${params}`
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Aucune présence trouvée');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la récupération des présences de la classe'
      );
    }
  }

  // ============================================================================
  // Rapports et exports
  // ============================================================================

  /**
   * Générer un rapport de présence
   */
  async generateAttendanceReport(filters: AttendanceReportFilters): Promise<any> {
    try {
      const response = await api.post<ApiResponse<any>>(
        ATTENDANCE_ENDPOINTS.REPORTS,
        filters
      );

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Erreur lors de la génération du rapport');
      }
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de la génération du rapport'
      );
    }
  }

  /**
   * Exporter les données de présence
   */
  async exportAttendanceData(
    filters: AttendanceSearchFilters,
    format: 'csv' | 'xlsx' | 'pdf' = 'csv'
  ): Promise<Blob> {
    try {
      const params = new URLSearchParams();
      params.append('format', format);

      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, value.toString());
          }
        });
      }

      const response = await api.get(
        `${ATTENDANCE_ENDPOINTS.ATTENDANCE}/export?${params}`,
        {
          responseType: 'blob',
        }
      );

      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.message || 
        'Erreur lors de l\'export des données'
      );
    }
  }
}

// Export de l'instance du service
export const attendanceService = new AttendanceService();
export default attendanceService;
