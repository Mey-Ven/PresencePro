import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  UserGroupIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  EnvelopeIcon,
  PhoneIcon,
} from '@heroicons/react/24/outline';

// Types pour les étudiants
interface Student {
  id: string;
  firstName: string;
  lastName: string;
  studentNumber: string;
  email: string;
  phone?: string;
  className: string;
  courses: string[];
  attendanceRate: number;
  totalAbsences: number;
  recentAbsences: number;
  lastAttendance: string;
  parentName: string;
  parentEmail: string;
  parentPhone?: string;
  status: 'active' | 'inactive' | 'at_risk';
  photo?: string;
}

interface StudentStats {
  totalStudents: number;
  averageAttendanceRate: number;
  atRiskStudents: number;
  activeStudents: number;
}

const TeacherStudents: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [stats, setStats] = useState<StudentStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [classFilter, setClassFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  // Simuler le chargement des données
  useEffect(() => {
    const loadStudents = async () => {
      setIsLoading(true);

      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Données simulées
      const mockStudents: Student[] = [
        {
          id: '1',
          firstName: 'Lucas',
          lastName: 'Moreau',
          studentNumber: '2024001',
          email: 'lucas.moreau@student.presencepro.fr',
          phone: '+33 6 12 34 56 78',
          className: '3ème A',
          courses: ['Mathématiques', 'Physique'],
          attendanceRate: 94.2,
          totalAbsences: 3,
          recentAbsences: 1,
          lastAttendance: '2024-01-15',
          parentName: 'Pierre Moreau',
          parentEmail: 'pierre.moreau@email.com',
          parentPhone: '+33 6 23 45 67 89',
          status: 'active',
        },
        {
          id: '2',
          firstName: 'Emma',
          lastName: 'Leroy',
          studentNumber: '2024002',
          email: 'emma.leroy@student.presencepro.fr',
          className: '3ème A',
          courses: ['Mathématiques', 'Français'],
          attendanceRate: 89.7,
          totalAbsences: 6,
          recentAbsences: 2,
          lastAttendance: '2024-01-14',
          parentName: 'Marie Leroy',
          parentEmail: 'marie.leroy@email.com',
          status: 'active',
        },
        {
          id: '3',
          firstName: 'Thomas',
          lastName: 'Dubois',
          studentNumber: '2024003',
          email: 'thomas.dubois@student.presencepro.fr',
          className: '3ème B',
          courses: ['Mathématiques'],
          attendanceRate: 76.3,
          totalAbsences: 12,
          recentAbsences: 4,
          lastAttendance: '2024-01-12',
          parentName: 'Claire Dubois',
          parentEmail: 'claire.dubois@email.com',
          status: 'at_risk',
        },
        {
          id: '4',
          firstName: 'Marie',
          lastName: 'Petit',
          studentNumber: '2024004',
          email: 'marie.petit@student.presencepro.fr',
          className: '4ème A',
          courses: ['Mathématiques', 'Géométrie'],
          attendanceRate: 91.8,
          totalAbsences: 4,
          recentAbsences: 0,
          lastAttendance: '2024-01-15',
          parentName: 'Jean Petit',
          parentEmail: 'jean.petit@email.com',
          status: 'active',
        },
        {
          id: '5',
          firstName: 'Paul',
          lastName: 'Martin',
          studentNumber: '2024005',
          email: 'paul.martin@student.presencepro.fr',
          className: '4ème B',
          courses: ['Géométrie'],
          attendanceRate: 87.3,
          totalAbsences: 7,
          recentAbsences: 1,
          lastAttendance: '2024-01-15',
          parentName: 'Sophie Martin',
          parentEmail: 'sophie.martin@email.com',
          status: 'active',
        },
      ];

      const mockStats: StudentStats = {
        totalStudents: mockStudents.length,
        averageAttendanceRate: mockStudents.reduce((sum, s) => sum + s.attendanceRate, 0) / mockStudents.length,
        atRiskStudents: mockStudents.filter(s => s.status === 'at_risk').length,
        activeStudents: mockStudents.filter(s => s.status === 'active').length,
      };

      setStudents(mockStudents);
      setStats(mockStats);
      setIsLoading(false);
    };

    loadStudents();
  }, []);

  // Filtrer les étudiants
  const filteredStudents = students.filter(student => {
    const matchesSearch = searchQuery === '' ||
      student.firstName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student.lastName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student.studentNumber.includes(searchQuery) ||
      student.email.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesClass = classFilter === 'all' || student.className === classFilter;
    const matchesStatus = statusFilter === 'all' || student.status === statusFilter;

    return matchesSearch && matchesClass && matchesStatus;
  });

  // Obtenir le badge de statut
  const getStatusBadge = (status: string, attendanceRate: number) => {
    if (status === 'at_risk' || attendanceRate < 80) {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md bg-red-100 text-red-800">
          <ExclamationTriangleIcon className="h-3 w-3 mr-1" />
          À risque
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md bg-green-100 text-green-800">
        <CheckCircleIcon className="h-3 w-3 mr-1" />
        Actif
      </span>
    );
  };

  if (isLoading) {
    return (
      <Layout title="Mes étudiants">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des étudiants..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Mes étudiants">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Mes étudiants
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Suivez les performances et la présence de vos étudiants
            </p>
          </div>
        </div>

        {/* Statistiques */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserGroupIcon className="h-8 w-8 text-blue-600" />
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
                  <ChartBarIcon className="h-8 w-8 text-green-600" />
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
                  <CheckCircleIcon className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Actifs</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.activeStudents}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">À risque</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.atRiskStudents}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filtres */}
        <div className="card p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Recherche */}
            <div>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher un étudiant..."
                  className="input pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            {/* Filtre par classe */}
            <div>
              <select
                className="input"
                value={classFilter}
                onChange={(e) => setClassFilter(e.target.value)}
              >
                <option value="all">Toutes les classes</option>
                <option value="3ème A">3ème A</option>
                <option value="3ème B">3ème B</option>
                <option value="4ème A">4ème A</option>
                <option value="4ème B">4ème B</option>
              </select>
            </div>

            {/* Filtre par statut */}
            <div>
              <select
                className="input"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="all">Tous les statuts</option>
                <option value="active">Actifs</option>
                <option value="at_risk">À risque</option>
                <option value="inactive">Inactifs</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tableau des étudiants */}
        <div className="card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Liste des étudiants ({filteredStudents.length})
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Étudiant
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Classe
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Présence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Absences
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Parent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredStudents.map((student) => (
                  <tr key={student.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          {student.photo ? (
                            <img
                              className="h-10 w-10 rounded-full object-cover"
                              src={student.photo}
                              alt={`${student.firstName} ${student.lastName}`}
                            />
                          ) : (
                            <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                              <span className="text-sm font-medium text-gray-600">
                                {student.firstName.charAt(0)}{student.lastName.charAt(0)}
                              </span>
                            </div>
                          )}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {student.firstName} {student.lastName}
                          </div>
                          <div className="text-sm text-gray-500">
                            {student.studentNumber} • {student.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{student.className}</div>
                      <div className="text-sm text-gray-500">
                        {student.courses.join(', ')}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="text-sm text-gray-900">{student.attendanceRate}%</div>
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              student.attendanceRate >= 90 ? 'bg-green-600' :
                              student.attendanceRate >= 80 ? 'bg-yellow-600' : 'bg-red-600'
                            }`}
                            style={{ width: `${student.attendanceRate}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{student.totalAbsences} total</div>
                      <div className="text-sm text-gray-500">{student.recentAbsences} récentes</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{student.parentName}</div>
                      <div className="flex items-center space-x-2 mt-1">
                        <a href={`mailto:${student.parentEmail}`} className="text-blue-600 hover:text-blue-700">
                          <EnvelopeIcon className="h-4 w-4" />
                        </a>
                        {student.parentPhone && (
                          <a href={`tel:${student.parentPhone}`} className="text-green-600 hover:text-green-700">
                            <PhoneIcon className="h-4 w-4" />
                          </a>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(student.status, student.attendanceRate)}
                    </td>
                    <td className="px-6 py-4">
                      <button className="text-blue-600 hover:text-blue-700">
                        <EyeIcon className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Message si aucun étudiant */}
        {filteredStudents.length === 0 && (
          <div className="card p-12 text-center">
            <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun étudiant trouvé</h3>
            <p className="mt-1 text-sm text-gray-500">
              Aucun étudiant ne correspond aux critères de recherche.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default TeacherStudents;
