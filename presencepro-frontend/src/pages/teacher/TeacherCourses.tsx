import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import { courseService } from '../../services/courseService';
import { useAuth } from '../../contexts/AuthContext';
import { Course, Schedule, PaginatedResponse } from '../../services/api';
import {
  AcademicCapIcon,
  CalendarDaysIcon,
  UserGroupIcon,
  ClipboardDocumentListIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

// Local interfaces for teacher-specific data
interface TeacherCourseStats {
  totalCourses: number;
  totalStudents: number;
  averageAttendanceRate: number;
  sessionsThisWeek: number;
}

const TeacherCourses: React.FC = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [stats, setStats] = useState<TeacherCourseStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Load teacher's courses from API
  useEffect(() => {
    const loadCourses = async () => {
      if (!user) return;

      setIsLoading(true);

      try {
        // Load teacher's courses from API
        const response = await courseService.getTeacherCourses(user.id);
        setCourses(response.data);

        // Calculate stats from the courses
        const mockStats: TeacherCourseStats = {
          totalCourses: response.data.length,
          totalStudents: response.data.reduce((sum, course) => sum + (course.max_students || 0), 0),
          averageAttendanceRate: 90.5, // This would come from attendance service
          sessionsThisWeek: 12, // This would come from schedule service
        };

        setStats(mockStats);
      } catch (error) {
        console.error('Error loading teacher courses:', error);

        // Fallback to mock data if API fails
        const mockCourses: Course[] = [
          {
            id: 1,
            name: 'Mathématiques Avancées',
            code: 'MATH301',
            description: 'Cours de mathématiques niveau 3ème avec focus sur l\'algèbre et la géométrie.',
            subject: 'Mathématiques',
            level: '3ème',
            credits: 3,
            max_students: 28,
            status: 'active',
            academic_year: '2023-2024',
            semester: 'Semestre 1',
            created_at: '2024-01-10T08:00:00Z',
            updated_at: '2024-01-15T14:30:00Z',
          },
          {
            id: 2,
            name: 'Mathématiques',
            code: 'MATH201',
            description: 'Cours de mathématiques niveau 3ème avec approche pratique.',
            subject: 'Mathématiques',
            level: '3ème',
            credits: 3,
            max_students: 30,
            status: 'active',
            academic_year: '2023-2024',
            semester: 'Semestre 1',
            created_at: '2024-01-08T09:15:00Z',
            updated_at: '2024-01-15T10:45:00Z',
          },
          {
            id: 3,
            name: 'Algèbre Fondamentale',
            code: 'MATH401',
            description: 'Introduction aux concepts fondamentaux de l\'algèbre.',
            subject: 'Mathématiques',
            level: '4ème',
            credits: 3,
            max_students: 25,
            status: 'active',
            academic_year: '2023-2024',
            semester: 'Semestre 1',
            created_at: '2024-01-05T11:20:00Z',
            updated_at: '2024-01-14T16:20:00Z',
          },
        ];

        const mockStats: TeacherCourseStats = {
          totalCourses: mockCourses.length,
          totalStudents: mockCourses.reduce((sum, course) => sum + (course.max_students || 0), 0),
          averageAttendanceRate: 90.5,
          sessionsThisWeek: 12,
        };

        setCourses(mockCourses);
        setStats(mockStats);
      } finally {
        setIsLoading(false);
      }
    };

    loadCourses();
  }, [user]);

  if (isLoading) {
    return (
      <Layout title="Mes cours">
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

  return (
    <Layout title="Mes cours">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Mes cours
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Gérez vos cours et suivez les performances de vos étudiants
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex space-x-2">
            <div className="flex rounded-md shadow-sm">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-2 text-sm font-medium rounded-l-md border ${
                  viewMode === 'grid'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                Grille
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-2 text-sm font-medium rounded-r-md border-t border-r border-b ${
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                Liste
              </button>
            </div>
            <button className="btn-primary">
              <PlusIcon className="h-4 w-4 mr-2" />
              Nouveau cours
            </button>
          </div>
        </div>

        {/* Statistiques */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <AcademicCapIcon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total cours</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalCourses}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserGroupIcon className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total étudiants</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalStudents}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Taux de présence</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.averageAttendanceRate.toFixed(1)}%</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CalendarDaysIcon className="h-8 w-8 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Sessions cette semaine</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.sessionsThisWeek}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Liste des cours */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <div key={course.id} className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <AcademicCapIcon className="h-6 w-6 text-blue-600 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900">{course.name}</h3>
                  </div>
                  <span className="text-sm px-2 py-1 rounded bg-blue-100 text-blue-800">
                    {course.status === 'active' ? 'Actif' : 'Inactif'}
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <UserGroupIcon className="h-4 w-4 mr-2" />
                    <span>{course.level} • {course.max_students} étudiants max</span>
                  </div>

                  <div className="flex items-center text-sm text-gray-600">
                    <ClipboardDocumentListIcon className="h-4 w-4 mr-2" />
                    <span>{course.code} • {course.credits} crédits</span>
                  </div>

                  <div className="flex items-center text-sm text-gray-600">
                    <CalendarDaysIcon className="h-4 w-4 mr-2" />
                    <span>{course.academic_year} - {course.semester}</span>
                  </div>

                  <div className="pt-3 border-t border-gray-200">
                    <p className="text-sm text-gray-500 mb-3">{course.description}</p>
                    <div className="flex space-x-2">
                      <button className="btn-secondary text-sm flex-1">
                        <EyeIcon className="h-4 w-4 mr-1" />
                        Voir
                      </button>
                      <button className="btn-secondary text-sm flex-1">
                        <PencilIcon className="h-4 w-4 mr-1" />
                        Modifier
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cours
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Niveau
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Étudiants Max
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Présence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Crédits
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Année/Semestre
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {courses.map((course) => (
                    <tr key={course.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{course.name}</div>
                          <div className="text-sm text-gray-500">{course.code}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{course.level}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{course.max_students}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="text-sm text-gray-900">90%</div>
                          <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: '90%' }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {course.credits} crédits
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {course.academic_year} - {course.semester}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex space-x-2">
                          <button className="text-blue-600 hover:text-blue-700">
                            <EyeIcon className="h-4 w-4" />
                          </button>
                          <button className="text-gray-600 hover:text-gray-700">
                            <PencilIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Message si aucun cours */}
        {courses.length === 0 && (
          <div className="card p-12 text-center">
            <AcademicCapIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun cours trouvé</h3>
            <p className="mt-1 text-sm text-gray-500">
              Commencez par créer votre premier cours.
            </p>
            <div className="mt-6">
              <button className="btn-primary">
                <PlusIcon className="h-4 w-4 mr-2" />
                Créer un cours
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default TeacherCourses;
