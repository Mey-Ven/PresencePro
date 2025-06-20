import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  AcademicCapIcon,
  ClipboardDocumentListIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

// Interface pour les statistiques du dashboard étudiant
interface StudentDashboardStats {
  totalCourses: number;
  attendanceRate: number;
  totalAbsences: number;
  pendingJustifications: number;
  recentAttendance: AttendanceRecord[];
  upcomingClasses: UpcomingClass[];
  monthlyStats: MonthlyStats;
}

interface AttendanceRecord {
  id: string;
  courseName: string;
  date: string;
  status: 'present' | 'absent' | 'late' | 'justified';
  teacher: string;
  notes?: string;
}

interface UpcomingClass {
  id: string;
  courseName: string;
  teacher: string;
  startTime: string;
  endTime: string;
  room: string;
  date: string;
}

interface MonthlyStats {
  totalClasses: number;
  presentClasses: number;
  absentClasses: number;
  lateClasses: number;
  justifiedAbsences: number;
}

// Composant Dashboard Étudiant
const StudentDashboard: React.FC = () => {
  const [stats, setStats] = useState<StudentDashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Simuler le chargement des données
  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true);
      
      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Données simulées pour l'étudiant
      const mockStats: StudentDashboardStats = {
        totalCourses: 8,
        attendanceRate: 87.5,
        totalAbsences: 12,
        pendingJustifications: 2,
        recentAttendance: [
          {
            id: '1',
            courseName: 'Mathématiques',
            date: '2024-01-15',
            status: 'present',
            teacher: 'Mme Dupont',
          },
          {
            id: '2',
            courseName: 'Physique',
            date: '2024-01-15',
            status: 'absent',
            teacher: 'M. Martin',
            notes: 'Absence non justifiée',
          },
          {
            id: '3',
            courseName: 'Français',
            date: '2024-01-14',
            status: 'late',
            teacher: 'Mme Moreau',
            notes: 'Retard de 10 minutes',
          },
          {
            id: '4',
            courseName: 'Histoire',
            date: '2024-01-14',
            status: 'justified',
            teacher: 'M. Bernard',
            notes: 'Rendez-vous médical justifié',
          },
          {
            id: '5',
            courseName: 'Anglais',
            date: '2024-01-13',
            status: 'present',
            teacher: 'Ms Johnson',
          },
        ],
        upcomingClasses: [
          {
            id: '1',
            courseName: 'Mathématiques',
            teacher: 'Mme Dupont',
            startTime: '14:00',
            endTime: '15:00',
            room: 'Salle 101',
            date: '2024-01-15',
          },
          {
            id: '2',
            courseName: 'Chimie',
            teacher: 'M. Rousseau',
            startTime: '15:00',
            endTime: '16:00',
            room: 'Labo 1',
            date: '2024-01-15',
          },
          {
            id: '3',
            courseName: 'Sport',
            teacher: 'M. Leroy',
            startTime: '16:00',
            endTime: '17:00',
            room: 'Gymnase',
            date: '2024-01-15',
          },
        ],
        monthlyStats: {
          totalClasses: 96,
          presentClasses: 84,
          absentClasses: 8,
          lateClasses: 4,
          justifiedAbsences: 3,
        },
      };
      
      setStats(mockStats);
      setIsLoading(false);
    };

    loadDashboardData();
  }, []);

  if (isLoading) {
    return (
      <Layout title="Mon tableau de bord">
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
      <Layout title="Mon tableau de bord">
        <div className="text-center py-12">
          <p className="text-gray-500">Erreur lors du chargement des données</p>
        </div>
      </Layout>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present':
        return 'text-green-600 bg-green-100';
      case 'absent':
        return 'text-red-600 bg-red-100';
      case 'late':
        return 'text-yellow-600 bg-yellow-100';
      case 'justified':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'present':
        return 'Présent';
      case 'absent':
        return 'Absent';
      case 'late':
        return 'Retard';
      case 'justified':
        return 'Justifié';
      default:
        return status;
    }
  };

  return (
    <Layout title="Mon tableau de bord">
      <div className="space-y-6">
        {/* Message de bienvenue */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-medium text-blue-900 mb-2">
            Bonjour ! Voici votre résumé de présence
          </h2>
          <p className="text-blue-700">
            Votre taux de présence ce mois-ci est de {stats.attendanceRate}%. 
            {stats.pendingJustifications > 0 && (
              <span className="font-medium"> Vous avez {stats.pendingJustifications} absence(s) à justifier.</span>
            )}
          </p>
        </div>

        {/* Cartes de statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Mes cours */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AcademicCapIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Mes cours</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalCourses}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/student/courses"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Voir mon planning →
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
                <p className="text-sm font-medium text-gray-500">Taux de présence</p>
                <p className="text-2xl font-bold text-gray-900">{stats.attendanceRate}%</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/student/attendance"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Voir l'historique →
              </Link>
            </div>
          </div>

          {/* Total absences */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total absences</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalAbsences}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/student/absences"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Gérer les absences →
              </Link>
            </div>
          </div>

          {/* Justifications en attente */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">À justifier</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pendingJustifications}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/student/justify"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Justifier absence →
              </Link>
            </div>
          </div>
        </div>

        {/* Statistiques mensuelles */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Statistiques du mois
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{stats.monthlyStats.totalClasses}</p>
              <p className="text-sm text-gray-500">Total cours</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{stats.monthlyStats.presentClasses}</p>
              <p className="text-sm text-gray-500">Présences</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{stats.monthlyStats.absentClasses}</p>
              <p className="text-sm text-gray-500">Absences</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{stats.monthlyStats.lateClasses}</p>
              <p className="text-sm text-gray-500">Retards</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{stats.monthlyStats.justifiedAbsences}</p>
              <p className="text-sm text-gray-500">Justifiées</p>
            </div>
          </div>
        </div>

        {/* Prochains cours et historique récent */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Prochains cours */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <CalendarDaysIcon className="h-5 w-5 mr-2" />
              Prochains cours
            </h3>
            <div className="space-y-4">
              {stats.upcomingClasses.map((classItem) => (
                <div key={classItem.id} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">{classItem.courseName}</h4>
                      <p className="text-sm text-gray-600">{classItem.teacher}</p>
                      <p className="text-sm text-gray-500">
                        <ClockIcon className="h-4 w-4 inline mr-1" />
                        {classItem.startTime} - {classItem.endTime} • {classItem.room}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Historique récent */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Historique récent
            </h3>
            <div className="space-y-4">
              {stats.recentAttendance.map((record) => (
                <div key={record.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900">{record.courseName}</h4>
                      <span className={`text-xs px-2 py-1 rounded ${getStatusColor(record.status)}`}>
                        {getStatusLabel(record.status)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{record.teacher}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(record.date).toLocaleDateString('fr-FR')}
                    </p>
                    {record.notes && (
                      <p className="text-xs text-gray-500 mt-1">{record.notes}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Link
                to="/student/attendance"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Voir tout l'historique →
              </Link>
            </div>
          </div>
        </div>

        {/* Actions rapides */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Actions rapides
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/student/justify"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center"
            >
              <DocumentTextIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Justifier une absence</h4>
              <p className="text-sm text-gray-500">Soumettre une justification</p>
            </Link>
            
            <Link
              to="/student/schedule"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center"
            >
              <CalendarDaysIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Mon planning</h4>
              <p className="text-sm text-gray-500">Consulter mes cours</p>
            </Link>
            
            <Link
              to="/student/statistics"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center"
            >
              <ClipboardDocumentListIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Mes statistiques</h4>
              <p className="text-sm text-gray-500">Analyser ma présence</p>
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default StudentDashboard;
