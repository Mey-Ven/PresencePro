import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  HomeIcon,
  UsersIcon,
  AcademicCapIcon,
  ClipboardDocumentListIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  CalendarDaysIcon,
  UserGroupIcon,
  ExclamationTriangleIcon,
  BellIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

// Interface pour un élément de navigation
interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  roles: string[];
  badge?: number;
  children?: NavigationItem[];
}

// Interface pour les props du composant
interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

// Configuration de la navigation selon les rôles
const getNavigationItems = (userRole: string): NavigationItem[] => {
  const baseItems: NavigationItem[] = [];

  // Navigation pour les administrateurs
  if (userRole === 'admin') {
    baseItems.push(
      {
        name: 'Tableau de bord',
        href: '/admin/dashboard',
        icon: HomeIcon,
        roles: ['admin'],
      },
      {
        name: 'Gestion des utilisateurs',
        href: '/admin/users',
        icon: UsersIcon,
        roles: ['admin'],
        children: [
          {
            name: 'Tous les utilisateurs',
            href: '/admin/users',
            icon: UsersIcon,
            roles: ['admin'],
          },
          {
            name: 'Étudiants',
            href: '/admin/users/students',
            icon: AcademicCapIcon,
            roles: ['admin'],
          },
          {
            name: 'Enseignants',
            href: '/admin/users/teachers',
            icon: UserGroupIcon,
            roles: ['admin'],
          },
          {
            name: 'Parents',
            href: '/admin/users/parents',
            icon: UsersIcon,
            roles: ['admin'],
          },
        ],
      },
      {
        name: 'Cours et Classes',
        href: '/admin/courses',
        icon: AcademicCapIcon,
        roles: ['admin'],
      },
      {
        name: 'Présences',
        href: '/admin/attendance',
        icon: ClipboardDocumentListIcon,
        roles: ['admin'],
      },
      {
        name: 'Justifications',
        href: '/admin/justifications',
        icon: DocumentTextIcon,
        roles: ['admin'],
        badge: 5, // Exemple de badge pour les justifications en attente
      },
      {
        name: 'Messagerie',
        href: '/admin/messaging',
        icon: ChatBubbleLeftRightIcon,
        roles: ['admin'],
      },
      {
        name: 'Statistiques',
        href: '/admin/statistics',
        icon: ChartBarIcon,
        roles: ['admin'],
      },
      {
        name: 'Paramètres',
        href: '/admin/settings',
        icon: Cog6ToothIcon,
        roles: ['admin'],
      }
    );
  }

  // Navigation pour les enseignants
  if (userRole === 'teacher') {
    baseItems.push(
      {
        name: 'Tableau de bord',
        href: '/teacher/dashboard',
        icon: HomeIcon,
        roles: ['teacher'],
      },
      {
        name: 'Mes cours',
        href: '/teacher/courses',
        icon: AcademicCapIcon,
        roles: ['teacher'],
      },
      {
        name: 'Prise de présence',
        href: '/teacher/attendance',
        icon: ClipboardDocumentListIcon,
        roles: ['teacher'],
      },
      {
        name: 'Absents du jour',
        href: '/teacher/absences',
        icon: ExclamationTriangleIcon,
        roles: ['teacher'],
        badge: 3, // Exemple de badge pour les absents
      },
      {
        name: 'Justifications',
        href: '/teacher/justifications',
        icon: DocumentTextIcon,
        roles: ['teacher'],
      },
      {
        name: 'Mes classes',
        href: '/teacher/classes',
        icon: UserGroupIcon,
        roles: ['teacher'],
      },
      {
        name: 'Statistiques',
        href: '/teacher/statistics',
        icon: ChartBarIcon,
        roles: ['teacher'],
      }
    );
  }

  // Navigation pour les étudiants
  if (userRole === 'student') {
    baseItems.push(
      {
        name: 'Tableau de bord',
        href: '/student/dashboard',
        icon: HomeIcon,
        roles: ['student'],
      },
      {
        name: 'Mes cours',
        href: '/student/courses',
        icon: AcademicCapIcon,
        roles: ['student'],
      },
      {
        name: 'Mes absences',
        href: '/student/attendance',
        icon: ClipboardDocumentListIcon,
        roles: ['student'],
      },
      {
        name: 'Justifier une absence',
        href: '/student/justify',
        icon: DocumentTextIcon,
        roles: ['student'],
      },
      {
        name: 'Mon planning',
        href: '/student/schedule',
        icon: CalendarDaysIcon,
        roles: ['student'],
      },
      {
        name: 'Mes statistiques',
        href: '/student/statistics',
        icon: ChartBarIcon,
        roles: ['student'],
      }
    );
  }

  // Navigation pour les parents
  if (userRole === 'parent') {
    baseItems.push(
      {
        name: 'Tableau de bord',
        href: '/parent/dashboard',
        icon: HomeIcon,
        roles: ['parent'],
      },
      {
        name: 'Absences de mon enfant',
        href: '/parent/attendance',
        icon: ClipboardDocumentListIcon,
        roles: ['parent'],
      },
      {
        name: 'Justifications',
        href: '/parent/justifications',
        icon: DocumentTextIcon,
        roles: ['parent'],
        badge: 2, // Exemple de badge pour les justifications à valider
      },
      {
        name: 'Messagerie',
        href: '/parent/messaging',
        icon: ChatBubbleLeftRightIcon,
        roles: ['parent'],
      },
      {
        name: 'Notifications',
        href: '/parent/notifications',
        icon: BellIcon,
        roles: ['parent'],
      },
      {
        name: 'Planning de mon enfant',
        href: '/parent/schedule',
        icon: CalendarDaysIcon,
        roles: ['parent'],
      }
    );
  }

  return baseItems;
};

