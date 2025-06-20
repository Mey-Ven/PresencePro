import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { notificationService } from '../services/notificationService';
import { useAuth } from './AuthContext';
import { Notification } from '../services/api';

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  isConnected: boolean;
  markAsRead: (notificationId: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (notificationId: string) => Promise<void>;
  createNotification: (data: {
    title: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success';
    priority?: 'low' | 'normal' | 'high' | 'urgent';
    action_url?: string;
  }) => Promise<void>;
  showToast: (message: string, type?: 'info' | 'warning' | 'error' | 'success') => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: ReactNode;
}

interface ToastNotification {
  id: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  timestamp: number;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [toasts, setToasts] = useState<ToastNotification[]>([]);

  // Load initial notifications
  useEffect(() => {
    if (!user) return;

    const loadNotifications = async () => {
      try {
        const [notificationsResponse, countResponse] = await Promise.all([
          notificationService.getMyNotifications({ page: 1, per_page: 50 }),
          notificationService.getMyNotificationCount()
        ]);

        setNotifications(notificationsResponse.data);
        setUnreadCount(countResponse.unread);
      } catch (error) {
        console.error('Error loading notifications:', error);
      }
    };

    loadNotifications();

    // Connect to WebSocket
    notificationService.connectWebSocket();
    setIsConnected(true);

    // Subscribe to new notifications
    const unsubscribe = notificationService.onNewNotification((notification) => {
      setNotifications(prev => [notification, ...prev]);
      setUnreadCount(prev => prev + 1);
      
      // Show toast for new notifications
      showToast(notification.message, notification.type);
    });

    return () => {
      unsubscribe();
      notificationService.disconnectWebSocket();
      setIsConnected(false);
    };
  }, [user]);

  // Mark notification as read
  const markAsRead = async (notificationId: string) => {
    try {
      await notificationService.markAsRead(notificationId);
      setNotifications(prev => 
        prev.map(n => 
          n.id === notificationId 
            ? { ...n, is_read: true, read_at: new Date().toISOString() }
            : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications(prev => 
        prev.map(n => ({ 
          ...n, 
          is_read: true, 
          read_at: n.read_at || new Date().toISOString() 
        }))
      );
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      throw error;
    }
  };

  // Delete notification
  const deleteNotification = async (notificationId: string) => {
    try {
      await notificationService.deleteNotification(notificationId);
      const notification = notifications.find(n => n.id === notificationId);
      
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      
      if (notification && !notification.is_read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
      throw error;
    }
  };

  // Create notification
  const createNotification = async (data: {
    title: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success';
    priority?: 'low' | 'normal' | 'high' | 'urgent';
    action_url?: string;
  }) => {
    if (!user) return;

    try {
      const notification = await notificationService.createNotification({
        user_id: user.id,
        title: data.title,
        message: data.message,
        type: data.type,
        priority: data.priority || 'normal',
        action_url: data.action_url,
      });

      setNotifications(prev => [notification, ...prev]);
      setUnreadCount(prev => prev + 1);
    } catch (error) {
      console.error('Error creating notification:', error);
      throw error;
    }
  };

  // Show toast notification
  const showToast = (message: string, type: 'info' | 'warning' | 'error' | 'success' = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    const toast: ToastNotification = {
      id,
      message,
      type,
      timestamp: Date.now(),
    };

    setToasts(prev => [...prev, toast]);

    // Auto-remove toast after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  };

  // Remove toast
  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const value: NotificationContextType = {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    createNotification,
    showToast,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      
      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden ${
              toast.type === 'success' ? 'border-l-4 border-green-500' :
              toast.type === 'warning' ? 'border-l-4 border-yellow-500' :
              toast.type === 'error' ? 'border-l-4 border-red-500' :
              'border-l-4 border-blue-500'
            }`}
          >
            <div className="p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  {toast.type === 'success' && (
                    <div className="h-5 w-5 text-green-400">✓</div>
                  )}
                  {toast.type === 'warning' && (
                    <div className="h-5 w-5 text-yellow-400">⚠</div>
                  )}
                  {toast.type === 'error' && (
                    <div className="h-5 w-5 text-red-400">✕</div>
                  )}
                  {toast.type === 'info' && (
                    <div className="h-5 w-5 text-blue-400">ℹ</div>
                  )}
                </div>
                <div className="ml-3 w-0 flex-1 pt-0.5">
                  <p className="text-sm font-medium text-gray-900">
                    {toast.message}
                  </p>
                </div>
                <div className="ml-4 flex-shrink-0 flex">
                  <button
                    className="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    onClick={() => removeToast(toast.id)}
                  >
                    <span className="sr-only">Close</span>
                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
};

export const useNotifications = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};
