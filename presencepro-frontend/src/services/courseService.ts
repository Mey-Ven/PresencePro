/**
 * Course Service
 * Handles course management, scheduling, and class operations
 */

import { BaseApiService, Course, CourseSchedule, Class, PaginatedResponse } from './api';

export interface CreateCourseRequest {
  name: string;
  description?: string;
  teacher_id: string;
  class_id: string;
  schedule: Omit<CourseSchedule, 'id' | 'course_id'>[];
  is_active?: boolean;
}

export interface UpdateCourseRequest {
  name?: string;
  description?: string;
  teacher_id?: string;
  class_id?: string;
  is_active?: boolean;
}

export interface CreateClassRequest {
  name: string;
  level: string;
  description?: string;
  teacher_id: string;
  is_active?: boolean;
}

export interface UpdateClassRequest {
  name?: string;
  level?: string;
  description?: string;
  teacher_id?: string;
  is_active?: boolean;
}

export interface CourseFilters {
  teacher_id?: string;
  class_id?: string;
  is_active?: boolean;
  search?: string;
  page?: number;
  per_page?: number;
}

export interface ClassFilters {
  teacher_id?: string;
  level?: string;
  is_active?: boolean;
  search?: string;
  page?: number;
  per_page?: number;
}

export interface ScheduleFilters {
  teacher_id?: string;
  class_id?: string;
  course_id?: string;
  day_of_week?: number;
  date_from?: string;
  date_to?: string;
}

export class CourseService extends BaseApiService {
  // Course CRUD operations
  async getCourses(filters?: CourseFilters): Promise<PaginatedResponse<Course>> {
    return this.getPaginated<Course>('/courses', filters);
  }

  async getCourseById(id: string): Promise<Course> {
    return this.get<Course>(`/courses/${id}`);
  }

  async createCourse(data: CreateCourseRequest): Promise<Course> {
    return this.post<Course>('/courses', data);
  }

  async updateCourse(id: string, data: UpdateCourseRequest): Promise<Course> {
    return this.put<Course>(`/courses/${id}`, data);
  }

  async deleteCourse(id: string): Promise<void> {
    await this.delete(`/courses/${id}`);
  }

  async activateCourse(id: string): Promise<Course> {
    return this.patch<Course>(`/courses/${id}/activate`);
  }

  async deactivateCourse(id: string): Promise<Course> {
    return this.patch<Course>(`/courses/${id}/deactivate`);
  }

  // Class CRUD operations
  async getClasses(filters?: ClassFilters): Promise<PaginatedResponse<Class>> {
    return this.getPaginated<Class>('/classes', filters);
  }

  async getClassById(id: string): Promise<Class> {
    return this.get<Class>(`/classes/${id}`);
  }

  async createClass(data: CreateClassRequest): Promise<Class> {
    return this.post<Class>('/classes', data);
  }

  async updateClass(id: string, data: UpdateClassRequest): Promise<Class> {
    return this.put<Class>(`/classes/${id}`, data);
  }

  async deleteClass(id: string): Promise<void> {
    await this.delete(`/classes/${id}`);
  }

  // Course schedule operations
  async getCourseSchedule(courseId: string): Promise<CourseSchedule[]> {
    return this.get<CourseSchedule[]>(`/courses/${courseId}/schedule`);
  }

  async updateCourseSchedule(courseId: string, schedule: Omit<CourseSchedule, 'id' | 'course_id'>[]): Promise<CourseSchedule[]> {
    return this.put<CourseSchedule[]>(`/courses/${courseId}/schedule`, { schedule });
  }

  async addScheduleSession(courseId: string, session: Omit<CourseSchedule, 'id' | 'course_id'>): Promise<CourseSchedule> {
    return this.post<CourseSchedule>(`/courses/${courseId}/schedule`, session);
  }

  async updateScheduleSession(courseId: string, sessionId: string, session: Partial<Omit<CourseSchedule, 'id' | 'course_id'>>): Promise<CourseSchedule> {
    return this.put<CourseSchedule>(`/courses/${courseId}/schedule/${sessionId}`, session);
  }

  async deleteScheduleSession(courseId: string, sessionId: string): Promise<void> {
    await this.delete(`/courses/${courseId}/schedule/${sessionId}`);
  }

  // Teacher-specific operations
  async getTeacherCourses(teacherId: string, filters?: Omit<CourseFilters, 'teacher_id'>): Promise<PaginatedResponse<Course>> {
    return this.getPaginated<Course>(`/teachers/${teacherId}/courses`, filters);
  }

