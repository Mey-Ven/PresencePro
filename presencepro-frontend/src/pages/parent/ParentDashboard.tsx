import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  UserIcon,
  ClipboardDocumentListIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  CalendarDaysIcon,
  BellIcon,
  ChatBubbleLeftRightIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

// Interface pour les statistiques du dashboard parent
interface ParentDashboardStats {
  children: ChildInfo[];
  totalNotifications: number;
  pendingJustifications: number;
  recentActivity: ParentActivityItem[];
  upcomingEvents: UpcomingEvent[];
}

interface ChildInfo {
  id: string;
  firstName: string;
  lastName: string;
  className: string;
  attendanceRate: number;
  totalAbsences: number;
  pendingAbsences: number;
  lastAbsence?: string;
  profilePicture?: string;
}

interface ParentActivityItem {
  id: string;
  type: 'absence_reported' | 'justification_approved' | 'message_received' | 'attendance_alert';
  message: string;
  timestamp: string;
  childName: string;
  urgent?: boolean;
}

interface UpcomingEvent {
  id: string;
  title: string;
  date: string;
  time: string;
  type: 'meeting' | 'event' | 'exam' | 'holiday';
  childName?: string;
}

// Composant Dashboard Parent
const ParentDashboard: React.FC = () => {
  const [stats, setStats] = useState<ParentDashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedChild, setSelectedChild] = useState<string>('all');

  // Simuler le chargement des données
  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true);
      
      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Données simulées pour le parent
      const mockStats: ParentDashboardStats = {
        children: [
          {
            id: '1',
            firstName: 'Emma',
            lastName: 'Moreau',
            className: '3ème A',
            attendanceRate: 94.2,
            totalAbsences: 4,
            pendingAbsences: 1,
            lastAbsence: '2024-01-14',
          },
          {
            id: '2',
            firstName: 'Lucas',
            lastName: 'Moreau',
            className: '5ème B',
            attendanceRate: 89.7,
            totalAbsences: 8,
            pendingAbsences: 2,
            lastAbsence: '2024-01-15',
          },
        ],
        totalNotifications: 5,
        pendingJustifications: 3,
        recentActivity: [
          {
            id: '1',
            type: 'absence_reported',
            message: 'Emma a été marquée absente en Mathématiques',
            timestamp: '2024-01-15T10:30:00Z',
            childName: 'Emma',
            urgent: true,
          },
          {
            id: '2',
            type: 'justification_approved',
            message: 'Justification approuvée pour Lucas (rendez-vous médical)',
            timestamp: '2024-01-15T09:15:00Z',
            childName: 'Lucas',
          },
          {
            id: '3',
            type: 'message_received',
            message: 'Nouveau message de Mme Dupont (professeur de Mathématiques)',
            timestamp: '2024-01-14T16:45:00Z',
            childName: 'Emma',
          },
          {
            id: '4',
            type: 'attendance_alert',
            message: 'Taux de présence de Lucas en baisse (89.7%)',
            timestamp: '2024-01-14T14:20:00Z',
            childName: 'Lucas',
            urgent: true,
          },
        ],
        upcomingEvents: [
          {
            id: '1',
            title: 'Réunion parents-professeurs',
            date: '2024-01-20',
            time: '14:00',
            type: 'meeting',
            childName: 'Emma',
          },
          {
            id: '2',
            title: 'Contrôle de Mathématiques',
            date: '2024-01-18',
            time: '08:00',
            type: 'exam',
            childName: 'Emma',
          },
          {
            id: '3',
            title: 'Sortie scolaire - Musée',
            date: '2024-01-22',
            time: '09:00',
            type: 'event',
            childName: 'Lucas',
          },
          {
            id: '4',
            title: 'Vacances d\'hiver',
            date: '2024-02-10',
            time: '17:00',
            type: 'holiday',
          },
        ],
      };
      
      setStats(mockStats);
      setIsLoading(false);
    };

    loadDashboardData();
  }, []);

  if (isLoading) {
    return (
      <Layout title="Tableau de bord - Parent">
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="card p-6">
                <CardSpinner />
              </div>
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  if (!stats) {
    return (
      <Layout title="Tableau de bord - Parent">
        <div className="text-center py-12">
          <p className="text-gray-500">Erreur lors du chargement des données</p>
        </div>
      </Layout>
    );
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'absence_reported':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'justification_approved':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'message_received':
        return <ChatBubbleLeftRightIcon className="h-5 w-5 text-blue-500" />;
      case 'attendance_alert':
        return <BellIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <BellIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'meeting':
        return '👥';
      case 'exam':
        return '📝';
      case 'event':
        return '🎯';
      case 'holiday':
        return '🏖️';
      default:
        return '📅';
    }
  };

  const filteredChildren = selectedChild === 'all' 
    ? stats.children 
    : stats.children.filter(child => child.id === selectedChild);

  return (
    <Layout title="Tableau de bord - Parent">
      <div className="space-y-6">
        {/* Message de bienvenue */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-medium text-blue-900 mb-2">
            Bonjour ! Voici le suivi de vos enfants
          </h2>
          <p className="text-blue-700">
            Vous avez {stats.totalNotifications} nouvelle(s) notification(s) et {stats.pendingJustifications} justification(s) en attente.
          </p>
        </div>

        {/* Sélecteur d'enfant */}
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Afficher :</label>
          <select
            value={selectedChild}
            onChange={(e) => setSelectedChild(e.target.value)}
            className="input w-auto"
          >
            <option value="all">Tous mes enfants</option>
            {stats.children.map((child) => (
              <option key={child.id} value={child.id}>
                {child.firstName} {child.lastName}
              </option>
            ))}
          </select>
        </div>

        {/* Cartes des enfants */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredChildren.map((child) => (
            <div key={child.id} className="card p-6">
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <UserIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {child.firstName} {child.lastName}
                  </h3>
                  <p className="text-sm text-gray-500">{child.className}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{child.attendanceRate}%</p>
                  <p className="text-xs text-gray-500">Taux de présence</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">{child.totalAbsences}</p>
                  <p className="text-xs text-gray-500">Total absences</p>
                </div>
              </div>

              {child.pendingAbsences > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
                  <p className="text-sm text-yellow-800">
                    <ExclamationTriangleIcon className="h-4 w-4 inline mr-1" />
                    {child.pendingAbsences} absence(s) à justifier
                  </p>
                </div>
              )}

              <div className="flex space-x-2">
                <Link
                  to={`/parent/child/${child.id}/attendance`}
                  className="btn-primary text-sm flex-1 text-center"
                >
                  Voir détails
                </Link>
                <Link
                  to={`/parent/child/${child.id}/justify`}
                  className="btn-secondary text-sm flex-1 text-center"
                >
                  Justifier
                </Link>
              </div>
            </div>
          ))}
        </div>

        {/* Statistiques globales */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Mes enfants</p>
                <p className="text-2xl font-bold text-gray-900">{stats.children.length}</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BellIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Notifications</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalNotifications}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/parent/notifications"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Voir toutes →
              </Link>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">À justifier</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pendingJustifications}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/parent/justifications"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Gérer →
              </Link>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChatBubbleLeftRightIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Messages</p>
                <p className="text-2xl font-bold text-gray-900">3</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/parent/messages"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Lire →
              </Link>
            </div>
          </div>
        </div>

        {/* Activité récente et événements à venir */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Activité récente */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Activité récente
            </h3>
            <div className="space-y-4">
              {stats.recentActivity.map((activity) => (
                <div key={activity.id} className={`flex items-start space-x-3 p-3 rounded-lg ${
                  activity.urgent ? 'bg-red-50 border border-red-200' : 'bg-gray-50'
                }`}>
                  <div className="flex-shrink-0">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{activity.message}</p>
                    <div className="flex items-center justify-between mt-1">
                      <p className="text-xs text-gray-500">
                        {activity.childName} • {new Date(activity.timestamp).toLocaleString('fr-FR')}
                      </p>
                      {activity.urgent && (
                        <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                          Urgent
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Link
                to="/parent/activity"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Voir toute l'activité →
              </Link>
            </div>
          </div>

          {/* Événements à venir */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <CalendarDaysIcon className="h-5 w-5 mr-2" />
              Événements à venir
            </h3>
            <div className="space-y-4">
              {stats.upcomingEvents.map((event) => (
                <div key={event.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl">{getEventIcon(event.type)}</div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{event.title}</h4>
                    <p className="text-sm text-gray-600">
                      {new Date(event.date).toLocaleDateString('fr-FR')} à {event.time}
                    </p>
                    {event.childName && (
                      <p className="text-xs text-gray-500">{event.childName}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Link
                to="/parent/calendar"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Voir le calendrier complet →
              </Link>
            </div>
          </div>
        </div>

        {/* Actions rapides */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Actions rapides
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Link
              to="/parent/justifications"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center"
            >
              <DocumentTextIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Justifier absences</h4>
              <p className="text-sm text-gray-500">Gérer les justifications</p>
            </Link>
            
            <Link
              to="/parent/messages"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center"
            >
              <ChatBubbleLeftRightIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Messagerie</h4>
              <p className="text-sm text-gray-500">Contacter l'école</p>
            </Link>
            
            <Link
              to="/parent/attendance"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center"
            >
              <ClipboardDocumentListIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Suivi présence</h4>
              <p className="text-sm text-gray-500">Voir les absences</p>
            </Link>
            
            <Link
              to="/parent/calendar"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center"
            >
              <CalendarDaysIcon className="h-8 w-8 text-orange-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Calendrier</h4>
              <p className="text-sm text-gray-500">Événements à venir</p>
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ParentDashboard;
