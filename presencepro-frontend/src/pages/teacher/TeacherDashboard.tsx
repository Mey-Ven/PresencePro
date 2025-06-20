import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  AcademicCapIcon,
  ClipboardDocumentListIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  UserGroupIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

// Interface pour les statistiques du dashboard enseignant
interface TeacherDashboardStats {
  totalCourses: number;
  totalStudents: number;
  todayClasses: number;
  pendingAttendance: number;
  todayAbsences: number;
  weeklyAttendanceRate: number;
  recentActivity: TeacherActivityItem[];
  todaySchedule: ClassSchedule[];
  myClasses: ClassInfo[];
}

interface TeacherActivityItem {
  id: string;
  type: 'attendance_taken' | 'absence_marked' | 'justification_received';
  message: string;
  timestamp: string;
  className?: string;
}

interface ClassSchedule {
  id: string;
  courseName: string;
  className: string;
  startTime: string;
  endTime: string;
  room: string;
  studentsCount: number;
  attendanceTaken: boolean;
}

interface ClassInfo {
  id: string;
  name: string;
  courseName: string;
  studentsCount: number;
  attendanceRate: number;
  lastAttendance: string;
}

// Composant Dashboard Enseignant
const TeacherDashboard: React.FC = () => {
  const [stats, setStats] = useState<TeacherDashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Simuler le chargement des données
  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true);
      
      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Données simulées pour l'enseignant
      const mockStats: TeacherDashboardStats = {
        totalCourses: 4,
        totalStudents: 89,
        todayClasses: 3,
        pendingAttendance: 1,
        todayAbsences: 7,
        weeklyAttendanceRate: 92.5,
        recentActivity: [
          {
            id: '1',
            type: 'attendance_taken',
            message: 'Présence prise pour Mathématiques - 3ème A',
            timestamp: '2024-01-15T10:30:00Z',
            className: '3ème A',
          },
          {
            id: '2',
            type: 'absence_marked',
            message: 'Jean Dupont marqué absent en Physique',
            timestamp: '2024-01-15T09:15:00Z',
            className: '4ème B',
          },
          {
            id: '3',
            type: 'justification_received',
            message: 'Justification reçue de Marie Martin',
            timestamp: '2024-01-15T08:45:00Z',
            className: '3ème A',
          },
        ],
        todaySchedule: [
          {
            id: '1',
            courseName: 'Mathématiques',
            className: '3ème A',
            startTime: '08:00',
            endTime: '09:00',
            room: 'Salle 101',
            studentsCount: 28,
            attendanceTaken: true,
          },
          {
            id: '2',
            courseName: 'Physique',
            className: '4ème B',
            startTime: '10:00',
            endTime: '11:00',
            room: 'Labo 2',
            studentsCount: 25,
            attendanceTaken: false,
          },
          {
            id: '3',
            courseName: 'Mathématiques',
            className: '3ème B',
            startTime: '14:00',
            endTime: '15:00',
            room: 'Salle 101',
            studentsCount: 30,
            attendanceTaken: false,
          },
        ],
        myClasses: [
          {
            id: '1',
            name: '3ème A',
            courseName: 'Mathématiques',
            studentsCount: 28,
            attendanceRate: 94.2,
            lastAttendance: '2024-01-15',
          },
          {
            id: '2',
            name: '3ème B',
            courseName: 'Mathématiques',
            studentsCount: 30,
            attendanceRate: 89.7,
            lastAttendance: '2024-01-14',
          },
          {
            id: '3',
            name: '4ème B',
            courseName: 'Physique',
            studentsCount: 25,
            attendanceRate: 91.8,
            lastAttendance: '2024-01-15',
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
      <Layout title="Tableau de bord - Enseignant">
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
      <Layout title="Tableau de bord - Enseignant">
        <div className="text-center py-12">
          <p className="text-gray-500">Erreur lors du chargement des données</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Tableau de bord - Enseignant">
      <div className="space-y-6">
        {/* Message de bienvenue */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-medium text-blue-900 mb-2">
            Bonjour ! Voici votre planning du jour
          </h2>
          <p className="text-blue-700">
            Vous avez {stats.todayClasses} cours aujourd'hui et {stats.pendingAttendance} présence en attente.
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
                to="/teacher/courses"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Gérer mes cours →
              </Link>
            </div>
          </div>

          {/* Total étudiants */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Mes étudiants</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalStudents}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/teacher/students"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Voir la liste →
              </Link>
            </div>
          </div>

          {/* Présences en attente */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClipboardDocumentListIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Présences en attente</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pendingAttendance}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/teacher/attendance"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Prendre présence →
              </Link>
            </div>
          </div>

          {/* Absences aujourd'hui */}
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Absences aujourd'hui</p>
                <p className="text-2xl font-bold text-gray-900">{stats.todayAbsences}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/teacher/absences"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Voir les détails →
              </Link>
            </div>
          </div>
        </div>

        {/* Planning du jour et activité récente */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Planning du jour */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <CalendarDaysIcon className="h-5 w-5 mr-2" />
              Planning du jour
            </h3>
            <div className="space-y-4">
              {stats.todaySchedule.map((schedule) => (
                <div
                  key={schedule.id}
                  className={`p-4 rounded-lg border ${
                    schedule.attendanceTaken
                      ? 'bg-green-50 border-green-200'
                      : 'bg-yellow-50 border-yellow-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {schedule.courseName} - {schedule.className}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {schedule.startTime} - {schedule.endTime} • {schedule.room}
                      </p>
                      <p className="text-sm text-gray-500">
                        {schedule.studentsCount} étudiants
                      </p>
                    </div>
                    <div className="flex items-center">
                      {schedule.attendanceTaken ? (
                        <CheckCircleIcon className="h-6 w-6 text-green-600" />
                      ) : (
                        <XCircleIcon className="h-6 w-6 text-yellow-600" />
                      )}
                    </div>
                  </div>
                  {!schedule.attendanceTaken && (
                    <div className="mt-3">
                      <button className="btn-primary text-sm">
                        Prendre présence
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Activité récente */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Activité récente
            </h3>
            <div className="space-y-4">
              {stats.recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {activity.type === 'attendance_taken' && (
                      <CheckCircleIcon className="h-5 w-5 text-green-500" />
                    )}
                    {activity.type === 'absence_marked' && (
                      <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
                    )}
                    {activity.type === 'justification_received' && (
                      <DocumentTextIcon className="h-5 w-5 text-blue-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(activity.timestamp).toLocaleString('fr-FR')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Mes classes */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Mes classes
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {stats.myClasses.map((classInfo) => (
              <div key={classInfo.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{classInfo.name}</h4>
                  <span className={`text-sm px-2 py-1 rounded ${
                    classInfo.attendanceRate >= 90
                      ? 'bg-green-100 text-green-800'
                      : classInfo.attendanceRate >= 80
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {classInfo.attendanceRate}%
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-1">{classInfo.courseName}</p>
                <p className="text-sm text-gray-500 mb-3">
                  {classInfo.studentsCount} étudiants
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">
                    Dernière présence: {new Date(classInfo.lastAttendance).toLocaleDateString('fr-FR')}
                  </span>
                  <Link
                    to={`/teacher/classes/${classInfo.id}`}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    Voir →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default TeacherDashboard;
