/**
 * Notification Service
 * Handles system notifications, alerts, and real-time updates
 */

import { BaseApiService, Notification, PaginatedResponse } from './api';

export interface CreateNotificationRequest {
  user_id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  action_url?: string;
  action_required?: boolean;
  expires_at?: string;
}

export interface BulkCreateNotificationRequest {
  user_ids: string[];
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  action_url?: string;
  action_required?: boolean;
  expires_at?: string;
}

export interface NotificationFilters {
  user_id?: string;
  type?: 'info' | 'warning' | 'error' | 'success';
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  is_read?: boolean;
  action_required?: boolean;
  date_from?: string;
  date_to?: string;
  search?: string;
  page?: number;
  per_page?: number;
}

export interface NotificationPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  notification_types: {
    attendance_alerts: boolean;
    justification_updates: boolean;
    message_notifications: boolean;
    system_announcements: boolean;
    grade_updates: boolean;
    schedule_changes: boolean;
  };
  quiet_hours: {
    enabled: boolean;
    start_time: string;
    end_time: string;
  };
}

export class NotificationService extends BaseApiService {
  private websocket: WebSocket | null = null;
  private notificationHandlers: Array<(notification: Notification) => void> = [];

  // Notification CRUD operations
  /**
   * Get notifications with pagination and filters
   */
  async getNotifications(filters?: NotificationFilters): Promise<PaginatedResponse<Notification>> {
    return this.getPaginated<Notification>('/notifications', filters);
  }

  /**
   * Get notification by ID
   */
  async getNotificationById(id: string): Promise<Notification> {
    return this.get<Notification>(`/notifications/${id}`);
  }

  /**
   * Create notification
   */
  async createNotification(data: CreateNotificationRequest): Promise<Notification> {
    return this.post<Notification>('/notifications', data);
  }

  /**
   * Create bulk notifications
   */
  async createBulkNotifications(data: BulkCreateNotificationRequest): Promise<Notification[]> {
    return this.post<Notification[]>('/notifications/bulk', data);
  }

  /**
   * Update notification
   */
  async updateNotification(id: string, data: Partial<CreateNotificationRequest>): Promise<Notification> {
    return this.put<Notification>(`/notifications/${id}`, data);
  }

  /**
   * Delete notification
   */
  async deleteNotification(id: string): Promise<void> {
    await this.delete(`/notifications/${id}`);
  }

  /**
   * Mark notification as read
   */
  async markAsRead(id: string): Promise<Notification> {
    return this.patch<Notification>(`/notifications/${id}/read`);
  }

  /**
   * Mark notification as unread
   */
  async markAsUnread(id: string): Promise<Notification> {
    return this.patch<Notification>(`/notifications/${id}/unread`);
  }

  /**
   * Mark all notifications as read for a user
   */
  async markAllAsRead(userId?: string): Promise<void> {
    const endpoint = userId ? `/notifications/user/${userId}/read-all` : '/notifications/read-all';
    await this.patch(endpoint);
  }

  // User-specific operations
  /**
   * Get notifications for current user
   */
  async getMyNotifications(filters?: Omit<NotificationFilters, 'user_id'>): Promise<PaginatedResponse<Notification>> {
    return this.getPaginated<Notification>('/notifications/me', filters);
  }

  /**
   * Get unread notifications for current user
   */
  async getMyUnreadNotifications(): Promise<Notification[]> {
    return this.get<Notification[]>('/notifications/me/unread');
  }

  /**
   * Get notification count for current user
   */
  async getMyNotificationCount(): Promise<{
    total: number;
    unread: number;
    by_type: Record<string, number>;
    by_priority: Record<string, number>;
  }> {
    return this.get('/notifications/me/count');
  }

  /**
   * Get notifications for specific user
   */
  async getUserNotifications(userId: string, filters?: Omit<NotificationFilters, 'user_id'>): Promise<PaginatedResponse<Notification>> {
    return this.getPaginated<Notification>(`/notifications/user/${userId}`, filters);
  }

  // Bulk operations
  /**
   * Bulk mark notifications as read
   */
  async bulkMarkAsRead(notificationIds: string[]): Promise<void> {
    await this.patch('/notifications/bulk-read', { notification_ids: notificationIds });
  }

  /**
   * Bulk delete notifications
   */
  async bulkDeleteNotifications(notificationIds: string[]): Promise<void> {
    await this.delete('/notifications/bulk', { data: { notification_ids: notificationIds } });
  }

  /**
   * Delete all read notifications for user
   */
  async deleteAllRead(userId?: string): Promise<void> {
    const endpoint = userId ? `/notifications/user/${userId}/delete-read` : '/notifications/me/delete-read';
    await this.delete(endpoint);
  }

