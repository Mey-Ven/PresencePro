/**
 * Justification Service
 * Handles absence justification workflow and document management
 */

import { BaseApiService, Justification, JustificationAttachment, PaginatedResponse } from './api';

export interface CreateJustificationRequest {
  student_id: string;
  attendance_id: string;
  reason: string;
  description: string;
  attachments?: File[];
}

export interface UpdateJustificationRequest {
  reason?: string;
  description?: string;
}

export interface ReviewJustificationRequest {
  status: 'approved' | 'rejected';
  review_comments?: string;
}

export interface JustificationFilters {
  student_id?: string;
  attendance_id?: string;
  status?: 'pending' | 'approved' | 'rejected';
  submitted_by?: string;
  reviewed_by?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
  page?: number;
  per_page?: number;
}

export class JustificationService extends BaseApiService {
  /**
   * Get justifications with pagination and filters
   */
  async getJustifications(filters?: JustificationFilters): Promise<PaginatedResponse<Justification>> {
    return this.getPaginated<Justification>('/justifications', filters);
  }

  /**
   * Get justification by ID
   */
  async getJustificationById(id: string): Promise<Justification> {
    return this.get<Justification>(`/justifications/${id}`);
  }

  /**
   * Create a new justification
   */
  async createJustification(data: CreateJustificationRequest): Promise<Justification> {
    const formData = new FormData();
    
    // Add text fields
    formData.append('student_id', data.student_id);
    formData.append('attendance_id', data.attendance_id);
    formData.append('reason', data.reason);
    formData.append('description', data.description);
    
    // Add file attachments
    if (data.attachments && data.attachments.length > 0) {
      data.attachments.forEach((file, index) => {
        formData.append(`attachments[${index}]`, file);
      });
    }
    
    return this.post<Justification>('/justifications', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * Update justification (only allowed for pending justifications)
   */
  async updateJustification(id: string, data: UpdateJustificationRequest): Promise<Justification> {
    return this.put<Justification>(`/justifications/${id}`, data);
  }

  /**
   * Delete justification (only allowed for pending justifications)
   */
  async deleteJustification(id: string): Promise<void> {
    await this.delete(`/justifications/${id}`);
  }

  /**
   * Review justification (admin/teacher only)
   */
  async reviewJustification(id: string, data: ReviewJustificationRequest): Promise<Justification> {
    return this.patch<Justification>(`/justifications/${id}/review`, data);
  }

  /**
   * Get justifications for a specific student
   */
  async getStudentJustifications(studentId: string, filters?: Omit<JustificationFilters, 'student_id'>): Promise<PaginatedResponse<Justification>> {
    return this.getPaginated<Justification>(`/justifications/student/${studentId}`, filters);
  }

  /**
   * Get justifications for a specific attendance record
   */
  async getAttendanceJustifications(attendanceId: string): Promise<Justification[]> {
    return this.get<Justification[]>(`/justifications/attendance/${attendanceId}`);
  }

  /**
   * Get pending justifications for review
   */
  async getPendingJustifications(filters?: Omit<JustificationFilters, 'status'>): Promise<PaginatedResponse<Justification>> {
    return this.getPaginated<Justification>('/justifications/pending', filters);
  }

  /**
   * Get justifications submitted by a specific user (parent/student)
   */
  async getJustificationsBySubmitter(submitterId: string, filters?: Omit<JustificationFilters, 'submitted_by'>): Promise<PaginatedResponse<Justification>> {
    return this.getPaginated<Justification>(`/justifications/submitter/${submitterId}`, filters);
  }

  /**
   * Get justifications reviewed by a specific user (admin/teacher)
   */
  async getJustificationsByReviewer(reviewerId: string, filters?: Omit<JustificationFilters, 'reviewed_by'>): Promise<PaginatedResponse<Justification>> {
    return this.getPaginated<Justification>(`/justifications/reviewer/${reviewerId}`, filters);
  }

  // Attachment management
  /**
   * Add attachment to existing justification
   */
  async addAttachment(justificationId: string, file: File): Promise<JustificationAttachment> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.post<JustificationAttachment>(`/justifications/${justificationId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * Remove attachment from justification
   */
  async removeAttachment(justificationId: string, attachmentId: string): Promise<void> {
    await this.delete(`/justifications/${justificationId}/attachments/${attachmentId}`);
  }

  /**
   * Download attachment
   */
  async downloadAttachment(justificationId: string, attachmentId: string): Promise<Blob> {
    return this.get<Blob>(`/justifications/${justificationId}/attachments/${attachmentId}/download`, {
      responseType: 'blob',
    });
  }

  /**
   * Get attachment info
   */
  async getAttachmentInfo(justificationId: string, attachmentId: string): Promise<JustificationAttachment> {
    return this.get<JustificationAttachment>(`/justifications/${justificationId}/attachments/${attachmentId}`);
  }

  // Statistics and analytics
  /**
   * Get justification statistics
   */
  async getJustificationStats(filters?: {
    student_id?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<{
    total_justifications: number;
    pending_justifications: number;
    approved_justifications: number;
    rejected_justifications: number;
    approval_rate: number;
    average_review_time_hours: number;
    justifications_by_reason: Array<{ reason: string; count: number }>;
    justifications_by_month: Array<{ month: string; count: number }>;
  }> {
    return this.get('/justifications/stats', { params: filters });
  }

  /**
   * Get justification trends
   */
  async getJustificationTrends(period: 'week' | 'month' | 'semester' | 'year'): Promise<Array<{
    period: string;
    total_justifications: number;
    approved_justifications: number;
    rejected_justifications: number;
    approval_rate: number;
  }>> {
    return this.get('/justifications/trends', { params: { period } });
  }

  /**
   * Get students with frequent justifications
   */
  async getFrequentJustifiers(threshold: number = 5): Promise<Array<{
    student_id: string;
    student_name: string;
    class_name: string;
    justification_count: number;
    approval_rate: number;
    most_common_reason: string;
  }>> {
    return this.get('/justifications/frequent', { params: { threshold } });
  }

  // Bulk operations
  /**
   * Bulk review justifications
   */
  async bulkReviewJustifications(reviews: Array<{
    justification_id: string;
    status: 'approved' | 'rejected';
    review_comments?: string;
  }>): Promise<Justification[]> {
    return this.patch<Justification[]>('/justifications/bulk-review', { reviews });
  }

  /**
   * Bulk delete justifications
   */
  async bulkDeleteJustifications(justificationIds: string[]): Promise<void> {
    await this.delete('/justifications/bulk', { data: { justification_ids: justificationIds } });
  }

  // Export and reporting
  /**
   * Export justifications
   */
  async exportJustifications(filters?: JustificationFilters & {
    format: 'csv' | 'excel' | 'pdf';
  }): Promise<Blob> {
    return this.get<Blob>('/justifications/export', {
      params: filters,
      responseType: 'blob',
    });
  }

  /**
   * Generate justification report
   */
  async generateJustificationReport(filters?: {
    student_id?: string;
    class_id?: string;
    date_from?: string;
    date_to?: string;
    format: 'pdf' | 'excel';
  }): Promise<Blob> {
    return this.get<Blob>('/justifications/report', {
      params: filters,
      responseType: 'blob',
    });
  }

  // Workflow management
  /**
   * Get justification workflow status
   */
  async getWorkflowStatus(justificationId: string): Promise<{
    current_status: 'pending' | 'approved' | 'rejected';
    workflow_steps: Array<{
      step: string;
      status: 'completed' | 'current' | 'pending';
      completed_at?: string;
      completed_by?: string;
      comments?: string;
    }>;
  }> {
    return this.get(`/justifications/${justificationId}/workflow`);
  }

  /**
   * Get available justification reasons
   */
  async getJustificationReasons(): Promise<Array<{
    id: string;
    name: string;
    description: string;
    requires_document: boolean;
    auto_approve: boolean;
  }>> {
    return this.get('/justifications/reasons');
  }

  /**
   * Check if attendance can be justified
   */
  async canJustifyAttendance(attendanceId: string): Promise<{
    can_justify: boolean;
    reason?: string;
    deadline?: string;
  }> {
    return this.get(`/justifications/can-justify/${attendanceId}`);
  }
}

// Export singleton instance
export const justificationService = new JustificationService();
