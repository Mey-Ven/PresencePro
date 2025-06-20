import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Notification, AppSettings } from '../types';

// Types pour l'état de l'application
interface AppState {
  notifications: Notification[];
  settings: AppSettings;
  sidebarCollapsed: boolean;
  loading: boolean;
  servicesHealth: Record<string, boolean>;
}

// Types pour les actions
type AppAction =
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'MARK_NOTIFICATION_READ'; payload: string }
  | { type: 'CLEAR_NOTIFICATIONS' }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<AppSettings> }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'UPDATE_SERVICES_HEALTH'; payload: Record<string, boolean> };

// État initial
const initialState: AppState = {
  notifications: [],
  settings: {
    theme: 'light',
    language: 'fr',
    notifications_enabled: true,
    auto_refresh_interval: 30000, // 30 secondes
  },
  sidebarCollapsed: false,
  loading: false,
  servicesHealth: {},
};

// Reducer pour gérer l'état de l'application
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [action.payload, ...state.notifications],
      };
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload),
      };
    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        notifications: state.notifications.map(n =>
          n.id === action.payload ? { ...n, read: true } : n
        ),
      };
    case 'CLEAR_NOTIFICATIONS':
      return {
        ...state,
        notifications: [],
      };
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload },
      };
    case 'TOGGLE_SIDEBAR':
      return {
        ...state,
        sidebarCollapsed: !state.sidebarCollapsed,
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'UPDATE_SERVICES_HEALTH':
      return {
        ...state,
        servicesHealth: action.payload,
      };
    default:
      return state;
  }
};

// Interface du contexte
interface AppContextType {
  state: AppState;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  removeNotification: (id: string) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  updateSettings: (settings: Partial<AppSettings>) => void;
  toggleSidebar: () => void;
  setLoading: (loading: boolean) => void;
  updateServicesHealth: (health: Record<string, boolean>) => void;
}

// Création du contexte
const AppContext = createContext<AppContextType | undefined>(undefined);

// Hook pour utiliser le contexte
export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp doit être utilisé dans un AppProvider');
  }
  return context;
};

// Props du provider
interface AppProviderProps {
  children: ReactNode;
}

// Provider du contexte de l'application
export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Fonction pour ajouter une notification
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>): void => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      read: false,
    };
    
    dispatch({ type: 'ADD_NOTIFICATION', payload: newNotification });
    
    // Auto-suppression après 5 secondes pour les notifications de succès
    if (notification.type === 'success') {
      setTimeout(() => {
        removeNotification(newNotification.id);
      }, 5000);
    }
  };

  // Fonction pour supprimer une notification
  const removeNotification = (id: string): void => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
  };

  // Fonction pour marquer une notification comme lue
  const markNotificationRead = (id: string): void => {
    dispatch({ type: 'MARK_NOTIFICATION_READ', payload: id });
  };

  // Fonction pour vider toutes les notifications
  const clearNotifications = (): void => {
    dispatch({ type: 'CLEAR_NOTIFICATIONS' });
  };

  // Fonction pour mettre à jour les paramètres
  const updateSettings = (settings: Partial<AppSettings>): void => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: settings });
    
    // Sauvegarder dans le localStorage
    const currentSettings = JSON.parse(localStorage.getItem('app_settings') || '{}');
    const newSettings = { ...currentSettings, ...settings };
    localStorage.setItem('app_settings', JSON.stringify(newSettings));
  };

  // Fonction pour basculer la sidebar
  const toggleSidebar = (): void => {
    dispatch({ type: 'TOGGLE_SIDEBAR' });
  };

  // Fonction pour définir l'état de chargement
  const setLoading = (loading: boolean): void => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  // Fonction pour mettre à jour l'état de santé des services
  const updateServicesHealth = (health: Record<string, boolean>): void => {
    dispatch({ type: 'UPDATE_SERVICES_HEALTH', payload: health });
  };

  // Valeur du contexte
  const contextValue: AppContextType = {
    state,
    addNotification,
    removeNotification,
    markNotificationRead,
    clearNotifications,
    updateSettings,
    toggleSidebar,
    setLoading,
    updateServicesHealth,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

export default AppContext;