// Composant Sidebar
const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const navigationItems = getNavigationItems(user.role);

  // Vérifier si un lien est actif
  const isActiveLink = (href: string): boolean => {
    return location.pathname === href || location.pathname.startsWith(href + '/');
  };

  // Composant pour un élément de navigation
  const NavigationItem: React.FC<{ item: NavigationItem; level?: number }> = ({ 
    item, 
    level = 0 
  }) => {
    const isActive = isActiveLink(item.href);
    const hasChildren = item.children && item.children.length > 0;

    return (
      <div>
        <Link
          to={item.href}
          onClick={onClose}
          className={clsx(
            'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-200',
            {
              'bg-primary-100 text-primary-900 border-r-2 border-primary-500': isActive,
              'text-gray-600 hover:bg-gray-50 hover:text-gray-900': !isActive,
              'pl-4': level > 0,
              'pl-6': level > 1,
            }
          )}
        >
          <item.icon
            className={clsx(
              'mr-3 flex-shrink-0 h-5 w-5',
              {
                'text-primary-500': isActive,
                'text-gray-400 group-hover:text-gray-500': !isActive,
              }
            )}
          />
          <span className="flex-1">{item.name}</span>
          {item.badge && item.badge > 0 && (
            <span className="ml-3 inline-block py-0.5 px-2 text-xs font-medium bg-red-100 text-red-800 rounded-full">
              {item.badge > 99 ? '99+' : item.badge}
            </span>
          )}
        </Link>

        {/* Sous-éléments */}
        {hasChildren && (
          <div className="mt-1 space-y-1">
            {item.children!.map((child) => (
              <NavigationItem key={child.href} item={child} level={level + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Overlay pour mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={onClose}
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
        </div>
      )}

      {/* Sidebar */}
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          {
            'translate-x-0': isOpen,
            '-translate-x-full': !isOpen,
          }
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo et titre */}
          <div className="flex items-center justify-center h-16 px-4 bg-primary-600">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <span className="text-primary-600 font-bold text-lg">P</span>
              </div>
              <span className="text-white font-bold text-xl">PresencePro</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {navigationItems.map((item) => (
              <NavigationItem key={item.href} item={item} />
            ))}
          </nav>

          {/* Informations utilisateur */}
          <div className="flex-shrink-0 px-4 py-4 border-t border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {user.profilePicture ? (
                  <img
                    className="h-8 w-8 rounded-full object-cover"
                    src={user.profilePicture}
                    alt={`${user.firstName} ${user.lastName}`}
                  />
                ) : (
                  <div className="h-8 w-8 bg-gray-300 rounded-full flex items-center justify-center">
                    <span className="text-gray-600 text-sm font-medium">
                      {user.firstName.charAt(0)}{user.lastName.charAt(0)}
                    </span>
                  </div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.firstName} {user.lastName}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user.role === 'admin' && 'Administrateur'}
                  {user.role === 'teacher' && 'Enseignant'}
                  {user.role === 'student' && 'Étudiant'}
                  {user.role === 'parent' && 'Parent'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
