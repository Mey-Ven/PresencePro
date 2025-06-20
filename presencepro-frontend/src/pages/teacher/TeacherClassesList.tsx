import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  UserGroupIcon,
  AcademicCapIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  EyeIcon,
  ClipboardDocumentListIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

// Types pour les classes
interface ClassInfo {
  id: string;
  name: string;
  level: string;
  studentsCount: number;
  coursesCount: number;
  attendanceRate: number;
  recentAbsences: number;
  nextSession?: {
    courseName: string;
    date: string;
    time: string;
    room: string;
  };
  students: {
    id: string;
    firstName: string;
    lastName: string;
    attendanceRate: number;
    recentAbsences: number;
  }[];
  schedule: {
    day: string;
    courseName: string;
    startTime: string;
    endTime: string;
    room: string;
  }[];
}

interface ClassStats {
  totalClasses: number;
  totalStudents: number;
  averageAttendanceRate: number;
  classesWithIssues: number;
}

const TeacherClassesList: React.FC = () => {
  const [classes, setClasses] = useState<ClassInfo[]>([]);
  const [stats, setStats] = useState<ClassStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedClass, setSelectedClass] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'overview' | 'details'>('overview');

  // Simuler le chargement des données
  useEffect(() => {
    const loadClasses = async () => {
      setIsLoading(true);

      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Données simulées
      const mockClasses: ClassInfo[] = [
        {
          id: '1',
          name: '3ème A',
          level: '3ème',
          studentsCount: 28,
          coursesCount: 3,
          attendanceRate: 94.2,
          recentAbsences: 2,
          nextSession: {
            courseName: 'Mathématiques',
            date: '2024-01-16',
            time: '08:00',
            room: 'Salle 101',
          },
          students: [
            { id: '1', firstName: 'Lucas', lastName: 'Moreau', attendanceRate: 96.5, recentAbsences: 1 },
            { id: '2', firstName: 'Emma', lastName: 'Leroy', attendanceRate: 92.3, recentAbsences: 2 },
            { id: '3', firstName: 'Thomas', lastName: 'Dubois', attendanceRate: 89.7, recentAbsences: 3 },
          ],
          schedule: [
            { day: 'Lundi', courseName: 'Mathématiques', startTime: '08:00', endTime: '09:00', room: 'Salle 101' },
            { day: 'Mercredi', courseName: 'Mathématiques', startTime: '10:00', endTime: '11:00', room: 'Salle 101' },
            { day: 'Vendredi', courseName: 'Mathématiques', startTime: '14:00', endTime: '15:00', room: 'Salle 101' },
          ],
        },
        {
          id: '2',
          name: '3ème B',
          level: '3ème',
          studentsCount: 30,
          coursesCount: 2,
          attendanceRate: 89.7,
          recentAbsences: 4,
          nextSession: {
            courseName: 'Mathématiques',
            date: '2024-01-16',
            time: '09:00',
            room: 'Salle 102',
          },
          students: [
            { id: '4', firstName: 'Sophie', lastName: 'Bernard', attendanceRate: 94.1, recentAbsences: 1 },
            { id: '5', firstName: 'Antoine', lastName: 'Rousseau', attendanceRate: 85.3, recentAbsences: 4 },
            { id: '6', firstName: 'Camille', lastName: 'Durand', attendanceRate: 91.8, recentAbsences: 2 },
          ],
          schedule: [
            { day: 'Mardi', courseName: 'Mathématiques', startTime: '09:00', endTime: '10:00', room: 'Salle 102' },
            { day: 'Jeudi', courseName: 'Mathématiques', startTime: '11:00', endTime: '12:00', room: 'Salle 102' },
          ],
        },
        {
          id: '3',
          name: '4ème A',
          level: '4ème',
          studentsCount: 25,
          coursesCount: 2,
          attendanceRate: 91.8,
          recentAbsences: 3,
          nextSession: {
            courseName: 'Algèbre',
            date: '2024-01-19',
            time: '15:00',
            room: 'Salle 103',
          },
          students: [
            { id: '7', firstName: 'Marie', lastName: 'Petit', attendanceRate: 93.2, recentAbsences: 2 },
            { id: '8', firstName: 'Paul', lastName: 'Martin', attendanceRate: 90.4, recentAbsences: 3 },
          ],
          schedule: [
            { day: 'Lundi', courseName: 'Algèbre', startTime: '15:00', endTime: '16:00', room: 'Salle 103' },
            { day: 'Vendredi', courseName: 'Algèbre', startTime: '10:00', endTime: '11:00', room: 'Salle 103' },
          ],
        },
        {
          id: '4',
          name: '4ème B',
          level: '4ème',
          studentsCount: 27,
          coursesCount: 2,
          attendanceRate: 87.3,
          recentAbsences: 5,
          nextSession: {
            courseName: 'Géométrie',
            date: '2024-01-16',
            time: '14:00',
            room: 'Salle 104',
          },
          students: [
            { id: '9', firstName: 'Julie', lastName: 'Moreau', attendanceRate: 88.9, recentAbsences: 3 },
            { id: '10', firstName: 'Kevin', lastName: 'Dubois', attendanceRate: 85.7, recentAbsences: 5 },
          ],
          schedule: [
            { day: 'Mardi', courseName: 'Géométrie', startTime: '14:00', endTime: '15:00', room: 'Salle 104' },
            { day: 'Jeudi', courseName: 'Géométrie', startTime: '08:00', endTime: '09:00', room: 'Salle 104' },
          ],
        },
      ];

      const mockStats: ClassStats = {
        totalClasses: mockClasses.length,
        totalStudents: mockClasses.reduce((sum, cls) => sum + cls.studentsCount, 0),
        averageAttendanceRate: mockClasses.reduce((sum, cls) => sum + cls.attendanceRate, 0) / mockClasses.length,
        classesWithIssues: mockClasses.filter(cls => cls.attendanceRate < 90).length,
      };

      setClasses(mockClasses);
      setStats(mockStats);
      setIsLoading(false);
    };

    loadClasses();
  }, []);

  // Obtenir la classe sélectionnée
  const selectedClassData = classes.find(c => c.id === selectedClass);

  if (isLoading) {
    return (
      <Layout title="Mes classes">
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
    <Layout title="Mes classes">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Mes classes
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Vue d'ensemble de toutes vos classes et leurs performances
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <div className="flex rounded-md shadow-sm">
              <button
                onClick={() => setViewMode('overview')}
                className={`px-3 py-2 text-sm font-medium rounded-l-md border ${
                  viewMode === 'overview'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                Vue d'ensemble
              </button>
              <button
                onClick={() => setViewMode('details')}
                className={`px-3 py-2 text-sm font-medium rounded-r-md border-t border-r border-b ${
                  viewMode === 'details'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                Détails
              </button>
            </div>
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
                  <p className="text-sm font-medium text-gray-500">Total classes</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalClasses}</p>
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
                  <p className="text-sm font-medium text-gray-500">Taux moyen</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.averageAttendanceRate.toFixed(1)}%</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Classes à risque</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.classesWithIssues}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Vue d'ensemble */}
        {viewMode === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {classes.map((classInfo) => (
              <div key={classInfo.id} className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <AcademicCapIcon className="h-6 w-6 text-blue-600 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900">{classInfo.name}</h3>
                  </div>
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

                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <UserGroupIcon className="h-4 w-4 mr-2" />
                    <span>{classInfo.studentsCount} étudiants • {classInfo.coursesCount} cours</span>
                  </div>

                  <div className="flex items-center text-sm text-gray-600">
                    <ExclamationTriangleIcon className="h-4 w-4 mr-2" />
                    <span>{classInfo.recentAbsences} absence{classInfo.recentAbsences > 1 ? 's' : ''} récente{classInfo.recentAbsences > 1 ? 's' : ''}</span>
                  </div>

                  {classInfo.nextSession && (
                    <div className="flex items-center text-sm text-gray-600">
                      <CalendarDaysIcon className="h-4 w-4 mr-2" />
                      <span>
                        Prochain: {classInfo.nextSession.courseName} le {new Date(classInfo.nextSession.date).toLocaleDateString('fr-FR')} à {classInfo.nextSession.time}
                      </span>
                    </div>
                  )}

                  <div className="pt-3 border-t border-gray-200">
                    <button
                      onClick={() => {
                        setSelectedClass(classInfo.id);
                        setViewMode('details');
                      }}
                      className="btn-secondary text-sm w-full"
                    >
                      <EyeIcon className="h-4 w-4 mr-1" />
                      Voir les détails
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Vue détaillée */}
        {viewMode === 'details' && (
          <div className="space-y-6">
            {/* Sélection de classe */}
            <div className="card p-4">
              <select
                className="input"
                value={selectedClass || ''}
                onChange={(e) => setSelectedClass(e.target.value)}
              >
                <option value="">Sélectionnez une classe</option>
                {classes.map((classInfo) => (
                  <option key={classInfo.id} value={classInfo.id}>
                    {classInfo.name} ({classInfo.studentsCount} étudiants)
                  </option>
                ))}
              </select>
            </div>

            {selectedClassData && (
              <>
                {/* Informations de la classe */}
                <div className="card p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">
                    Classe {selectedClassData.name}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{selectedClassData.studentsCount}</div>
                      <div className="text-sm text-gray-500">Étudiants</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{selectedClassData.attendanceRate}%</div>
                      <div className="text-sm text-gray-500">Taux de présence</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{selectedClassData.recentAbsences}</div>
                      <div className="text-sm text-gray-500">Absences récentes</div>
                    </div>
                  </div>
                </div>

                {/* Planning de la classe */}
                <div className="card p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">
                    Planning des cours
                  </h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Jour
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Cours
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Horaire
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Salle
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {selectedClassData.schedule.map((session, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 text-sm text-gray-900">{session.day}</td>
                            <td className="px-6 py-4 text-sm text-gray-900">{session.courseName}</td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {session.startTime} - {session.endTime}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">{session.room}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Liste des étudiants */}
                <div className="card p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">
                    Étudiants de la classe
                  </h4>
                  <div className="space-y-3">
                    {selectedClassData.students.map((student) => (
                      <div key={student.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-medium text-gray-900">
                            {student.firstName} {student.lastName}
                          </div>
                          <div className="text-sm text-gray-500">
                            {student.recentAbsences} absence{student.recentAbsences > 1 ? 's' : ''} récente{student.recentAbsences > 1 ? 's' : ''}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`text-sm font-medium ${
                            student.attendanceRate >= 90 ? 'text-green-600' :
                            student.attendanceRate >= 80 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {student.attendanceRate}%
                          </div>
                          <div className="text-xs text-gray-500">Présence</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* Message si aucune classe */}
        {classes.length === 0 && (
          <div className="card p-12 text-center">
            <AcademicCapIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune classe trouvée</h3>
            <p className="mt-1 text-sm text-gray-500">
              Vous n'avez pas encore de classes assignées.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default TeacherClassesList;
