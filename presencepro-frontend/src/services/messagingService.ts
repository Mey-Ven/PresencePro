/**
 * Messaging Service
 * Handles real-time messaging, conversations, and notifications
 */

import { BaseApiService, Message, MessageAttachment, Conversation, ConversationParticipant, PaginatedResponse } from './api';

export interface CreateConversationRequest {
  subject: string;
  participant_ids: string[];
  initial_message?: string;
  attachments?: File[];
}

export interface SendMessageRequest {
  conversation_id: string;
  content: string;
  message_type?: 'text' | 'file' | 'system';
  attachments?: File[];
}

export interface ConversationFilters {
  participant_id?: string;
  is_archived?: boolean;
  has_unread?: boolean;
  search?: string;
  page?: number;
  per_page?: number;
}

export interface MessageFilters {
  conversation_id?: string;
  sender_id?: string;
  message_type?: 'text' | 'file' | 'system';
  is_read?: boolean;
  date_from?: string;
  date_to?: string;
  page?: number;
  per_page?: number;
}

export class MessagingService extends BaseApiService {
  private websocket: WebSocket | null = null;
  private messageHandlers: Array<(message: Message) => void> = [];
  private conversationHandlers: Array<(conversation: Conversation) => void> = [];

  // Conversation management
  /**
   * Get conversations with pagination and filters
   */
  async getConversations(filters?: ConversationFilters): Promise<PaginatedResponse<Conversation>> {
    return this.getPaginated<Conversation>('/conversations', filters);
  }

  /**
   * Get conversation by ID
   */
  async getConversationById(id: string): Promise<Conversation> {
    return this.get<Conversation>(`/conversations/${id}`);
  }

