import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import PowerBIChart from '../../components/charts/PowerBIChart';
import {
  UserIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';

// Types pour les données parent
interface Child {
  id: string;
  firstName: string;
  lastName: string;
  className: string;
  studentNumber: string;
  photo?: string;
}

interface AttendanceRecord {
  id: string;
  date: string;
  courseName: string;
  teacherName: string;
  startTime: string;
  endTime: string;
  status: 'present' | 'absent' | 'late' | 'justified';
  justificationStatus?: 'pending' | 'approved' | 'rejected';
  justificationReason?: string;
  canJustify: boolean;
}

interface AttendanceStats {
  totalSessions: number;
  presentSessions: number;
  absentSessions: number;
  lateSessions: number;
  attendanceRate: number;
  thisWeekAbsences: number;
  unjustifiedAbsences: number;
}

const ParentAttendance: React.FC = () => {
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChild, setSelectedChild] = useState<string | null>(null);
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [stats, setStats] = useState<AttendanceStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'semester'>('month');

  // Simuler le chargement des données
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);

      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Données simulées
      const mockChildren: Child[] = [
        {
          id: '1',
          firstName: 'Lucas',
          lastName: 'Moreau',
          className: '3ème A',
          studentNumber: '2024001',
        },
        {
          id: '2',
          firstName: 'Emma',
          lastName: 'Moreau',
          className: '5ème B',
          studentNumber: '2024002',
        },
      ];

      const mockRecords: AttendanceRecord[] = [
        {
          id: '1',
          date: '2024-01-15',
          courseName: 'Mathématiques',
          teacherName: 'Jean Martin',
          startTime: '08:00',
          endTime: '09:00',
          status: 'absent',
          justificationStatus: 'pending',
          justificationReason: 'Rendez-vous médical',
          canJustify: false,
        },
        {
          id: '2',
          date: '2024-01-14',
          courseName: 'Physique',
          teacherName: 'Sophie Bernard',
          startTime: '10:00',
          endTime: '11:00',
          status: 'present',
          canJustify: false,
        },
        {
          id: '3',
          date: '2024-01-13',
          courseName: 'Histoire',
          teacherName: 'Claire Dubois',
          startTime: '14:00',
          endTime: '15:00',
          status: 'late',
          canJustify: true,
        },
        {
          id: '4',
          date: '2024-01-12',
          courseName: 'Français',
          teacherName: 'Marie Durand',
          startTime: '09:00',
          endTime: '10:00',
          status: 'justified',
          justificationStatus: 'approved',
          justificationReason: 'Maladie',
          canJustify: false,
        },
        {
          id: '5',
          date: '2024-01-11',
          courseName: 'Mathématiques',
          teacherName: 'Jean Martin',
          startTime: '08:00',
          endTime: '09:00',
          status: 'absent',
          canJustify: true,
        },
      ];

      const mockStats: AttendanceStats = {
        totalSessions: 42,
        presentSessions: 36,
        absentSessions: 4,
        lateSessions: 2,
        attendanceRate: 85.7,
        thisWeekAbsences: 2,
        unjustifiedAbsences: 2,
      };

      setChildren(mockChildren);
      setSelectedChild(mockChildren[0].id);
      setAttendanceRecords(mockRecords);
      setStats(mockStats);
      setIsLoading(false);
    };

    loadData();
  }, []);

  // Obtenir l'enfant sélectionné
  const currentChild = children.find(c => c.id === selectedChild);

  // Obtenir le badge de statut
  const getStatusBadge = (status: string, justificationStatus?: string) => {
    if (status === 'absent' && justificationStatus) {
      const justificationBadges = {
        pending: 'bg-yellow-100 text-yellow-800',
        approved: 'bg-green-100 text-green-800',
        rejected: 'bg-red-100 text-red-800',
      };

      const justificationLabels = {
        pending: 'Justification en attente',
        approved: 'Absence justifiée',
        rejected: 'Justification rejetée',
      };

      return (
        <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md ${justificationBadges[justificationStatus as keyof typeof justificationBadges]}`}>
          <DocumentTextIcon className="h-3 w-3 mr-1" />
          {justificationLabels[justificationStatus as keyof typeof justificationLabels]}
        </span>
      );
    }

    const badges = {
      present: 'bg-green-100 text-green-800',
      absent: 'bg-red-100 text-red-800',
      late: 'bg-yellow-100 text-yellow-800',
      justified: 'bg-blue-100 text-blue-800',
    };

    const labels = {
      present: 'Présent',
      absent: 'Absent',
      late: 'Retard',
      justified: 'Justifié',
    };

    const icons = {
      present: <CheckCircleIcon className="h-3 w-3 mr-1" />,
      absent: <XCircleIcon className="h-3 w-3 mr-1" />,
      late: <ExclamationTriangleIcon className="h-3 w-3 mr-1" />,
      justified: <DocumentTextIcon className="h-3 w-3 mr-1" />,
    };

    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md ${badges[status as keyof typeof badges]}`}>
        {icons[status as keyof typeof icons]}
        {labels[status as keyof typeof labels]}
      </span>
    );
  };

  // Contacter l'enseignant
  const contactTeacher = (teacherName: string) => {
    // Simulation d'ouverture de la messagerie
    alert(`Contacter ${teacherName} - Fonctionnalité de messagerie à implémenter`);
  };

  if (isLoading) {
    return (
      <Layout title="Absences de mon enfant">
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
    <Layout title="Absences de mon enfant">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Absences de mon enfant
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Suivez l'assiduité et gérez les justifications
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex space-x-2">
            {/* Sélection de l'enfant */}
            {children.length > 1 && (
              <select
                className="input"
                value={selectedChild || ''}
                onChange={(e) => setSelectedChild(e.target.value)}
              >
                {children.map((child) => (
                  <option key={child.id} value={child.id}>
                    {child.firstName} {child.lastName} ({child.className})
                  </option>
                ))}
              </select>
            )}
            {/* Sélection de la période */}
            <select
              className="input"
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value as any)}
            >
              <option value="week">Cette semaine</option>
              <option value="month">Ce mois</option>
              <option value="semester">Ce semestre</option>
            </select>
          </div>
        </div>

        {/* Informations de l'enfant */}
        {currentChild && (
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 h-16 w-16">
                {currentChild.photo ? (
                  <img
                    className="h-16 w-16 rounded-full object-cover"
                    src={currentChild.photo}
                    alt={`${currentChild.firstName} ${currentChild.lastName}`}
                  />
                ) : (
                  <div className="h-16 w-16 rounded-full bg-gray-300 flex items-center justify-center">
                    <UserIcon className="h-8 w-8 text-gray-600" />
                  </div>
                )}
              </div>
              <div className="ml-6">
                <h2 className="text-xl font-bold text-gray-900">
                  {currentChild.firstName} {currentChild.lastName}
                </h2>
                <p className="text-sm text-gray-500">
                  Classe: {currentChild.className} • N° étudiant: {currentChild.studentNumber}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Statistiques */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Taux de présence</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.attendanceRate}%</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Sessions présent</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.presentSessions}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <XCircleIcon className="h-8 w-8 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Absences cette semaine</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.thisWeekAbsences}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ExclamationTriangleIcon className="h-8 w-8 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Non justifiées</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.unjustifiedAbsences}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Graphique d'évolution */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Évolution de la présence
          </h3>
          <PowerBIChart
            title="Évolution de la présence"
            chartType="line"
            mockData={{
              labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5'],
              data: [92, 88, 85, 89, 86],
            }}
            height="300px"
          />
        </div>

        {/* Historique des présences */}
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Historique des présences
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cours
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Horaire
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Enseignant
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
                {attendanceRecords.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <CalendarDaysIcon className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900">
                          {new Date(record.date).toLocaleDateString('fr-FR')}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{record.courseName}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center text-sm text-gray-900">
                        <ClockIcon className="h-4 w-4 text-gray-400 mr-1" />
                        {record.startTime} - {record.endTime}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{record.teacherName}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        {getStatusBadge(record.status, record.justificationStatus)}
                        {record.justificationReason && (
                          <div className="text-xs text-gray-500">
                            Raison: {record.justificationReason}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex space-x-2">
                        {record.canJustify && (
                          <button className="text-blue-600 hover:text-blue-700 text-sm">
                            Justifier
                          </button>
                        )}
                        <button
                          onClick={() => contactTeacher(record.teacherName)}
                          className="text-green-600 hover:text-green-700"
                        >
                          <EnvelopeIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Actions rapides */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Actions rapides
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="btn-primary">
              <DocumentTextIcon className="h-4 w-4 mr-2" />
              Justifier une absence
            </button>
            <button className="btn-secondary">
              <EnvelopeIcon className="h-4 w-4 mr-2" />
              Contacter l'école
            </button>
            <button className="btn-secondary">
              <CalendarDaysIcon className="h-4 w-4 mr-2" />
              Voir le planning
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ParentAttendance;
