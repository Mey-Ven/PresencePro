// Types pour l'authentification
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

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

// Types pour les étudiants
export interface Student {
  id: string;
  user_id: string;
  student_number: string;
  class_id: string;
  parent_id?: string;
  enrollment_date: string;
  is_active: boolean;
  user: User;
  class?: Class;
  parent?: Parent;
}

// Types pour les classes
export interface Class {
  id: string;
  name: string;
  level: string;
  teacher_id: string;
  academic_year: string;
  is_active: boolean;
  teacher?: Teacher;
  students?: Student[];
}

// Types pour les enseignants
export interface Teacher {
  id: string;
  user_id: string;
  employee_number: string;
  department: string;
  hire_date: string;
  is_active: boolean;
  user: User;
  classes?: Class[];
}

// Types pour les parents
export interface Parent {
  id: string;
  user_id: string;
  phone: string;
  address: string;
  emergency_contact: string;
  user: User;
  children?: Student[];
}

// Types pour les présences
export interface AttendanceRecord {
  id: string;
  student_id: string;
  course_id: string;
  date: string;
  status: 'present' | 'absent' | 'late' | 'excused';
  method: 'manual' | 'face_recognition' | 'qr_code';
  notes?: string;
  marked_by: string;
  marked_at: string;
  student?: Student;
  course?: Course;
}

export interface AttendanceStats {
  total_records: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  excused_count: number;
  attendance_rate: number;
}

// Types pour les cours
export interface Course {
  id: string;
  name: string;
  code: string;
  description?: string;
  teacher_id: string;
  class_id: string;
  schedule: string;
  is_active: boolean;
  teacher?: Teacher;
  class?: Class;
}

// Types pour les justifications
export interface Justification {
  id: string;
  student_id: string;
  title: string;
  description: string;
  justification_type: 'medical' | 'family' | 'transport' | 'personal' | 'academic';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'draft' | 'submitted' | 'parent_approved' | 'admin_validated' | 'rejected';
  absence_start_date: string;
  absence_end_date: string;
  course_id?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  student?: Student;
  course?: Course;
  documents?: JustificationDocument[];
}

export interface JustificationDocument {
  id: string;
  justification_id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
}

// Types pour les statistiques
export interface StudentStatistics {
  student_id: string;
  period_start: string;
  period_end: string;
  total_days: number;
  present_days: number;
  absent_days: number;
  late_days: number;
  attendance_rate: number;
  weekly_trends: WeeklyTrend[];
  course_breakdown: CourseBreakdown[];
  class_ranking: number;
  class_average: number;
}

export interface ClassStatistics {
  class_id: string;
  period_start: string;
  period_end: string;
  total_students: number;
  average_attendance_rate: number;
  student_rankings: StudentRanking[];
  weekly_trends: WeeklyTrend[];
  course_comparison: CourseComparison[];
}

export interface GlobalStatistics {
  period_start: string;
  period_end: string;
  total_students: number;
  total_classes: number;
  overall_attendance_rate: number;
  class_rankings: ClassRanking[];
  monthly_trends: MonthlyTrend[];
  top_performers: TopPerformer[];
}

export interface WeeklyTrend {
  week: string;
  attendance_rate: number;
  present_count: number;
  absent_count: number;
}

export interface MonthlyTrend {
  month: string;
  attendance_rate: number;
  present_count: number;
  absent_count: number;
}

export interface CourseBreakdown {
  course_id: string;
  course_name: string;
  attendance_rate: number;
  total_sessions: number;
  present_sessions: number;
}

export interface CourseComparison {
  course_id: string;
  course_name: string;
  class_average: number;
  attendance_rate: number;
}

export interface StudentRanking {
  student_id: string;
  student_name: string;
  attendance_rate: number;
  rank: number;
}

export interface ClassRanking {
  class_id: string;
  class_name: string;
  attendance_rate: number;
  rank: number;
}

export interface TopPerformer {
  student_id: string;
  student_name: string;
  class_name: string;
  attendance_rate: number;
}

// Types pour les graphiques
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
  fill?: boolean;
}

export interface ChartOptions {
  responsive: boolean;
  plugins: {
    title: {
      display: boolean;
      text: string;
    };
    legend: {
      display: boolean;
      position: 'top' | 'bottom' | 'left' | 'right';
    };
  };
  scales?: {
    y: {
      beginAtZero: boolean;
      max?: number;
    };
  };
}

// Types pour les API responses
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Types pour les filtres et recherche
export interface AttendanceFilters {
  student_id?: string;
  class_id?: string;
  course_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  method?: string;
}

export interface UserFilters {
  role?: string;
  is_active?: boolean;
  search?: string;
}

export interface JustificationFilters {
  student_id?: string;
  status?: string;
  type?: string;
  priority?: string;
  start_date?: string;
  end_date?: string;
}

// Types pour les notifications
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

// Types pour les paramètres de l'application
export interface AppSettings {
  theme: 'light' | 'dark';
  language: 'fr' | 'en';
  notifications_enabled: boolean;
  auto_refresh_interval: number;
}

// Types pour les erreurs
export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}

// Types pour les formulaires
export interface FormErrors {
  [key: string]: string | undefined;
}

export interface FormState<T> {
  data: T;
  errors: FormErrors;
  isSubmitting: boolean;
  isValid: boolean;
}

// Types pour les modals
export interface ModalProps {
  show: boolean;
  onHide: () => void;
  title: string;
  size?: 'sm' | 'lg' | 'xl';
}

// Types pour les tableaux
export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
}

export interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  pagination?: {
    current: number;
    total: number;
    pageSize: number;
    onChange: (page: number) => void;
  };
  onSort?: (key: keyof T, direction: 'asc' | 'desc') => void;
}

// Types pour les hooks
export interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  refetch: () => Promise<void>;
}

export interface UsePaginationResult {
  currentPage: number;
  totalPages: number;
  goToPage: (page: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  canGoNext: boolean;
  canGoPrev: boolean;
}