  /**
   * Create new conversation
   */
  async createConversation(data: CreateConversationRequest): Promise<Conversation> {
    const formData = new FormData();
    
    formData.append('subject', data.subject);
    formData.append('participant_ids', JSON.stringify(data.participant_ids));
    
    if (data.initial_message) {
      formData.append('initial_message', data.initial_message);
    }
    
    if (data.attachments && data.attachments.length > 0) {
      data.attachments.forEach((file, index) => {
        formData.append(`attachments[${index}]`, file);
      });
    }
    
    return this.post<Conversation>('/conversations', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * Update conversation
   */
  async updateConversation(id: string, data: { subject?: string }): Promise<Conversation> {
    return this.put<Conversation>(`/conversations/${id}`, data);
  }

  /**
   * Archive conversation
   */
  async archiveConversation(id: string): Promise<Conversation> {
    return this.patch<Conversation>(`/conversations/${id}/archive`);
  }

  /**
   * Unarchive conversation
   */
  async unarchiveConversation(id: string): Promise<Conversation> {
    return this.patch<Conversation>(`/conversations/${id}/unarchive`);
  }

  /**
   * Delete conversation
   */
  async deleteConversation(id: string): Promise<void> {
    await this.delete(`/conversations/${id}`);
  }

  /**
   * Add participant to conversation
   */
  async addParticipant(conversationId: string, userId: string): Promise<ConversationParticipant> {
    return this.post<ConversationParticipant>(`/conversations/${conversationId}/participants`, {
      user_id: userId,
    });
  }

  /**
   * Remove participant from conversation
   */
  async removeParticipant(conversationId: string, userId: string): Promise<void> {
    await this.delete(`/conversations/${conversationId}/participants/${userId}`);
  }

  /**
   * Mark conversation as read
   */
  async markConversationAsRead(conversationId: string): Promise<void> {
    await this.patch(`/conversations/${conversationId}/read`);
  }

  // Message management
  /**
   * Get messages in conversation
   */
  async getMessages(conversationId: string, filters?: Omit<MessageFilters, 'conversation_id'>): Promise<PaginatedResponse<Message>> {
    return this.getPaginated<Message>(`/conversations/${conversationId}/messages`, filters);
  }

  /**
   * Get message by ID
   */
  async getMessageById(conversationId: string, messageId: string): Promise<Message> {
    return this.get<Message>(`/conversations/${conversationId}/messages/${messageId}`);
  }

  /**
   * Send message
   */
  async sendMessage(data: SendMessageRequest): Promise<Message> {
    const formData = new FormData();
    
    formData.append('content', data.content);
    formData.append('message_type', data.message_type || 'text');
    
    if (data.attachments && data.attachments.length > 0) {
      data.attachments.forEach((file, index) => {
        formData.append(`attachments[${index}]`, file);
      });
    }
    
    return this.post<Message>(`/conversations/${data.conversation_id}/messages`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * Update message (only content, within time limit)
   */
  async updateMessage(conversationId: string, messageId: string, content: string): Promise<Message> {
    return this.put<Message>(`/conversations/${conversationId}/messages/${messageId}`, {
      content,
    });
  }

  /**
   * Delete message
   */
  async deleteMessage(conversationId: string, messageId: string): Promise<void> {
    await this.delete(`/conversations/${conversationId}/messages/${messageId}`);
  }

  /**
   * Mark message as read
   */
  async markMessageAsRead(conversationId: string, messageId: string): Promise<void> {
    await this.patch(`/conversations/${conversationId}/messages/${messageId}/read`);
  }

  /**
   * Mark all messages in conversation as read
   */
  async markAllMessagesAsRead(conversationId: string): Promise<void> {
    await this.patch(`/conversations/${conversationId}/messages/read-all`);
  }

  // Attachment management
  /**
   * Download message attachment
   */
  async downloadAttachment(conversationId: string, messageId: string, attachmentId: string): Promise<Blob> {
    return this.get<Blob>(`/conversations/${conversationId}/messages/${messageId}/attachments/${attachmentId}/download`, {
      responseType: 'blob',
    });
  }

  /**
   * Get attachment info
   */
  async getAttachmentInfo(conversationId: string, messageId: string, attachmentId: string): Promise<MessageAttachment> {
    return this.get<MessageAttachment>(`/conversations/${conversationId}/messages/${messageId}/attachments/${attachmentId}`);
  }

  // Search and filtering
  /**
   * Search conversations
   */
  async searchConversations(query: string): Promise<Conversation[]> {
    return this.get<Conversation[]>('/conversations/search', { params: { q: query } });
  }

  /**
   * Search messages
   */
  async searchMessages(query: string, conversationId?: string): Promise<Message[]> {
    return this.get<Message[]>('/messages/search', {
      params: { q: query, conversation_id: conversationId },
    });
  }

  // Statistics
  /**
   * Get messaging statistics
   */
  async getMessagingStats(): Promise<{
    total_conversations: number;
    active_conversations: number;
    archived_conversations: number;
    total_messages: number;
    unread_messages: number;
    messages_today: number;
    messages_this_week: number;
    average_response_time_hours: number;
  }> {
    return this.get('/messaging/stats');
  }

  /**
   * Get user messaging stats
   */
  async getUserMessagingStats(userId: string): Promise<{
    total_conversations: number;
    unread_conversations: number;
    total_messages_sent: number;
    total_messages_received: number;
    average_response_time_hours: number;
    most_active_conversations: Array<{
      conversation_id: string;
      subject: string;
      message_count: number;
    }>;
  }> {
    return this.get(`/messaging/stats/user/${userId}`);
  }

  // Real-time WebSocket functionality
  /**
   * Connect to WebSocket for real-time messaging
   */
  connectWebSocket(): void {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No access token available for WebSocket connection');
      return;
    }

    const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/messaging?token=${token}`;
    
    this.websocket = new WebSocket(wsUrl);

    this.websocket.onopen = () => {
      console.log('WebSocket connected for messaging');
    };

    this.websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'new_message') {
          this.messageHandlers.forEach(handler => handler(data.message));
        } else if (data.type === 'conversation_updated') {
          this.conversationHandlers.forEach(handler => handler(data.conversation));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
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
   * Subscribe to new messages
   */
  onNewMessage(handler: (message: Message) => void): () => void {
    this.messageHandlers.push(handler);
    
    // Return unsubscribe function
    return () => {
      const index = this.messageHandlers.indexOf(handler);
      if (index > -1) {
        this.messageHandlers.splice(index, 1);
      }
    };
  }

  /**
   * Subscribe to conversation updates
   */
  onConversationUpdate(handler: (conversation: Conversation) => void): () => void {
    this.conversationHandlers.push(handler);
    
    // Return unsubscribe function
    return () => {
      const index = this.conversationHandlers.indexOf(handler);
      if (index > -1) {
        this.conversationHandlers.splice(index, 1);
      }
    };
  }

  /**
   * Send typing indicator
   */
  sendTypingIndicator(conversationId: string): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({
        type: 'typing',
        conversation_id: conversationId,
      }));
    }
  }

  /**
   * Join conversation room for real-time updates
   */
  joinConversation(conversationId: string): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({
        type: 'join_conversation',
        conversation_id: conversationId,
      }));
    }
  }

  /**
   * Leave conversation room
   */
  leaveConversation(conversationId: string): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({
        type: 'leave_conversation',
        conversation_id: conversationId,
      }));
    }
  }
}

// Export singleton instance
export const messagingService = new MessagingService();