  async getTeacherClasses(teacherId: string, filters?: Omit<ClassFilters, 'teacher_id'>): Promise<PaginatedResponse<Class>> {
    return this.getPaginated<Class>(`/teachers/${teacherId}/classes`, filters);
  }

  async getTeacherSchedule(teacherId: string, filters?: ScheduleFilters): Promise<Array<{
    course_id: string;
    course_name: string;
    class_id: string;
    class_name: string;
    day_of_week: number;
    start_time: string;
    end_time: string;
    room: string;
  }>> {
    return this.get(`/teachers/${teacherId}/schedule`, { params: filters });
  }

  // Class-specific operations
  async getClassCourses(classId: string, filters?: Omit<CourseFilters, 'class_id'>): Promise<PaginatedResponse<Course>> {
    return this.getPaginated<Course>(`/classes/${classId}/courses`, filters);
  }

  async getClassSchedule(classId: string, filters?: ScheduleFilters): Promise<Array<{
    course_id: string;
    course_name: string;
    teacher_id: string;
    teacher_name: string;
    day_of_week: number;
    start_time: string;
    end_time: string;
    room: string;
  }>> {
    return this.get(`/classes/${classId}/schedule`, { params: filters });
  }

  // Schedule operations
  async getWeeklySchedule(filters?: ScheduleFilters): Promise<{
    [key: string]: Array<{
      course_id: string;
      course_name: string;
      teacher_name: string;
      class_name: string;
      start_time: string;
      end_time: string;
      room: string;
    }>;
  }> {
    return this.get('/schedule/weekly', { params: filters });
  }

  async getDailySchedule(date: string, filters?: Omit<ScheduleFilters, 'date_from' | 'date_to'>): Promise<Array<{
    course_id: string;
    course_name: string;
    teacher_id: string;
    teacher_name: string;
    class_id: string;
    class_name: string;
    start_time: string;
    end_time: string;
    room: string;
  }>> {
    return this.get('/schedule/daily', { params: { date, ...filters } });
  }

  // Statistics and analytics
  async getCourseStats(): Promise<{
    total_courses: number;
    active_courses: number;
    inactive_courses: number;
    total_classes: number;
    active_classes: number;
    courses_by_level: Array<{ level: string; count: number }>;
    courses_by_teacher: Array<{ teacher_name: string; count: number }>;
  }> {
    return this.get('/courses/stats');
  }

  async getClassStats(): Promise<{
    total_classes: number;
    active_classes: number;
    inactive_classes: number;
    total_students: number;
    average_class_size: number;
    classes_by_level: Array<{ level: string; count: number }>;
    largest_classes: Array<{ class_name: string; student_count: number }>;
  }> {
    return this.get('/classes/stats');
  }

  // Search operations
  async searchCourses(query: string): Promise<Course[]> {
    return this.get<Course[]>('/courses/search', { params: { q: query } });
  }

  async searchClasses(query: string): Promise<Class[]> {
    return this.get<Class[]>('/classes/search', { params: { q: query } });
  }

  // Bulk operations
  async bulkCreateCourses(courses: CreateCourseRequest[]): Promise<Course[]> {
    return this.post<Course[]>('/courses/bulk', { courses });
  }

  async bulkUpdateCourses(updates: Array<{ id: string; data: UpdateCourseRequest }>): Promise<Course[]> {
    return this.put<Course[]>('/courses/bulk', { updates });
  }

  async bulkDeleteCourses(courseIds: string[]): Promise<void> {
    await this.delete('/courses/bulk', { data: { course_ids: courseIds } });
  }

  // Import/Export
  async importCourses(file: File): Promise<{ success: number; errors: string[] }> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.post<{ success: number; errors: string[] }>('/courses/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  async exportCourses(filters?: CourseFilters): Promise<Blob> {
    return this.get<Blob>('/courses/export', {
      params: filters,
      responseType: 'blob',
    });
  }

  async exportSchedule(filters?: ScheduleFilters): Promise<Blob> {
    return this.get<Blob>('/schedule/export', {
      params: filters,
      responseType: 'blob',
    });
  }

  // Room management
  async getRooms(): Promise<Array<{ id: string; name: string; capacity: number; is_available: boolean }>> {
    return this.get('/rooms');
  }

  async checkRoomAvailability(room: string, date: string, startTime: string, endTime: string): Promise<{ is_available: boolean; conflicts?: Array<{ course_name: string; start_time: string; end_time: string }> }> {
    return this.get('/rooms/availability', {
      params: { room, date, start_time: startTime, end_time: endTime },
    });
  }
}

// Export singleton instance
export const courseService = new CourseService();
