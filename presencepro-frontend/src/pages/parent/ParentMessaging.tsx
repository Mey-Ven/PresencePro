import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  UserIcon,
  AcademicCapIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

// Types pour la messagerie
interface Message {
  id: string;
  subject: string;
  content: string;
  sender: {
    id: string;
    name: string;
    role: 'teacher' | 'admin' | 'parent';
  };
  timestamp: string;
  isRead: boolean;
}

interface Conversation {
  id: string;
  subject: string;
  participants: {
    id: string;
    name: string;
    role: 'teacher' | 'admin' | 'parent';
  }[];
  lastMessage: string;
  lastMessageTime: string;
  unreadCount: number;
  messages: Message[];
}

const ParentMessaging: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [newMessage, setNewMessage] = useState('');
  const [showCompose, setShowCompose] = useState(false);

  // Simuler le chargement des données
  useEffect(() => {
    const loadConversations = async () => {
      setIsLoading(true);

      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Données simulées
      const mockConversations: Conversation[] = [
        {
          id: '1',
          subject: 'Absence de Lucas - Justification',
          participants: [
            { id: '1', name: 'Jean Martin', role: 'teacher' },
            { id: '2', name: 'Pierre Moreau', role: 'parent' },
          ],
          lastMessage: 'Merci pour la justification. Lucas peut rattraper le cours.',
          lastMessageTime: '2024-01-15T14:30:00Z',
          unreadCount: 1,
          messages: [
            {
              id: '1',
              subject: 'Absence de Lucas - Justification',
              content: 'Bonjour, Lucas était absent ce matin en raison d\'un rendez-vous médical. Voici le certificat médical.',
              sender: { id: '2', name: 'Pierre Moreau', role: 'parent' },
              timestamp: '2024-01-15T08:30:00Z',
              isRead: true,
            },
            {
              id: '2',
              subject: 'Re: Absence de Lucas - Justification',
              content: 'Bonjour M. Moreau, merci pour la justification. Lucas peut rattraper le cours de mathématiques lors de la prochaine séance.',
              sender: { id: '1', name: 'Jean Martin', role: 'teacher' },
              timestamp: '2024-01-15T14:30:00Z',
              isRead: false,
            },
          ],
        },
        {
          id: '2',
          subject: 'Réunion parents-professeurs',
          participants: [
            { id: '3', name: 'Administration', role: 'admin' },
            { id: '2', name: 'Pierre Moreau', role: 'parent' },
          ],
          lastMessage: 'La réunion aura lieu le 20 janvier à 18h.',
          lastMessageTime: '2024-01-14T16:00:00Z',
          unreadCount: 0,
          messages: [
            {
              id: '3',
              subject: 'Réunion parents-professeurs',
              content: 'Chers parents, nous organisons une réunion parents-professeurs le 20 janvier à 18h en salle polyvalente. Votre présence est souhaitée pour discuter des progrès de votre enfant.',
              sender: { id: '3', name: 'Administration', role: 'admin' },
              timestamp: '2024-01-14T16:00:00Z',
              isRead: true,
            },
          ],
        },
        {
          id: '3',
          subject: 'Résultats du trimestre',
          participants: [
            { id: '4', name: 'Sophie Bernard', role: 'teacher' },
            { id: '2', name: 'Pierre Moreau', role: 'parent' },
          ],
          lastMessage: 'Lucas a fait de bons progrès en physique.',
          lastMessageTime: '2024-01-12T10:15:00Z',
          unreadCount: 0,
          messages: [
            {
              id: '4',
              subject: 'Résultats du trimestre',
              content: 'Bonjour, je voulais vous informer que Lucas a fait de bons progrès en physique ce trimestre. Il participe activement en classe et ses notes s\'améliorent.',
              sender: { id: '4', name: 'Sophie Bernard', role: 'teacher' },
              timestamp: '2024-01-12T10:15:00Z',
              isRead: true,
            },
          ],
        },
      ];

      setConversations(mockConversations);
      if (mockConversations.length > 0) {
        setSelectedConversation(mockConversations[0].id);
      }
      setIsLoading(false);
    };

    loadConversations();
  }, []);

  // Filtrer les conversations
  const filteredConversations = conversations.filter(conv =>
    conv.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.participants.some(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Obtenir la conversation sélectionnée
  const currentConversation = conversations.find(c => c.id === selectedConversation);

  // Envoyer un message
  const sendMessage = () => {
    if (!newMessage.trim() || !currentConversation) return;

    const message: Message = {
      id: Date.now().toString(),
      subject: `Re: ${currentConversation.subject}`,
      content: newMessage,
      sender: { id: '2', name: 'Pierre Moreau', role: 'parent' },
      timestamp: new Date().toISOString(),
      isRead: true,
    };

    setConversations(prev => prev.map(conv =>
      conv.id === selectedConversation
        ? {
            ...conv,
            messages: [...conv.messages, message],
            lastMessage: newMessage,
            lastMessageTime: new Date().toISOString(),
          }
        : conv
    ));

    setNewMessage('');
  };

  // Obtenir l'icône de rôle
  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'teacher':
        return <AcademicCapIcon className="h-4 w-4 text-blue-600" />;
      case 'admin':
        return <UserIcon className="h-4 w-4 text-purple-600" />;
      default:
        return <UserIcon className="h-4 w-4 text-gray-600" />;
    }
  };

  if (isLoading) {
    return (
      <Layout title="Messagerie">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des messages..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Messagerie">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Messagerie
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Communiquez avec les enseignants et l'administration
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
              {/* Recherche */}
              <div className="p-4 border-b border-gray-200">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Rechercher des conversations..."
                    className="input pl-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </div>

              {/* Liste des conversations */}
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {filteredConversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    onClick={() => setSelectedConversation(conversation.id)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 ${
                      selectedConversation === conversation.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          {conversation.unreadCount > 0 && (
                            <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded-full">
                              {conversation.unreadCount}
                            </span>
                          )}
                        </div>
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {conversation.subject}
                        </p>
                        <p className="text-sm text-gray-500 truncate">
                          {conversation.lastMessage}
                        </p>
                        <div className="flex items-center mt-2 text-xs text-gray-400">
                          {getRoleIcon(conversation.participants[0].role)}
                          <span className="ml-1">{conversation.participants[0].name}</span>
                          <span className="mx-2">•</span>
                          <ClockIcon className="h-3 w-3 mr-1" />
                          {new Date(conversation.lastMessageTime).toLocaleDateString('fr-FR')}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Message si aucune conversation */}
              {filteredConversations.length === 0 && (
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

          {/* Zone de conversation */}
          <div className="lg:col-span-2">
            {currentConversation ? (
              <div className="card">
                {/* En-tête de la conversation */}
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">
                    {currentConversation.subject}
                  </h3>
                  <div className="flex items-center mt-1 text-sm text-gray-500">
                    <span>Participants: </span>
                    {currentConversation.participants.map((participant, index) => (
                      <span key={participant.id} className="ml-1">
                        {participant.name}
                        {index < currentConversation.participants.length - 1 && ', '}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Messages */}
                <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
                  {currentConversation.messages.map((message) => (
                    <div key={message.id} className="flex space-x-3">
                      <div className="flex-shrink-0">
                        <div className="h-8 w-8 bg-gray-300 rounded-full flex items-center justify-center">
                          {getRoleIcon(message.sender.role)}
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900">
                            {message.sender.name}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(message.timestamp).toLocaleString('fr-FR')}
                          </span>
                          {!message.isRead && (
                            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                              Nouveau
                            </span>
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
                        placeholder="Tapez votre message..."
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                      />
                    </div>
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim()}
                      className="btn-primary self-end"
                    >
                      <PaperAirplaneIcon className="h-4 w-4" />
                    </button>
                  </div>
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

export default ParentMessaging;
