import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ApiResponse, ApiError } from '../types';

// Configuration des URLs des microservices
const API_URLS = {
  AUTH: process.env.REACT_APP_AUTH_SERVICE_URL || 'http://localhost:8001',
  USER: process.env.REACT_APP_USER_SERVICE_URL || 'http://localhost:8002',
  COURSE: process.env.REACT_APP_COURSE_SERVICE_URL || 'http://localhost:8003',
  FACE_RECOGNITION: process.env.REACT_APP_FACE_RECOGNITION_SERVICE_URL || 'http://localhost:8004',
  ATTENDANCE: process.env.REACT_APP_ATTENDANCE_SERVICE_URL || 'http://localhost:8005',
  JUSTIFICATION: process.env.REACT_APP_JUSTIFICATION_SERVICE_URL || 'http://localhost:8006',
  MESSAGING: process.env.REACT_APP_MESSAGING_SERVICE_URL || 'http://localhost:8007',
  NOTIFICATION: process.env.REACT_APP_NOTIFICATION_SERVICE_URL || 'http://localhost:8008',
  STATISTICS: process.env.REACT_APP_STATISTICS_SERVICE_URL || 'http://localhost:8009',
};

// Instance Axios principale
const createApiInstance = (baseURL: string): AxiosInstance => {
  const instance = axios.create({
    baseURL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Intercepteur pour ajouter le token d'authentification
  instance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Intercepteur pour gérer les réponses et erreurs
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      return response;
    },
    (error) => {
      if (error.response?.status === 401) {
        // Token expiré ou invalide
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        window.location.href = '/login';
      }
      
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Une erreur est survenue',
        code: error.response?.status?.toString(),
        details: error.response?.data,
      };
      
      return Promise.reject(apiError);
    }
  );

  return instance;
};

// Instances pour chaque microservice
export const authApi = createApiInstance(API_URLS.AUTH);
export const userApi = createApiInstance(API_URLS.USER);
export const courseApi = createApiInstance(API_URLS.COURSE);
export const faceRecognitionApi = createApiInstance(API_URLS.FACE_RECOGNITION);
export const attendanceApi = createApiInstance(API_URLS.ATTENDANCE);
export const justificationApi = createApiInstance(API_URLS.JUSTIFICATION);
export const messagingApi = createApiInstance(API_URLS.MESSAGING);
export const notificationApi = createApiInstance(API_URLS.NOTIFICATION);
export const statisticsApi = createApiInstance(API_URLS.STATISTICS);

// Fonctions utilitaires pour les appels API
export const apiCall = async <T>(
  apiFunction: () => Promise<AxiosResponse<T>>
): Promise<T> => {
  try {
    const response = await apiFunction();
    return response.data;
  } catch (error) {
    throw error as ApiError;
  }
};

export const handleApiError = (error: any): ApiError => {
  if (error.response) {
    return {
      message: error.response.data?.detail || error.response.data?.message || 'Erreur serveur',
      code: error.response.status?.toString(),
      details: error.response.data,
    };
  } else if (error.request) {
    return {
      message: 'Impossible de contacter le serveur',
      code: 'NETWORK_ERROR',
    };
  } else {
    return {
      message: error.message || 'Une erreur inattendue est survenue',
      code: 'UNKNOWN_ERROR',
    };
  }
};

// Fonction pour vérifier la santé des services
export const checkServiceHealth = async (serviceName: string): Promise<boolean> => {
  try {
    const apiInstance = getApiInstance(serviceName);
    await apiInstance.get('/health');
    return true;
  } catch (error) {
    console.error(`Service ${serviceName} is not healthy:`, error);
    return false;
  }
};

// Fonction pour obtenir l'instance API appropriée
const getApiInstance = (serviceName: string): AxiosInstance => {
  switch (serviceName.toLowerCase()) {
    case 'auth':
      return authApi;
    case 'user':
      return userApi;
    case 'course':
      return courseApi;
    case 'face_recognition':
      return faceRecognitionApi;
    case 'attendance':
      return attendanceApi;
    case 'justification':
      return justificationApi;
    case 'messaging':
      return messagingApi;
    case 'notification':
      return notificationApi;
    case 'statistics':
      return statisticsApi;
    default:
      throw new Error(`Service inconnu: ${serviceName}`);
  }
};

// Fonction pour vérifier l'état de tous les services
export const checkAllServicesHealth = async (): Promise<Record<string, boolean>> => {
  const services = [
    'auth',
    'user',
    'course',
    'face_recognition',
    'attendance',
    'justification',
    'messaging',
    'notification',
    'statistics',
  ];

  const healthChecks = await Promise.allSettled(
    services.map(async (service) => ({
      service,
      healthy: await checkServiceHealth(service),
    }))
  );

  const result: Record<string, boolean> = {};
  healthChecks.forEach((check, index) => {
    if (check.status === 'fulfilled') {
      result[check.value.service] = check.value.healthy;
    } else {
      result[services[index]] = false;
    }
  });

  return result;
};

// Configuration pour les uploads de fichiers
export const createFormDataRequest = (file: File, additionalData?: Record<string, any>) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (additionalData) {
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, typeof value === 'string' ? value : JSON.stringify(value));
    });
  }
  
  return formData;
};

// Fonction pour télécharger des fichiers
export const downloadFile = async (url: string, filename: string): Promise<void> => {
  try {
    const response = await axios.get(url, {
      responseType: 'blob',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });
    
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    throw handleApiError(error);
  }
};

// Fonction pour formater les paramètres de requête
export const formatQueryParams = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value.toString());
    }
  });
  
  return searchParams.toString();
};

// Fonction pour gérer la pagination
export const buildPaginationParams = (page: number, pageSize: number = 20) => {
  return {
    page,
    per_page: pageSize,
  };
};

// Fonction pour gérer les filtres de date
export const formatDateForApi = (date: Date | string): string => {
  if (typeof date === 'string') {
    return date;
  }
  return date.toISOString().split('T')[0];
};

// Fonction pour gérer les retry automatiques
export const retryApiCall = async <T>(
  apiFunction: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiFunction();
    } catch (error) {
      lastError = error;
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }
  
  throw lastError;
};

// Export des URLs pour utilisation dans les composants
export { API_URLS };

// Export par défaut
export default {
  authApi,
  userApi,
  courseApi,
  faceRecognitionApi,
  attendanceApi,
  justificationApi,
  messagingApi,
  notificationApi,
  statisticsApi,
  apiCall,
  handleApiError,
  checkServiceHealth,
  checkAllServicesHealth,
  createFormDataRequest,
  downloadFile,
  formatQueryParams,
  buildPaginationParams,
  formatDateForApi,
  retryApiCall,
};
