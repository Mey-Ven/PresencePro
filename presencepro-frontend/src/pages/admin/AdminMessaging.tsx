import React, { useState, useEffect, useRef } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import { messagingService } from '../../services/messagingService';
import { useAuth } from '../../contexts/AuthContext';
import { Message, MessageThread, PaginatedResponse } from '../../services/api';
import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  UserGroupIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

// Use interfaces from API service

// WebSocket message types
interface WebSocketMessageBase {
  type: string;
}

interface NewMessageEventData extends WebSocketMessageBase {
  type: 'new_message';
  message: Message;
}

interface SendMessagePayload extends WebSocketMessageBase {
  type: 'send_message';
  message: Message; // Or a subset of fields needed for sending
}

type ReceivedWebSocketMessage = NewMessageEventData; // Add more types as needed

// Types for badge/icon functions (even if not used yet, good for consistency)
type MessagePriority = 'low' | 'normal' | 'high' | 'urgent';
const messagePriorityLabels: Record<MessagePriority, string> = {
  low: 'Faible',
  normal: 'Normal',
  high: 'Important',
  urgent: 'Urgent',
};
const messagePriorityBadges: Record<MessagePriority, string> = {
  low: 'bg-gray-100 text-gray-800',
  normal: 'bg-blue-100 text-blue-800',
  high: 'bg-yellow-100 text-yellow-800',
  urgent: 'bg-red-100 text-red-800',
};

type MessageDisplayStatus = 'sent' | 'delivered' | 'read' | 'draft';
const messageDisplayStatusIcons: Record<MessageDisplayStatus, JSX.Element> = {
  sent: <PaperAirplaneIcon className="h-4 w-4 text-blue-500" />,
  delivered: <CheckCircleIcon className="h-4 w-4 text-green-500" />,
  read: <CheckCircleIcon className="h-4 w-4 text-green-600" />, // Differentiated for clarity, could be same as delivered
  draft: <ClockIcon className="h-4 w-4 text-gray-500" />,
};


