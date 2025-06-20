import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import PowerBIChart from '../../components/charts/PowerBIChart';
import { statisticsService } from '../../services/statisticsService';
import { DashboardStats, ActivityItem } from '../../services/api';
import {
  UsersIcon,
  AcademicCapIcon,
  ClipboardDocumentListIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';
// Temporairement désactivé Chart.js pour les tests
// import {
//   Chart as ChartJS,
//   CategoryScale,
//   LinearScale,
//   PointElement,
//   LineElement,
//   BarElement,
//   Title,
//   Tooltip,
//   Legend,
//   ArcElement,
// } from 'chart.js';
// import { Line, Bar, Doughnut } from 'react-chartjs-2';

// Use interfaces from API service

// Composant Dashboard Admin
const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load dashboard data from API
  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true);

      try {
        // Load dashboard statistics from API
        const dashboardStats = await statisticsService.getAdminDashboardStats();
        setStats(dashboardStats);
      } catch (error) {
        console.error('Error loading dashboard data:', error);

        // Fallback to mock data if API fails
        const mockStats: DashboardStats = {
          total_students: 892,
          total_teachers: 45,
          total_parents: 310,
          total_courses: 156,
          total_classes: 28,
          today_attendance_rate: 87.5,
          weekly_attendance_rate: 89.2,
          monthly_attendance_rate: 91.8,
          pending_justifications: 12,
          unread_messages: 5,
          recent_activity: [
            {
              id: '1',
              type: 'attendance',
              message: 'Jean Dupont marqué absent en Mathématiques',
              timestamp: '2024-01-15T10:30:00Z',
              user_name: 'Prof. Martin',
            },
            {
              id: '2',
              type: 'justification',
              message: 'Nouvelle justification soumise par Marie Dubois',
              timestamp: '2024-01-15T09:45:00Z',
              user_name: 'Marie Dubois',
            },
            {
              id: '3',
              type: 'user_created',
              message: 'Nouvel étudiant inscrit: Pierre Moreau',
              timestamp: '2024-01-15T08:20:00Z',
              user_name: 'Admin',
            },
            {
              id: '4',
              type: 'course_created',
              message: 'Nouveau cours créé: Physique Quantique',
              timestamp: '2024-01-14T16:30:00Z',
              user_name: 'Prof. Durand',
            },
          ],
        };

        setStats(mockStats);
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  // Chart data - will be loaded from API or use fallback
  const weeklyAttendanceData = {
    labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
    data: [92, 88, 91, 85, 89, 78, 82],
  };

  const absencesByClassData = {
    labels: ['6ème A', '6ème B', '5ème A', '5ème B', '4ème A', '4ème B', '3ème A', '3ème B'],
    data: [5, 8, 3, 12, 7, 4, 9, 6],
  };

  const userTypesData = stats ? {
    labels: ['Étudiants', 'Enseignants', 'Parents'],
    data: [stats.total_students, stats.total_teachers, stats.total_parents],
  } : {
    labels: ['Étudiants', 'Enseignants', 'Parents'],
    data: [892, 45, 310],
  };

  if (isLoading) {
    return (
      <Layout title="Tableau de bord">
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="card p-6">
                <CardSpinner />
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(2)].map((_, i) => (
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
      <Layout title="Tableau de bord">
        <div className="text-center py-12">
          <p className="text-gray-500">Erreur lors du chargement des données</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Tableau de bord">
      <div className="space-y-6">
        {/* Message de bienvenue */}
        <div className="card p-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-1">
                Bienvenue dans PresencePro Admin
              </h2>
              <p className="text-gray-600">
                Tableau de bord administrateur - Gérez efficacement votre établissement scolaire
              </p>
            </div>
          </div>
        </div>

        {/* Cartes de statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total utilisateurs */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UsersIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total utilisateurs</p>
                <p className="text-2xl font-bold text-gray-900">{(stats.total_students + stats.total_teachers + stats.total_parents).toLocaleString()}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/admin/users"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Gérer les utilisateurs →
              </Link>
            </div>
          </div>

          {/* Taux de présence */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClipboardDocumentListIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Présence aujourd'hui</p>
                <p className="text-2xl font-bold text-gray-900">{stats.today_attendance_rate}%</p>
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+2.1% vs hier</span>
            </div>
          </div>

          {/* Absences du jour */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Absences aujourd'hui</p>
                <p className="text-2xl font-bold text-gray-900">{Math.round(stats.total_students * (100 - stats.today_attendance_rate) / 100)}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/admin/attendance"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Voir les détails →
              </Link>
            </div>
          </div>

          {/* Justifications en attente */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Justifications en attente</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pending_justifications}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/admin/justifications"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Traiter les demandes →
              </Link>
            </div>
          </div>
        </div>

        {/* Graphiques Power BI */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Graphique de présence hebdomadaire */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Taux de présence cette semaine
            </h3>
            <PowerBIChart
              title="Taux de présence hebdomadaire"
              chartType="line"
              mockData={weeklyAttendanceData}
              height="300px"
            />
          </div>

          {/* Graphique des absences par classe */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Absences par classe aujourd'hui
            </h3>
            <PowerBIChart
              title="Absences par classe"
              chartType="bar"
              mockData={absencesByClassData}
              height="300px"
            />
          </div>
        </div>

        {/* Section inférieure */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Répartition des utilisateurs */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Répartition des utilisateurs
            </h3>
            <PowerBIChart
              title="Répartition des utilisateurs"
              chartType="doughnut"
              mockData={userTypesData}
              height="300px"
            />
          </div>

          {/* Activité récente */}
          <div className="lg:col-span-2 card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Activité récente
              </h3>
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            </div>
            <div className="space-y-3">
              {stats.recent_activity.map((activity, index) => (
                <div key={activity.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                  <div className="flex-shrink-0">
                    {activity.type === 'attendance' && (
                      <div className="w-8 h-8 bg-yellow-500 rounded-lg flex items-center justify-center">
                        <ExclamationTriangleIcon className="h-4 w-4 text-white" />
                      </div>
                    )}
                    {activity.type === 'justification' && (
                      <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                        <DocumentTextIcon className="h-4 w-4 text-white" />
                      </div>
                    )}
                    {activity.type === 'user_created' && (
                      <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                        <UsersIcon className="h-4 w-4 text-white" />
                      </div>
                    )}
                    {activity.type === 'course_created' && (
                      <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                        <AcademicCapIcon className="h-4 w-4 text-white" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(activity.timestamp).toLocaleString('fr-FR')} • {activity.user_name}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Link
                to="/admin/activity"
                className="btn-primary"
              >
                Voir toute l'activité →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AdminDashboard;
