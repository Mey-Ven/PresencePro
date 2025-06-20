import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  BellIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

// Interface pour les props du composant
interface HeaderProps {
  onMenuToggle?: () => void;
  isMobileMenuOpen?: boolean;
  title?: string;
}

// Interface pour les notifications (exemple)
interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  isRead: boolean;
  createdAt: string;
}

// Composant Header
const Header: React.FC<HeaderProps> = ({
  onMenuToggle,
  isMobileMenuOpen = false,
  title,
}) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  // États locaux
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isNotificationMenuOpen, setIsNotificationMenuOpen] = useState(false);
  const [notifications] = useState<Notification[]>([
    {
      id: '1',
      title: 'Nouvelle absence',
      message: 'Jean Dupont est absent aujourd\'hui',
      type: 'warning',
      isRead: false,
      createdAt: '2024-01-15T10:30:00Z',
    },
    {
      id: '2',
      title: 'Justification approuvée',
      message: 'La justification de Marie Martin a été approuvée',
      type: 'success',
      isRead: false,
      createdAt: '2024-01-15T09:15:00Z',
    },
  ]);

  // Refs pour les menus déroulants
  const profileMenuRef = useRef<HTMLDivElement>(null);
  const notificationMenuRef = useRef<HTMLDivElement>(null);

  // Fermer les menus quand on clique à l'extérieur
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setIsProfileMenuOpen(false);
      }
      if (notificationMenuRef.current && !notificationMenuRef.current.contains(event.target as Node)) {
        setIsNotificationMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Gérer la déconnexion
  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    }
  };

  // Obtenir le nom d'affichage de l'utilisateur
  const getDisplayName = () => {
    if (!user) return 'Utilisateur';
    return `${user.firstName} ${user.lastName}`;
  };

  // Obtenir le rôle traduit
  const getRoleLabel = () => {
    if (!user) return '';
    const roleLabels = {
      admin: 'Administrateur',
      teacher: 'Enseignant',
      student: 'Étudiant',
      parent: 'Parent',
    };
    return roleLabels[user.role as keyof typeof roleLabels] || user.role;
  };

  // Compter les notifications non lues
  const unreadNotificationsCount = notifications.filter(n => !n.isRead).length;

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Section gauche - Menu mobile et titre */}
          <div className="flex items-center space-x-4">
            {/* Bouton menu mobile */}
            <button
              type="button"
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
              onClick={onMenuToggle}
            >
              <span className="sr-only">Ouvrir le menu</span>
              {isMobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>

            {/* Titre de la page */}
            {title && (
              <h1 className="text-xl font-semibold text-gray-900 hidden sm:block">
                {title}
              </h1>
            )}
          </div>

          {/* Section droite - Notifications et profil */}
          <div className="flex items-center space-x-4">
            {/* Menu des notifications */}
            <div className="relative" ref={notificationMenuRef}>
              <button
                type="button"
                className="relative p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                onClick={() => setIsNotificationMenuOpen(!isNotificationMenuOpen)}
              >
                <span className="sr-only">Voir les notifications</span>
                <BellIcon className="h-6 w-6" />
                {unreadNotificationsCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {unreadNotificationsCount > 9 ? '9+' : unreadNotificationsCount}
                  </span>
                )}
              </button>

              {/* Menu déroulant des notifications */}
              {isNotificationMenuOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                  <div className="py-1">
                    <div className="px-4 py-2 border-b border-gray-200">
                      <h3 className="text-sm font-medium text-gray-900">Notifications</h3>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                      {notifications.length > 0 ? (
                        notifications.map((notification) => (
                          <div
                            key={notification.id}
                            className={clsx(
                              'px-4 py-3 hover:bg-gray-50 cursor-pointer border-l-4',
                              {
                                'border-blue-500': notification.type === 'info',
                                'border-yellow-500': notification.type === 'warning',
                                'border-red-500': notification.type === 'error',
                                'border-green-500': notification.type === 'success',
                                'bg-gray-50': !notification.isRead,
                              }
                            )}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900">
                                  {notification.title}
                                </p>
                                <p className="text-sm text-gray-500 mt-1">
                                  {notification.message}
                                </p>
                                <p className="text-xs text-gray-400 mt-1">
                                  {new Date(notification.createdAt).toLocaleString('fr-FR')}
                                </p>
                              </div>
                              {!notification.isRead && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full ml-2 mt-1"></div>
                              )}
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="px-4 py-6 text-center text-gray-500">
                          Aucune notification
                        </div>
                      )}
                    </div>
                    <div className="px-4 py-2 border-t border-gray-200">
                      <Link
                        to="/notifications"
                        className="text-sm text-primary-600 hover:text-primary-700"
                        onClick={() => setIsNotificationMenuOpen(false)}
                      >
                        Voir toutes les notifications
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Menu du profil utilisateur */}
            <div className="relative" ref={profileMenuRef}>
              <button
                type="button"
                className="flex items-center space-x-3 p-2 rounded-md text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
              >
                <div className="flex items-center space-x-2">
                  {user?.profilePicture ? (
                    <img
                      className="h-8 w-8 rounded-full object-cover"
                      src={user.profilePicture}
                      alt={getDisplayName()}
                    />
                  ) : (
                    <UserCircleIcon className="h-8 w-8 text-gray-400" />
                  )}
                  <div className="hidden md:block text-left">
                    <p className="text-sm font-medium text-gray-900">
                      {getDisplayName()}
                    </p>
                    <p className="text-xs text-gray-500">
                      {getRoleLabel()}
                    </p>
                  </div>
                </div>
                <ChevronDownIcon className="h-4 w-4 text-gray-400" />
              </button>

              {/* Menu déroulant du profil */}
              {isProfileMenuOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                  <div className="py-1">
                    <div className="px-4 py-2 border-b border-gray-200">
                      <p className="text-sm font-medium text-gray-900">
                        {getDisplayName()}
                      </p>
                      <p className="text-sm text-gray-500">{user?.email}</p>
                    </div>
                    
                    <Link
                      to="/profile"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setIsProfileMenuOpen(false)}
                    >
                      <UserCircleIcon className="h-4 w-4 mr-3" />
                      Mon profil
                    </Link>
                    
                    <Link
                      to="/settings"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setIsProfileMenuOpen(false)}
                    >
                      <Cog6ToothIcon className="h-4 w-4 mr-3" />
                      Paramètres
                    </Link>
                    
                    <div className="border-t border-gray-200">
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <ArrowRightOnRectangleIcon className="h-4 w-4 mr-3" />
                        Se déconnecter
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
