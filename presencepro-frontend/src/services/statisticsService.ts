/**
 * Statistics Service
 * Handles analytics, reporting, and dashboard statistics
 */

import { BaseApiService, DashboardStats, ActivityItem, AttendanceStats } from './api';

export interface StatisticsFilters {
  date_from?: string;
  date_to?: string;
  student_id?: string;
  teacher_id?: string;
  class_id?: string;
  course_id?: string;
  period?: 'day' | 'week' | 'month' | 'semester' | 'year';
}

export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }>;
}

export interface TrendData {
  period: string;
  value: number;
  change_percentage?: number;
  comparison_period?: string;
}

export class StatisticsService extends BaseApiService {
  // Dashboard statistics
  /**
   * Get dashboard statistics for admin
   */
  async getAdminDashboardStats(filters?: StatisticsFilters): Promise<DashboardStats> {
    return this.get<DashboardStats>('/statistics/dashboard/admin', { params: filters });
  }

  /**
   * Get dashboard statistics for teacher
   */
  async getTeacherDashboardStats(teacherId: string, filters?: StatisticsFilters): Promise<{
    total_students: number;
    total_courses: number;
    total_classes: number;
    today_attendance_rate: number;
    weekly_attendance_rate: number;
    monthly_attendance_rate: number;
    pending_justifications: number;
    unread_messages: number;
    recent_activity: ActivityItem[];
    my_classes: Array<{
      class_id: string;
      class_name: string;
      student_count: number;
      attendance_rate: number;
      recent_absences: number;
    }>;
  }> {
    return this.get(`/statistics/dashboard/teacher/${teacherId}`, { params: filters });
  }

  /**
   * Get dashboard statistics for student
   */
  async getStudentDashboardStats(studentId: string, filters?: StatisticsFilters): Promise<{
    total_courses: number;
    attendance_rate: number;
    total_absences: number;
    justified_absences: number;
    unjustified_absences: number;
    recent_grades: Array<{
      course_name: string;
      grade: number;
      date: string;
    }>;
    upcoming_sessions: Array<{
      course_name: string;
      date: string;
      start_time: string;
      end_time: string;
      room: string;
    }>;
    recent_activity: ActivityItem[];
  }> {
    return this.get(`/statistics/dashboard/student/${studentId}`, { params: filters });
  }

  /**
   * Get dashboard statistics for parent
   */
  async getParentDashboardStats(parentId: string, filters?: StatisticsFilters): Promise<{
    children: Array<{
      student_id: string;
      student_name: string;
      class_name: string;
      attendance_rate: number;
      recent_absences: number;
      pending_justifications: number;
    }>;
    unread_messages: number;
    unread_notifications: number;
    recent_activity: ActivityItem[];
  }> {
    return this.get(`/statistics/dashboard/parent/${parentId}`, { params: filters });
  }

  // Attendance statistics
  /**
   * Get global attendance statistics
   */
  async getGlobalAttendanceStats(filters?: StatisticsFilters): Promise<AttendanceStats & {
    attendance_by_class: Array<{
      class_id: string;
      class_name: string;
      attendance_rate: number;
      total_students: number;
      present_students: number;
      absent_students: number;
    }>;
    attendance_by_course: Array<{
      course_id: string;
      course_name: string;
      attendance_rate: number;
      total_sessions: number;
      present_sessions: number;
      absent_sessions: number;
    }>;
  }> {
    return this.get('/statistics/attendance/global', { params: filters });
  }

  /**
   * Get attendance trends over time
   */
  async getAttendanceTrends(filters?: StatisticsFilters): Promise<TrendData[]> {
    return this.get<TrendData[]>('/statistics/attendance/trends', { params: filters });
  }

  /**
   * Get attendance comparison between periods
   */
  async getAttendanceComparison(filters?: StatisticsFilters & {
    compare_period: 'previous_week' | 'previous_month' | 'previous_semester' | 'previous_year';
  }): Promise<{
    current_period: AttendanceStats;
    comparison_period: AttendanceStats;
    improvement_percentage: number;
  }> {
    return this.get('/statistics/attendance/comparison', { params: filters });
  }

  // Chart data for visualizations
  /**
   * Get attendance chart data
   */
  async getAttendanceChartData(filters?: StatisticsFilters & {
    chart_type: 'line' | 'bar' | 'pie' | 'doughnut';
    group_by: 'day' | 'week' | 'month' | 'class' | 'course';
  }): Promise<ChartData> {
    return this.get<ChartData>('/statistics/charts/attendance', { params: filters });
  }

  /**
   * Get justification chart data
   */
  async getJustificationChartData(filters?: StatisticsFilters & {
    chart_type: 'line' | 'bar' | 'pie' | 'doughnut';
    group_by: 'day' | 'week' | 'month' | 'status' | 'reason';
  }): Promise<ChartData> {
    return this.get<ChartData>('/statistics/charts/justifications', { params: filters });
  }

  /**
   * Get user activity chart data
   */
  async getUserActivityChartData(filters?: StatisticsFilters & {
    chart_type: 'line' | 'bar';
    group_by: 'day' | 'week' | 'month' | 'role';
  }): Promise<ChartData> {
    return this.get<ChartData>('/statistics/charts/user-activity', { params: filters });
  }