const AdminMessaging: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [threads, setThreads] = useState<MessageThread[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedThread, setSelectedThread] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCompose, setShowCompose] = useState(false);
  const [activeTab, setActiveTab] = useState<'inbox' | 'sent' | 'drafts'>('inbox');
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Load messages and establish WebSocket connection
  useEffect(() => {
    const loadMessages = async () => {
      if (!user) return;

      setIsLoading(true);

      try {
        // Load message threads from API
        const threadsResponse = await messagingService.getMessageThreads({
          page: 1,
          per_page: 50,
        });

        setThreads(threadsResponse.data);

        // Establish WebSocket connection for real-time messaging
        const wsUrl = `ws://localhost:8005/ws/${user.id}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const parsedData = JSON.parse(event.data as string);
            // Type guard for received messages
            if (parsedData && typeof parsedData.type === 'string') {
              const data = parsedData as ReceivedWebSocketMessage;

              if (data.type === 'new_message' && data.message) {
                const newMessageData = data.message as Message; // Assert if confident, or validate
                // Add new message to the list
                setMessages(prev => [...prev, newMessageData]);

                // Update thread with new message
                setThreads(prev => prev.map(thread =>
                  thread.id === newMessageData.thread_id
                    ? {
                        ...thread,
                        last_message: newMessageData.content,
                        last_message_time: newMessageData.created_at,
                        // unread_count should ideally be handled by backend or a more robust client logic
                        unread_count: (thread.unread_count || 0) + 1,
                      }
                    : thread
                ));
              }
              // Handle other message types if any
            } else {
              console.warn('Received WebSocket message with unknown structure:', parsedData);
            }
          } catch (e) {
            console.error('Error parsing WebSocket message data:', e);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
        };

        wsRef.current = ws;
      } catch (error) {
        console.error('Error loading messages:', error);

        // Fallback to mock data if API fails
        const mockThreads: MessageThread[] = [
          {
            id: '1',
            participants: ['user_1', 'user_2'],
            last_message: 'Merci pour votre réponse. Je vais fournir le certificat médical.',
            last_message_time: '2024-01-15T14:30:00Z',
            unread_count: 2,
            created_at: '2024-01-15T08:00:00Z',
            updated_at: '2024-01-15T14:30:00Z',
          },
          {
            id: '2',
            participants: ['user_3', 'user_4'],
            last_message: 'La réunion aura lieu le 20 janvier à 18h en salle 101.',
            last_message_time: '2024-01-15T10:15:00Z',
            unread_count: 0,
            created_at: '2024-01-15T09:00:00Z',
            updated_at: '2024-01-15T10:15:00Z',
          },
        ];

        const mockMessages: Message[] = [
          {
            id: 1,
            thread_id: '1',
            sender_id: 'user_1',
            content: 'Bonjour, mon fils Lucas était absent ce matin en raison d\'un rendez-vous médical. Je vous enverrai le certificat médical dès que possible.',
            message_type: 'text',
            is_read: false,
            created_at: '2024-01-15T08:30:00Z',
            updated_at: '2024-01-15T08:30:00Z',
          },
          {
            id: 2,
            thread_id: '2',
            sender_id: 'user_3',
            content: 'Chers parents, nous organisons une réunion pour discuter des progrès de vos enfants. La réunion aura lieu le 20 janvier à 18h en salle 101.',
            message_type: 'text',
            is_read: true,
            created_at: '2024-01-15T10:15:00Z',
            updated_at: '2024-01-15T10:15:00Z',
          },
        ];

        setThreads(mockThreads);
        setMessages(mockMessages);
      } finally {
        setIsLoading(false);
      }
    };

    loadMessages();

    // Cleanup WebSocket on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [user]);

  // Load messages for a specific thread
  const loadThreadMessages = async (threadId: string) => {
    try {
      const messagesResponse = await messagingService.getThreadMessages(threadId, {
        page: 1,
        per_page: 100,
      });

      setMessages(messagesResponse.data);

      // Mark messages as read
      await messagingService.markMessagesAsRead(threadId);

      // Update thread unread count
      setThreads(prev => prev.map(thread =>
        thread.id === threadId
          ? { ...thread, unread_count: 0 }
          : thread
      ));
    } catch (error) {
      console.error('Error loading thread messages:', error);
    }
  };

  // Send a new message
  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedThread || !user) return;

    try {
      const message = await messagingService.sendMessage({
        thread_id: selectedThread,
        content: newMessage.trim(),
        message_type: 'text',
      });

      // Add message to local state
      setMessages(prev => [...prev, message]);

      // Update thread with new message
      setThreads(prev => prev.map(thread =>
        thread.id === selectedThread
          ? {
              ...thread,
              last_message: message.content,
              last_message_time: message.created_at,
            }
          : thread
      ));

      // Clear input
      setNewMessage('');

      // Send via WebSocket for real-time delivery
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'send_message',
          message: message,
        }));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Erreur lors de l\'envoi du message');
    }
  };

  // Handle thread selection
  const handleThreadSelect = (threadId: string) => {
    setSelectedThread(threadId);
    loadThreadMessages(threadId);
  };

  // Filtrer les threads selon la recherche
  const filteredThreads = threads.filter(thread =>
    thread.last_message.toLowerCase().includes(searchQuery.toLowerCase()) ||
    thread.participants.some(p => p.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Obtenir le badge de priorité
  const getPriorityBadge = (priorityValue: string) => {
    const priority = priorityValue as MessagePriority;
    if (!messagePriorityLabels[priority]) {
      return (
        <span className="px-2 py-1 text-xs font-medium rounded-md bg-gray-200 text-gray-700">
          Priorité Inconnue
        </span>
      );
    }
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-md ${messagePriorityBadges[priority]}`}>
        {messagePriorityLabels[priority]}
      </span>
    );
  };

  // Obtenir l'icône de statut
  const getStatusIcon = (statusValue: string) => {
    const status = statusValue as MessageDisplayStatus;
    if (!messageDisplayStatusIcons[status]) {
      return null; // Or a default icon
    }
    return messageDisplayStatusIcons[status];
  };

  if (isLoading) {
    return (
      <Layout title="Messagerie administrative">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des messages..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Messagerie administrative">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Messagerie administrative
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Gérez la communication avec les enseignants et les parents
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <button
              onClick={() => setShowCompose(true)}
              className="btn-primary"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Nouveau message
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Liste des conversations */}
          <div className="lg:col-span-1">
            <div className="card">
              {/* Onglets */}
              <div className="border-b border-gray-200">
                <nav className="flex space-x-8 px-6 py-3">
                  {[
                    { key: 'inbox', label: 'Reçus', count: threads.filter(t => t.unread_count > 0).length },
                    { key: 'sent', label: 'Envoyés', count: 0 },
                    { key: 'drafts', label: 'Brouillons', count: 0 },
                  ].map((tab) => (
                    <button
                      key={tab.key}
                      onClick={() => setActiveTab(tab.key as any)}
                      className={`py-2 px-1 border-b-2 font-medium text-sm ${
                        activeTab === tab.key
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      {tab.label}
                      {tab.count > 0 && (
                        <span className="ml-2 bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded-full">
                          {tab.count}
                        </span>
                      )}
                    </button>
                  ))}
                </nav>
              </div>

              {/* Recherche */}
              <div className="p-4 border-b border-gray-200">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Rechercher des messages..."
                    className="input pl-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </div>

              {/* Liste des threads */}
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {filteredThreads.map((thread) => (
                  <div
                    key={thread.id}
                    onClick={() => handleThreadSelect(thread.id)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 ${
                      selectedThread === thread.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          {thread.unread_count > 0 && (
                            <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded-full">
                              {thread.unread_count}
                            </span>
                          )}
                          {!isConnected && (
                            <span className="bg-gray-100 text-gray-800 text-xs font-medium px-2 py-1 rounded-full">
                              Hors ligne
                            </span>
                          )}
                        </div>
                        <p className="text-sm font-medium text-gray-900 truncate">
                          Conversation {thread.id}
                        </p>
                        <p className="text-sm text-gray-500 truncate">
                          {thread.last_message}
                        </p>
                        <div className="flex items-center mt-2 text-xs text-gray-400">
                          <UserGroupIcon className="h-3 w-3 mr-1" />
                          {thread.participants.length} participant{thread.participants.length > 1 ? 's' : ''}
                          <span className="mx-2">•</span>
                          {new Date(thread.last_message_time).toLocaleDateString('fr-FR')}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Message si aucun thread */}
              {filteredThreads.length === 0 && (
                <div className="p-8 text-center">
                  <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune conversation</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Aucune conversation ne correspond à votre recherche.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Zone de contenu principal */}
          <div className="lg:col-span-2">
            {selectedThread ? (
              <div className="card">
                {/* En-tête de la conversation */}
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        Conversation {selectedThread}
                      </h3>
                      <div className="flex items-center mt-1 text-sm text-gray-500">
                        <UserGroupIcon className="h-4 w-4 mr-1" />
                        {threads.find(t => t.id === selectedThread)?.participants.join(', ')}
                        {isConnected && (
                          <span className="ml-2 flex items-center text-green-600">
                            <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                            En ligne
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button className="btn-secondary text-sm">
                        Répondre
                      </button>
                      <button className="btn-secondary text-sm">
                        Transférer
                      </button>
                    </div>
                  </div>
                </div>

                {/* Messages de la conversation */}
                <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
                  {messages
                    .filter(msg => msg.thread_id === selectedThread)
                    .map((message) => (
                      <div key={message.id} className="flex space-x-3">
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 bg-gray-300 rounded-full flex items-center justify-center">
                            <span className="text-xs font-medium text-gray-600">
                              {message.sender_id.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-gray-900">
                              Utilisateur {message.sender_id}
                            </span>
                            <span className="text-xs text-gray-500">
                              {new Date(message.created_at).toLocaleString('fr-FR')}
                            </span>
                            {message.is_read ? (
                              <CheckCircleIcon className="h-4 w-4 text-green-500" />
                            ) : (
                              <ClockIcon className="h-4 w-4 text-gray-500" />
                            )}
                          </div>
                          <div className="mt-1 text-sm text-gray-700">
                            {message.content}
                          </div>
                        </div>
                      </div>
                    ))}
                </div>

                {/* Zone de réponse */}
                <div className="px-6 py-4 border-t border-gray-200">
                  <div className="flex space-x-3">
                    <div className="flex-1">
                      <textarea
                        rows={3}
                        className="input resize-none"
                        placeholder="Tapez votre réponse..."
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            sendMessage();
                          }
                        }}
                      />
                    </div>
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim() || !isConnected}
                      className="btn-primary self-end disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <PaperAirplaneIcon className="h-4 w-4" />
                    </button>
                  </div>
                  {!isConnected && (
                    <p className="text-xs text-red-600 mt-2">
                      Connexion WebSocket fermée. Les messages ne peuvent pas être envoyés.
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="card p-12 text-center">
                <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Sélectionnez une conversation</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Choisissez une conversation dans la liste pour voir les messages.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AdminMessaging;
