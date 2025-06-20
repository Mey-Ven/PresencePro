import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import toast from 'react-hot-toast';

// Configuration de base de l'API
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Types pour la configuration
interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

// Configuration par défaut
const defaultConfig: ApiConfig = {
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 secondes
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
};

// Création de l'instance Axios
export const apiClient: AxiosInstance = axios.create(defaultConfig);

// Types pour la gestion des tokens
interface TokenStorage {
  getAccessToken: () => string | null;
  getRefreshToken: () => string | null;
  setTokens: (accessToken: string, refreshToken: string) => void;
  clearTokens: () => void;
}

// Gestionnaire de tokens
export const tokenStorage: TokenStorage = {
  getAccessToken: () => localStorage.getItem('accessToken'),
  getRefreshToken: () => localStorage.getItem('refreshToken'),
  setTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
  },
  clearTokens: () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  },
};

// Flag pour éviter les boucles infinies lors du refresh
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (reason?: any) => void;
}> = [];

// Fonction pour traiter la queue des requêtes en attente
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  
  failedQueue = [];
};

// Intercepteur de requête - Ajouter le token d'authentification
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig): any => {
    const token = tokenStorage.getAccessToken();
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Ajouter un ID de requête pour le debugging
    config.headers = {
      ...config.headers,
      'X-Request-ID': `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Intercepteur de réponse - Gestion des erreurs et refresh des tokens
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest: any = error.config;
    
    // Gestion des erreurs 401 (Unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Si un refresh est déjà en cours, mettre la requête en queue
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return apiClient(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }
      
      originalRequest._retry = true;
      isRefreshing = true;
      
      const refreshToken = tokenStorage.getRefreshToken();
      
      if (refreshToken) {
        try {
          // Tentative de refresh du token
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refreshToken,
          });
          
          const { accessToken, refreshToken: newRefreshToken } = response.data;
          
          // Sauvegarder les nouveaux tokens
          tokenStorage.setTokens(accessToken, newRefreshToken);
          
          // Traiter la queue des requêtes en attente
          processQueue(null, accessToken);
          
          // Réessayer la requête originale
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${accessToken}`;
          }
          
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Le refresh a échoué, déconnecter l'utilisateur
          processQueue(refreshError, null);
          tokenStorage.clearTokens();
          
          // Rediriger vers la page de connexion
          window.location.href = '/login';
          
          toast.error('Session expirée. Veuillez vous reconnecter.');
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      } else {
        // Pas de refresh token, déconnecter l'utilisateur
        tokenStorage.clearTokens();
        window.location.href = '/login';
        toast.error('Session expirée. Veuillez vous reconnecter.');
        return Promise.reject(error);
      }
    }
    
    // Gestion des autres erreurs
    handleApiError(error);
    return Promise.reject(error);
  }
);

// Fonction pour gérer les erreurs API
const handleApiError = (error: AxiosError) => {
  const status = error.response?.status;
  const message = (error.response?.data as any)?.message || error.message;
  
  switch (status) {
    case 400:
      toast.error(`Erreur de validation: ${message}`);
      break;
    case 403:
      toast.error('Accès refusé. Vous n\'avez pas les permissions nécessaires.');
      break;
    case 404:
      toast.error('Ressource non trouvée.');
      break;
    case 429:
      toast.error('Trop de requêtes. Veuillez patienter.');
      break;
    case 500:
      toast.error('Erreur serveur. Veuillez réessayer plus tard.');
      break;
    case 503:
      toast.error('Service temporairement indisponible.');
      break;
    default:
      if (status && status >= 400) {
        toast.error(`Erreur ${status}: ${message}`);
      } else if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
        toast.error('Erreur de connexion. Vérifiez votre connexion internet.');
      } else {
        toast.error('Une erreur inattendue s\'est produite.');
      }
  }
};

// Fonction utilitaire pour créer des requêtes avec gestion d'erreur
export const createApiRequest = <T = any>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  url: string,
  data?: any,
  config?: AxiosRequestConfig
) => {
  return apiClient.request<T>({
    method,
    url,
    data,
    ...config,
  });
};

// Fonctions utilitaires pour les requêtes courantes
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) => 
    createApiRequest<T>('GET', url, undefined, config),
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    createApiRequest<T>('POST', url, data, config),
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    createApiRequest<T>('PUT', url, data, config),
  
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    createApiRequest<T>('PATCH', url, data, config),
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig) => 
    createApiRequest<T>('DELETE', url, undefined, config),
};

// Configuration pour les uploads de fichiers
export const createFileUploadConfig = (
  onUploadProgress?: (progressEvent: any) => void
): AxiosRequestConfig => ({
  headers: {
    'Content-Type': 'multipart/form-data',
  },
  onUploadProgress,
  timeout: 60000, // 1 minute pour les uploads
});

// Fonction pour uploader des fichiers
export const uploadFile = (
  url: string,
  file: File,
  onProgress?: (progress: number) => void
) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return api.post(url, formData, createFileUploadConfig(
    onProgress ? (progressEvent) => {
      const progress = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      );
      onProgress(progress);
    } : undefined
  ));
};

// Export de l'instance par défaut
export default apiClient;
