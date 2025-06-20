import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  BellIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  CalendarDaysIcon,
  ClockIcon,
  EyeIcon,
  TrashIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';

// Types pour les notifications
interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'absence' | 'justification' | 'general' | 'urgent' | 'event';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  isRead: boolean;
  timestamp: string;
  relatedStudent?: string;
  actionRequired?: boolean;
  actionUrl?: string;
}

interface NotificationStats {
  total: number;
  unread: number;
  urgent: number;
  actionRequired: number;
}

const ParentNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread' | 'urgent' | 'action_required'>('all');
  const [typeFilter, setTypeFilter] = useState<'all' | 'absence' | 'justification' | 'general' | 'urgent' | 'event'>('all');

  // Simuler le chargement des données
  useEffect(() => {
    const loadNotifications = async () => {
      setIsLoading(true);

      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Données simulées
      const mockNotifications: Notification[] = [
        {
          id: '1',
          title: 'Absence de Lucas',
          message: 'Votre enfant Lucas a été marqué absent au cours de Mathématiques ce matin à 8h00.',
          type: 'absence',
          priority: 'high',
          isRead: false,
          timestamp: '2024-01-15T08:05:00Z',
          relatedStudent: 'Lucas Moreau',
          actionRequired: true,
          actionUrl: '/parent/justifications',
        },
        {
          id: '2',
          title: 'Justification approuvée',
          message: 'La justification d\'absence pour Lucas du 12 janvier a été approuvée par l\'administration.',
          type: 'justification',
          priority: 'normal',
          isRead: false,
          timestamp: '2024-01-15T10:30:00Z',
          relatedStudent: 'Lucas Moreau',
          actionRequired: false,
        },
        {
          id: '3',
          title: 'Réunion parents-professeurs',
          message: 'Une réunion parents-professeurs est organisée le 20 janvier à 18h en salle polyvalente.',
          type: 'event',
          priority: 'normal',
          isRead: true,
          timestamp: '2024-01-14T16:00:00Z',
          actionRequired: false,
        },
        {
          id: '4',
          title: 'Retard de Lucas',
          message: 'Lucas est arrivé en retard au cours de Physique aujourd\'hui à 10h15.',
          type: 'absence',
          priority: 'normal',
          isRead: true,
          timestamp: '2024-01-14T10:20:00Z',
          relatedStudent: 'Lucas Moreau',
          actionRequired: false,
        },
        {
          id: '5',
          title: 'Changement d\'horaire',
          message: 'Le cours de Mathématiques du vendredi est déplacé de 14h à 15h à partir de la semaine prochaine.',
          type: 'general',
          priority: 'normal',
          isRead: true,
          timestamp: '2024-01-13T14:00:00Z',
          actionRequired: false,
        },
        {
          id: '6',
          title: 'Alerte: Absences répétées',
          message: 'Lucas a accumulé 3 absences non justifiées ce mois-ci. Une action est requise.',
          type: 'urgent',
          priority: 'urgent',
          isRead: false,
          timestamp: '2024-01-12T16:30:00Z',
          relatedStudent: 'Lucas Moreau',
          actionRequired: true,
          actionUrl: '/parent/justifications',
        },
      ];

      const mockStats: NotificationStats = {
        total: mockNotifications.length,
        unread: mockNotifications.filter(n => !n.isRead).length,
        urgent: mockNotifications.filter(n => n.priority === 'urgent').length,
        actionRequired: mockNotifications.filter(n => n.actionRequired).length,
      };

      setNotifications(mockNotifications);
      setStats(mockStats);
      setIsLoading(false);
    };

    loadNotifications();
  }, []);

  // Filtrer les notifications
  const filteredNotifications = notifications.filter(notification => {
    let matchesFilter = true;

    switch (filter) {
      case 'unread':
        matchesFilter = !notification.isRead;
        break;
      case 'urgent':
        matchesFilter = notification.priority === 'urgent';
        break;
      case 'action_required':
        matchesFilter = notification.actionRequired === true;
        break;
    }

    if (typeFilter !== 'all') {
      matchesFilter = matchesFilter && notification.type === typeFilter;
    }

    return matchesFilter;
  });

  // Marquer comme lu
  const markAsRead = (notificationId: string) => {
    setNotifications(prev => prev.map(notification =>
      notification.id === notificationId
        ? { ...notification, isRead: true }
        : notification
    ));
  };

  // Supprimer une notification
  const deleteNotification = (notificationId: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== notificationId));
  };

  // Marquer toutes comme lues
  const markAllAsRead = () => {
    setNotifications(prev => prev.map(notification => ({ ...notification, isRead: true })));
  };

  // Obtenir l'icône de type
  const getTypeIcon = (type: string, priority: string) => {
    if (priority === 'urgent') {
      return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
    }

    switch (type) {
      case 'absence':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'justification':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'event':
        return <CalendarDaysIcon className="h-5 w-5 text-blue-500" />;
      case 'urgent':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  // Obtenir le badge de priorité
  const getPriorityBadge = (priority: string) => {
    const badges = {
      low: 'bg-gray-100 text-gray-800',
      normal: 'bg-blue-100 text-blue-800',
      high: 'bg-yellow-100 text-yellow-800',
      urgent: 'bg-red-100 text-red-800',
    };

    const labels = {
      low: 'Faible',
      normal: 'Normal',
      high: 'Important',
      urgent: 'Urgent',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-md ${badges[priority as keyof typeof badges]}`}>
        {labels[priority as keyof typeof labels]}
      </span>
    );
  };

  if (isLoading) {
    return (
      <Layout title="Notifications">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des notifications..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Notifications">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Notifications
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Restez informé des événements concernant votre enfant
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <button
              onClick={markAllAsRead}
              className="btn-secondary"
            >
              Tout marquer comme lu
            </button>
          </div>
        </div>

        {/* Statistiques */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BellIcon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BellIcon className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Non lues</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.unread}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Urgentes</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.urgent}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-8 w-8 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Action requise</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.actionRequired}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filtres */}
        <div className="card p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Filtre par statut */}
            <div>
              <label className="label">Filtrer par statut</label>
              <select
                className="input"
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
              >
                <option value="all">Toutes les notifications</option>
                <option value="unread">Non lues</option>
                <option value="urgent">Urgentes</option>
                <option value="action_required">Action requise</option>
              </select>
            </div>

            {/* Filtre par type */}
            <div>
              <label className="label">Filtrer par type</label>
              <select
                className="input"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value as any)}
              >
                <option value="all">Tous les types</option>
                <option value="absence">Absences</option>
                <option value="justification">Justifications</option>
                <option value="event">Événements</option>
                <option value="urgent">Alertes</option>
                <option value="general">Général</option>
              </select>
            </div>
          </div>
        </div>

        {/* Liste des notifications */}
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Notifications ({filteredNotifications.length})
            </h3>
          </div>

          {filteredNotifications.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {filteredNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-6 ${!notification.isRead ? 'bg-blue-50' : 'bg-white'} hover:bg-gray-50 transition-colors`}
                >
                  <div className="flex items-start space-x-4">
                    {/* Icône */}
                    <div className="flex-shrink-0 mt-1">
                      {getTypeIcon(notification.type, notification.priority)}
                    </div>

                    {/* Contenu */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <h4 className={`text-sm font-medium ${!notification.isRead ? 'text-gray-900' : 'text-gray-700'}`}>
                            {notification.title}
                          </h4>
                          {!notification.isRead && (
                            <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                          )}
                          {getPriorityBadge(notification.priority)}
                          {notification.actionRequired && (
                            <span className="px-2 py-1 text-xs font-medium rounded-md bg-orange-100 text-orange-800">
                              Action requise
                            </span>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-gray-500">
                            {new Date(notification.timestamp).toLocaleDateString('fr-FR')} à{' '}
                            {new Date(notification.timestamp).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                      </div>

                      <p className="text-sm text-gray-600 mb-2">
                        {notification.message}
                      </p>

                      {notification.relatedStudent && (
                        <div className="text-xs text-gray-500 mb-3">
                          Concernant: {notification.relatedStudent}
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center space-x-3">
                        {!notification.isRead && (
                          <button
                            onClick={() => markAsRead(notification.id)}
                            className="text-blue-600 hover:text-blue-700 text-sm"
                          >
                            <EyeIcon className="h-4 w-4 inline mr-1" />
                            Marquer comme lu
                          </button>
                        )}

                        {notification.actionRequired && notification.actionUrl && (
                          <button className="text-orange-600 hover:text-orange-700 text-sm">
                            Voir l'action
                          </button>
                        )}

                        <button
                          onClick={() => deleteNotification(notification.id)}
                          className="text-red-600 hover:text-red-700 text-sm"
                        >
                          <TrashIcon className="h-4 w-4 inline mr-1" />
                          Supprimer
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune notification</h3>
              <p className="mt-1 text-sm text-gray-500">
                Aucune notification ne correspond aux critères sélectionnés.
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default ParentNotifications;