  // Notification preferences
  /**
   * Get user notification preferences
   */
  async getNotificationPreferences(userId?: string): Promise<NotificationPreferences> {
    const endpoint = userId ? `/notifications/preferences/${userId}` : '/notifications/preferences/me';
    return this.get<NotificationPreferences>(endpoint);
  }

  /**
   * Update user notification preferences
   */
  async updateNotificationPreferences(preferences: Partial<NotificationPreferences>, userId?: string): Promise<NotificationPreferences> {
    const endpoint = userId ? `/notifications/preferences/${userId}` : '/notifications/preferences/me';
    return this.put<NotificationPreferences>(endpoint, preferences);
  }

  // Statistics and analytics
  /**
   * Get notification statistics
   */
  async getNotificationStats(filters?: {
    user_id?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<{
    total_notifications: number;
    read_notifications: number;
    unread_notifications: number;
    notifications_by_type: Record<string, number>;
    notifications_by_priority: Record<string, number>;
    average_read_time_hours: number;
    most_active_users: Array<{
      user_id: string;
      user_name: string;
      notification_count: number;
    }>;
  }> {
    return this.get('/notifications/stats', { params: filters });
  }

  // System notifications
  /**
   * Send system-wide notification
   */
  async sendSystemNotification(data: {
    title: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success';
    priority: 'low' | 'normal' | 'high' | 'urgent';
    target_roles?: string[];
    target_users?: string[];
    action_url?: string;
    expires_at?: string;
  }): Promise<Notification[]> {
    return this.post<Notification[]>('/notifications/system', data);
  }

  /**
   * Send attendance alert notifications
   */
  async sendAttendanceAlerts(data: {
    student_ids: string[];
    alert_type: 'absence' | 'late' | 'low_attendance';
    message: string;
  }): Promise<Notification[]> {
    return this.post<Notification[]>('/notifications/attendance-alerts', data);
  }

  /**
   * Send justification notifications
   */
  async sendJustificationNotifications(data: {
    justification_id: string;
    notification_type: 'submitted' | 'approved' | 'rejected' | 'reminder';
    recipients: string[];
  }): Promise<Notification[]> {
    return this.post<Notification[]>('/notifications/justification', data);
  }

  // Real-time WebSocket functionality
  /**
   * Connect to WebSocket for real-time notifications
   */
  connectWebSocket(): void {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No access token available for WebSocket connection');
      return;
    }

    const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/notifications?token=${token}`;
    
    this.websocket = new WebSocket(wsUrl);

    this.websocket.onopen = () => {
      console.log('WebSocket connected for notifications');
    };

    this.websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'new_notification') {
          this.notificationHandlers.forEach(handler => handler(data.notification));
          
          // Show browser notification if permission granted
          this.showBrowserNotification(data.notification);
        }
      } catch (error) {
        console.error('Error parsing WebSocket notification:', error);
      }
    };

    this.websocket.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        if (this.websocket?.readyState === WebSocket.CLOSED) {
          this.connectWebSocket();
        }
      }, 5000);
    };

    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  /**
   * Disconnect WebSocket
   */
  disconnectWebSocket(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }

  /**
   * Subscribe to new notifications
   */
  onNewNotification(handler: (notification: Notification) => void): () => void {
    this.notificationHandlers.push(handler);
    
    // Return unsubscribe function
    return () => {
      const index = this.notificationHandlers.indexOf(handler);
      if (index > -1) {
        this.notificationHandlers.splice(index, 1);
      }
    };
  }

  // Browser notifications
  /**
   * Request browser notification permission
   */
  async requestNotificationPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) {
      console.warn('This browser does not support notifications');
      return 'denied';
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission;
    }

    return Notification.permission;
  }

  /**
   * Show browser notification
   */
  private showBrowserNotification(notification: Notification): void {
    if (Notification.permission === 'granted') {
      const browserNotification = new window.Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        tag: notification.id,
        requireInteraction: notification.priority === 'urgent',
      });

      browserNotification.onclick = () => {
        window.focus();
        if (notification.action_url) {
          window.location.href = notification.action_url;
        }
        browserNotification.close();
      };

      // Auto-close after 5 seconds for non-urgent notifications
      if (notification.priority !== 'urgent') {
        setTimeout(() => {
          browserNotification.close();
        }, 5000);
      }
    }
  }

  /**
   * Test notification system
   */
  async testNotification(): Promise<void> {
    await this.createNotification({
      user_id: 'current',
      title: 'Test Notification',
      message: 'This is a test notification to verify the system is working.',
      type: 'info',
      priority: 'normal',
    });
  }
}

// Export singleton instance
export const notificationService = new NotificationService();