  // Performance analytics
  /**
   * Get class performance statistics
   */
  async getClassPerformanceStats(classId: string, filters?: StatisticsFilters): Promise<{
    class_info: {
      class_id: string;
      class_name: string;
      student_count: number;
      teacher_name: string;
    };
    attendance_stats: AttendanceStats;
    top_performers: Array<{
      student_id: string;
      student_name: string;
      attendance_rate: number;
      total_absences: number;
    }>;
    students_at_risk: Array<{
      student_id: string;
      student_name: string;
      attendance_rate: number;
      consecutive_absences: number;
      risk_level: 'low' | 'medium' | 'high';
    }>;
    monthly_trends: TrendData[];
  }> {
    return this.get(`/statistics/performance/class/${classId}`, { params: filters });
  }

  /**
   * Get teacher performance statistics
   */
  async getTeacherPerformanceStats(teacherId: string, filters?: StatisticsFilters): Promise<{
    teacher_info: {
      teacher_id: string;
      teacher_name: string;
      subject: string;
      total_classes: number;
      total_students: number;
    };
    overall_attendance_rate: number;
    class_performance: Array<{
      class_id: string;
      class_name: string;
      attendance_rate: number;
      student_count: number;
    }>;
    course_performance: Array<{
      course_id: string;
      course_name: string;
      attendance_rate: number;
      session_count: number;
    }>;
    monthly_trends: TrendData[];
  }> {
    return this.get(`/statistics/performance/teacher/${teacherId}`, { params: filters });
  }

  /**
   * Get student performance statistics
   */
  async getStudentPerformanceStats(studentId: string, filters?: StatisticsFilters): Promise<{
    student_info: {
      student_id: string;
      student_name: string;
      class_name: string;
      enrollment_date: string;
    };
    attendance_stats: AttendanceStats;
    course_performance: Array<{
      course_id: string;
      course_name: string;
      teacher_name: string;
      attendance_rate: number;
      total_sessions: number;
      absent_sessions: number;
    }>;
    justification_stats: {
      total_justifications: number;
      approved_justifications: number;
      rejected_justifications: number;
      pending_justifications: number;
    };
    monthly_trends: TrendData[];
    attendance_patterns: {
      most_absent_day: string;
      most_absent_time: string;
      absence_reasons: Array<{ reason: string; count: number }>;
    };
  }> {
    return this.get(`/statistics/performance/student/${studentId}`, { params: filters });
  }

  // Reporting
  /**
   * Generate attendance report
   */
  async generateAttendanceReport(filters?: StatisticsFilters & {
    format: 'pdf' | 'excel' | 'csv';
    include_charts: boolean;
    include_details: boolean;
  }): Promise<Blob> {
    return this.get<Blob>('/statistics/reports/attendance', {
      params: filters,
      responseType: 'blob',
    });
  }

  /**
   * Generate performance report
   */
  async generatePerformanceReport(filters?: StatisticsFilters & {
    format: 'pdf' | 'excel' | 'csv';
    report_type: 'class' | 'teacher' | 'student' | 'global';
    entity_id?: string;
  }): Promise<Blob> {
    return this.get<Blob>('/statistics/reports/performance', {
      params: filters,
      responseType: 'blob',
    });
  }

  /**
   * Generate custom report
   */
  async generateCustomReport(config: {
    title: string;
    description?: string;
    filters: StatisticsFilters;
    metrics: string[];
    charts: Array<{
      type: 'line' | 'bar' | 'pie' | 'doughnut';
      metric: string;
      group_by: string;
    }>;
    format: 'pdf' | 'excel';
  }): Promise<Blob> {
    return this.post<Blob>('/statistics/reports/custom', config, {
      responseType: 'blob',
    });
  }

  // Real-time statistics
  /**
   * Get real-time attendance statistics
   */
  async getRealtimeAttendanceStats(): Promise<{
    current_sessions: number;
    completed_sessions: number;
    pending_sessions: number;
    total_students_present: number;
    total_students_absent: number;
    current_attendance_rate: number;
    last_updated: string;
  }> {
    return this.get('/statistics/realtime/attendance');
  }

  /**
   * Get system health statistics
   */
  async getSystemHealthStats(): Promise<{
    total_users: number;
    active_users_today: number;
    active_users_this_week: number;
    total_sessions_today: number;
    system_uptime: number;
    database_health: 'healthy' | 'warning' | 'critical';
    api_response_time_ms: number;
    last_backup: string;
  }> {
    return this.get('/statistics/system/health');
  }

  // Export and scheduling
  /**
   * Schedule recurring report
   */
  async scheduleReport(config: {
    name: string;
    report_type: 'attendance' | 'performance' | 'custom';
    filters: StatisticsFilters;
    schedule: 'daily' | 'weekly' | 'monthly';
    recipients: string[];
    format: 'pdf' | 'excel';
  }): Promise<{ schedule_id: string }> {
    return this.post('/statistics/schedule-report', config);
  }

  /**
   * Get scheduled reports
   */
  async getScheduledReports(): Promise<Array<{
    schedule_id: string;
    name: string;
    report_type: string;
    schedule: string;
    next_run: string;
    last_run?: string;
    is_active: boolean;
  }>> {
    return this.get('/statistics/scheduled-reports');
  }

  /**
   * Cancel scheduled report
   */
  async cancelScheduledReport(scheduleId: string): Promise<void> {
    await this.delete(`/statistics/scheduled-reports/${scheduleId}`);
  }
}

// Export singleton instance
export const statisticsService = new StatisticsService();
