/**
 * API Service Layer for PresencePro Frontend
 * Handles all HTTP requests to backend microservices
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_VERSION}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}${API_VERSION}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Generic API response interface
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: string;
}

// Pagination interface
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Error interface
export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}

// Base API service class
export class BaseApiService {
  protected async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.get<ApiResponse<T>>(url, config);
    return response.data.data;
  }

  protected async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.post<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  protected async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.put<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  protected async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.patch<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  protected async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.delete<ApiResponse<T>>(url, config);
    return response.data.data;
  }

  protected async getPaginated<T>(
    url: string,
    params?: any,
    config?: AxiosRequestConfig
  ): Promise<PaginatedResponse<T>> {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<T>>>(url, {
      ...config,
      params,
    });
    return response.data.data;
  }
}

// Authentication interfaces
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'teacher' | 'student' | 'parent';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Student interface
export interface Student {
  id: string;
  student_number: string;
  first_name: string;
  last_name: string;
  email: string;
  date_of_birth: string;
  class_id: string;
  class_name?: string;
  parent_ids: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Teacher interface
export interface Teacher {
  id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  subject: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Parent interface
export interface Parent {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  student_ids: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Course interface
export interface Course {
  id: string;
  name: string;
  description?: string;
  teacher_id: string;
  teacher_name?: string;
  class_id: string;
  class_name?: string;
  schedule: CourseSchedule[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Course schedule interface
export interface CourseSchedule {
  id: string;
  course_id: string;
  day_of_week: number; // 0 = Monday, 6 = Sunday
  start_time: string;
  end_time: string;
  room: string;
}

// Class interface
export interface Class {
  id: string;
  name: string;
  level: string;
  description?: string;
  teacher_id: string;
  teacher_name?: string;
  student_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Attendance interface
export interface AttendanceRecord {
  id: string;
  student_id: string;
  student_name?: string;
  course_id: string;
  course_name?: string;
  teacher_id: string;
  teacher_name?: string;
  date: string;
  start_time: string;
  end_time: string;
  status: 'present' | 'absent' | 'late' | 'justified';
  marked_at?: string;
  marked_by?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Justification interface
export interface Justification {
  id: string;
  student_id: string;
  student_name?: string;
  attendance_id: string;
  reason: string;
  description: string;
  status: 'pending' | 'approved' | 'rejected';
  submitted_by: string;
  submitted_at: string;
  reviewed_by?: string;
  reviewed_at?: string;
  review_comments?: string;
  attachments: JustificationAttachment[];
  created_at: string;
  updated_at: string;
}

// Justification attachment interface
export interface JustificationAttachment {
  id: string;
  justification_id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
}

// Message interface
export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  sender_name?: string;
  sender_role?: string;
  content: string;
  message_type: 'text' | 'file' | 'system';
  is_read: boolean;
  read_at?: string;
  attachments: MessageAttachment[];
  created_at: string;
  updated_at: string;
}

// Message attachment interface
export interface MessageAttachment {
  id: string;
  message_id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
}

// Conversation interface
export interface Conversation {
  id: string;
  subject: string;
  participants: ConversationParticipant[];
  last_message?: Message;
  unread_count: number;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

// Conversation participant interface
export interface ConversationParticipant {
  id: string;
  conversation_id: string;
  user_id: string;
  user_name?: string;
  user_role?: string;
  joined_at: string;
  last_read_at?: string;
}

// Notification interface
export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  is_read: boolean;
  read_at?: string;
  action_url?: string;
  action_required: boolean;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

// Statistics interfaces
export interface AttendanceStats {
  total_sessions: number;
  present_sessions: number;
  absent_sessions: number;
  late_sessions: number;
  justified_sessions: number;
  attendance_rate: number;
  period_start: string;
  period_end: string;
}

export interface DashboardStats {
  total_students: number;
  total_teachers: number;
  total_parents: number;
  total_courses: number;
  total_classes: number;
  today_attendance_rate: number;
  weekly_attendance_rate: number;
  monthly_attendance_rate: number;
  pending_justifications: number;
  unread_messages: number;
  recent_activity: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  type: 'attendance' | 'justification' | 'message' | 'user_created' | 'course_created';
  message: string;
  user_name?: string;
  timestamp: string;
  metadata?: any;
}

export default apiClient;
