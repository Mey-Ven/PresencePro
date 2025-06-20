// ============================================================================
// Types pour l'écosystème PresencePro
// ============================================================================

export type UserRole = 'admin' | 'teacher' | 'student' | 'parent';

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  profilePicture?: string;
  phone?: string;
  address?: string;
}

export interface Student extends User {
  role: 'student';
  studentId: string;
  classId?: string;
  parentIds: string[];
  enrollmentDate: string;
  graduationDate?: string;
}

export interface Teacher extends User {
  role: 'teacher';
  teacherId: string;
  department: string;
  subjects: string[];
  hireDate: string;
}

export interface Parent extends User {
  role: 'parent';
  parentId: string;
  childrenIds: string[];
  emergencyContact?: string;
}

export interface Admin extends User {
  role: 'admin';
  adminId: string;
  permissions: string[];
  lastLogin?: string;
}

// ============================================================================
// Types pour l'authentification
// ============================================================================

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// ============================================================================
// Types pour les cours et classes
// ============================================================================

export interface Course {
  id: string;
  name: string;
  code: string;
  description?: string;
  credits: number;
  teacherId: string;
  teacher?: Teacher;
  schedule: CourseSchedule[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CourseSchedule {
  id: string;
  courseId: string;
  dayOfWeek: number; // 0 = Dimanche, 1 = Lundi, etc.
  startTime: string; // Format HH:mm
  endTime: string;   // Format HH:mm
  classroom: string;
}

export interface Class {
  id: string;
  name: string;
  level: string;
  academicYear: string;
  studentIds: string[];
  students?: Student[];
  courseIds: string[];
  courses?: Course[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// ============================================================================
// Types pour les présences
// ============================================================================

export type AttendanceStatus = 'present' | 'absent' | 'late' | 'excused';

export interface AttendanceRecord {
  id: string;
  studentId: string;
  student?: Student;
  courseId: string;
  course?: Course;
  date: string;
  status: AttendanceStatus;
  markedAt: string;
  markedBy: string; // Teacher ID
  notes?: string;
  justificationId?: string;
}

export interface AttendanceSession {
  id: string;
  courseId: string;
  course?: Course;
  date: string;
  startTime: string;
  endTime: string;
  teacherId: string;
  teacher?: Teacher;
  records: AttendanceRecord[];
  isCompleted: boolean;
  createdAt: string;
}

// ============================================================================
// Types pour les justifications
// ============================================================================

export type JustificationStatus = 'pending' | 'approved' | 'rejected';
export type JustificationType = 'medical' | 'family' | 'personal' | 'other';

export interface Justification {
  id: string;
  studentId: string;
  student?: Student;
  attendanceRecordId: string;
  attendanceRecord?: AttendanceRecord;
  type: JustificationType;
  reason: string;
  description?: string;
  attachments: string[]; // URLs des fichiers
  status: JustificationStatus;
  submittedAt: string;
  submittedBy: string; // Student or Parent ID
  reviewedAt?: string;
  reviewedBy?: string; // Teacher or Admin ID
  reviewNotes?: string;
  parentApproval?: boolean;
  parentApprovedAt?: string;
  parentApprovedBy?: string;
}

// ============================================================================
// Types pour la messagerie
// ============================================================================

export type MessageType = 'text' | 'file' | 'notification';
export type MessageStatus = 'sent' | 'delivered' | 'read';

export interface Message {
  id: string;
  senderId: string;
  sender?: User;
  recipientId: string;
  recipient?: User;
  type: MessageType;
  content: string;
  attachments?: string[];
  status: MessageStatus;
  sentAt: string;
  readAt?: string;
  conversationId: string;
}

export interface Conversation {
  id: string;
  participants: string[]; // User IDs
  participantDetails?: User[];
  lastMessage?: Message;
  unreadCount: number;
  createdAt: string;
  updatedAt: string;
}

// ============================================================================
// Types pour les notifications
// ============================================================================

export type NotificationType = 'absence' | 'justification' | 'message' | 'system';
export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  priority: NotificationPriority;
  isRead: boolean;
  actionUrl?: string;
  metadata?: Record<string, any>;
  createdAt: string;
  readAt?: string;
}

// ============================================================================
// Types pour les statistiques
// ============================================================================

export interface AttendanceStats {
  totalStudents: number;
  presentCount: number;
  absentCount: number;
  lateCount: number;
  excusedCount: number;
  attendanceRate: number;
  period: {
    startDate: string;
    endDate: string;
  };
}

export interface StudentStats {
  studentId: string;
  student?: Student;
  totalClasses: number;
  presentCount: number;
  absentCount: number;
  lateCount: number;
  excusedCount: number;
  attendanceRate: number;
  trendData: {
    date: string;
    attendanceRate: number;
  }[];
}

export interface ClassStats {
  classId: string;
  class?: Class;
  attendanceStats: AttendanceStats;
  studentStats: StudentStats[];
  trendData: {
    date: string;
    attendanceRate: number;
  }[];
}

// ============================================================================
// Types pour l'API et les réponses
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
}

// ============================================================================
// Types pour les formulaires
// ============================================================================

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'select' | 'textarea' | 'file' | 'date' | 'time';
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
}

export interface FormState {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
}

// ============================================================================
// Types pour les filtres et recherche
// ============================================================================

export interface FilterOption {
  key: string;
  label: string;
  type: 'select' | 'date' | 'text' | 'boolean';
  options?: { value: string; label: string }[];
}

export interface SearchFilters {
  query?: string;
  role?: UserRole;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  classId?: string;
  courseId?: string;
  [key: string]: any;
}

export interface SortOption {
  field: string;
  direction: 'asc' | 'desc';
  label: string;
}
