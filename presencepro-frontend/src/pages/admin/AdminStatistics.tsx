import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import PowerBIChart from '../../components/charts/PowerBIChart';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarDaysIcon,
  UserGroupIcon,
  AcademicCapIcon,
  ExclamationTriangleIcon,
  DocumentArrowDownIcon,
} from '@heroicons/react/24/outline';

// Types pour les statistiques
interface GlobalStats {
  totalStudents: number;
  totalTeachers: number;
  totalClasses: number;
  averageAttendanceRate: number;
  totalAbsencesToday: number;
  totalAbsencesWeek: number;
  totalAbsencesMonth: number;
  attendanceTrend: 'up' | 'down' | 'stable';
}

interface ClassStats {
  className: string;
  studentsCount: number;
  attendanceRate: number;
  absencesCount: number;
  trend: 'up' | 'down' | 'stable';
}

interface TeacherStats {
  teacherName: string;
  coursesCount: number;
  studentsCount: number;
  attendanceRate: number;
  absencesReported: number;
}

interface PeriodStats {
  period: string;
  attendanceRate: number;
  absencesCount: number;
  studentsCount: number;
}

const AdminStatistics: React.FC = () => {
  const [globalStats, setGlobalStats] = useState<GlobalStats | null>(null);
  const [classStats, setClassStats] = useState<ClassStats[]>([]);
  const [teacherStats, setTeacherStats] = useState<TeacherStats[]>([]);
  const [periodStats, setPeriodStats] = useState<PeriodStats[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('month');

  // Simuler le chargement des données
  useEffect(() => {
    const loadStatistics = async () => {
      setIsLoading(true);

      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1200));

      // Données simulées
      const mockGlobalStats: GlobalStats = {
        totalStudents: 450,
        totalTeachers: 28,
        totalClasses: 18,
        averageAttendanceRate: 87.3,
        totalAbsencesToday: 23,
        totalAbsencesWeek: 156,
        totalAbsencesMonth: 678,
        attendanceTrend: 'up',
      };

      const mockClassStats: ClassStats[] = [
        { className: '3ème A', studentsCount: 28, attendanceRate: 92.1, absencesCount: 12, trend: 'up' },
        { className: '3ème B', studentsCount: 26, attendanceRate: 89.4, absencesCount: 18, trend: 'stable' },
        { className: '4ème A', studentsCount: 30, attendanceRate: 85.7, absencesCount: 25, trend: 'down' },
        { className: '4ème B', studentsCount: 27, attendanceRate: 91.2, absencesCount: 14, trend: 'up' },
        { className: '5ème A', studentsCount: 29, attendanceRate: 88.9, absencesCount: 19, trend: 'stable' },
        { className: '5ème B', studentsCount: 25, attendanceRate: 83.2, absencesCount: 28, trend: 'down' },
      ];

      const mockTeacherStats: TeacherStats[] = [
        { teacherName: 'Jean Martin', coursesCount: 4, studentsCount: 89, attendanceRate: 91.5, absencesReported: 45 },
        { teacherName: 'Sophie Bernard', coursesCount: 3, studentsCount: 67, attendanceRate: 88.2, absencesReported: 38 },
        { teacherName: 'Claire Dubois', coursesCount: 5, studentsCount: 112, attendanceRate: 85.7, absencesReported: 67 },
        { teacherName: 'Pierre Moreau', coursesCount: 3, studentsCount: 78, attendanceRate: 89.9, absencesReported: 42 },
      ];

      const mockPeriodStats: PeriodStats[] = [
        { period: 'Janvier 2024', attendanceRate: 87.3, absencesCount: 678, studentsCount: 450 },
        { period: 'Décembre 2023', attendanceRate: 85.1, absencesCount: 712, studentsCount: 445 },
        { period: 'Novembre 2023', attendanceRate: 89.2, absencesCount: 589, studentsCount: 442 },
        { period: 'Octobre 2023', attendanceRate: 91.4, absencesCount: 523, studentsCount: 438 },
        { period: 'Septembre 2023', attendanceRate: 93.7, absencesCount: 412, studentsCount: 435 },
      ];

      setGlobalStats(mockGlobalStats);
      setClassStats(mockClassStats);
      setTeacherStats(mockTeacherStats);
      setPeriodStats(mockPeriodStats);
      setIsLoading(false);
    };

    loadStatistics();
  }, [selectedPeriod]);

  // Obtenir l'icône de tendance
  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />;
      case 'down':
        return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />;
      default:
        return <div className="h-4 w-4 bg-gray-400 rounded-full"></div>;
    }
  };

  if (isLoading) {
    return (
      <Layout title="Statistiques globales">
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

  if (!globalStats) {
    return (
      <Layout title="Statistiques globales">
        <div className="text-center py-12">
          <p className="text-gray-500">Erreur lors du chargement des statistiques</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Statistiques globales">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Statistiques globales
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Vue d'ensemble des performances de présence de l'établissement
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex space-x-2">
            <select
              className="input"
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value as 'week' | 'month' | 'year')}
            >
              <option value="week">Cette semaine</option>
              <option value="month">Ce mois</option>
              <option value="year">Cette année</option>
            </select>
            <button className="btn-secondary">
              <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
              Exporter
            </button>
          </div>
        </div>

        {/* Statistiques principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total étudiants</p>
                <p className="text-2xl font-bold text-gray-900">{globalStats.totalStudents}</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AcademicCapIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Enseignants</p>
                <p className="text-2xl font-bold text-gray-900">{globalStats.totalTeachers}</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500">Taux de présence</p>
                <div className="flex items-center">
                  <p className="text-2xl font-bold text-gray-900">{globalStats.averageAttendanceRate}%</p>
                  <div className="ml-2">
                    {getTrendIcon(globalStats.attendanceTrend)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Absences ce mois</p>
                <p className="text-2xl font-bold text-gray-900">{globalStats.totalAbsencesMonth}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Graphiques */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Graphique d'évolution */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Évolution du taux de présence
            </h3>
            <PowerBIChart
              title="Évolution du taux de présence"
              chartType="line"
              mockData={{
                labels: periodStats.map(stat => stat.period),
                data: periodStats.map(stat => stat.attendanceRate),
              }}
              height="300px"
            />
          </div>

          {/* Graphique des absences */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Absences par période
            </h3>
            <PowerBIChart
              title="Absences par période"
              chartType="bar"
              mockData={{
                labels: periodStats.map(stat => stat.period),
                data: periodStats.map(stat => stat.absencesCount),
              }}
              height="300px"
            />
          </div>
        </div>

        {/* Statistiques par classe */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Performance par classe
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Classe
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Étudiants
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Taux de présence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Absences
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tendance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {classStats.map((classData) => (
                  <tr key={classData.className} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {classData.className}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{classData.studentsCount}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="text-sm text-gray-900">{classData.attendanceRate}%</div>
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${classData.attendanceRate}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{classData.absencesCount}</div>
                    </td>
                    <td className="px-6 py-4">
                      {getTrendIcon(classData.trend)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Statistiques par enseignant */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Performance par enseignant
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Enseignant
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cours
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Étudiants
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Taux de présence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Absences signalées
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {teacherStats.map((teacher) => (
                  <tr key={teacher.teacherName} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {teacher.teacherName}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{teacher.coursesCount}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{teacher.studentsCount}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="text-sm text-gray-900">{teacher.attendanceRate}%</div>
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: `${teacher.attendanceRate}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{teacher.absencesReported}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AdminStatistics;
