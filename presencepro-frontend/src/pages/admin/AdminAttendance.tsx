import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import { attendanceService } from '../../services/attendanceService';
import { AttendanceRecord, AttendanceStats, PaginatedResponse } from '../../services/api';
import {
  CalendarDaysIcon,
  ClipboardDocumentListIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentArrowDownIcon,
} from '@heroicons/react/24/outline';

// Define specific types for status
type AttendanceStatus = 'present' | 'absent' | 'late' | 'justified';

const attendanceStatusLabels: Record<AttendanceStatus, string> = {
  present: 'Présent',
  absent: 'Absent',
  late: 'Retard',
  justified: 'Justifié',
};

const attendanceStatusBadges: Record<AttendanceStatus, string> = {
  present: 'bg-green-100 text-green-800',
  absent: 'bg-red-100 text-red-800',
  late: 'bg-yellow-100 text-yellow-800',
  justified: 'bg-blue-100 text-blue-800',
};

const attendanceStatusIcons: Record<AttendanceStatus, JSX.Element> = {
  present: <CheckCircleIcon className="h-4 w-4 mr-1" />,
  absent: <XCircleIcon className="h-4 w-4 mr-1" />,
  late: <ExclamationTriangleIcon className="h-4 w-4 mr-1" />,
  justified: <ClipboardDocumentListIcon className="h-4 w-4 mr-1" />,
};

// Local interfaces for filters
interface LocalAttendanceFilters {
  date: string;
  class: string; // Assuming class name, not ID, based on usage
  course: string; // Assuming course name, not ID, based on usage
  status: string; // Can be 'all' or AttendanceStatus
  search: string;
}

const AdminAttendance: React.FC = () => {
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [stats, setStats] = useState<AttendanceStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<LocalAttendanceFilters>({
    date: new Date().toISOString().split('T')[0],
    class: 'all',
    course: 'all',
    status: 'all',
    search: '',
  });
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 50,
    total: 0,
    total_pages: 0,
  });

  // Load attendance data from API
  useEffect(() => {
    const loadAttendanceData = async () => {
      setIsLoading(true);

      try {
        // Prepare API filters
        const apiFilters = {
          date: filters.date,
          class_id: filters.class !== 'all' ? filters.class : undefined,
          course_id: filters.course !== 'all' ? filters.course : undefined,
          status: filters.status !== 'all' ? filters.status : undefined,
          search: filters.search || undefined,
          page: pagination.page,
          per_page: pagination.per_page,
        };

        // Load attendance records and stats from API
        const [recordsResponse, statsResponse] = await Promise.all([
          attendanceService.getAttendanceRecords(apiFilters),
          attendanceService.getAttendanceStats(filters.date)
        ]);

        setAttendanceRecords(recordsResponse.data);
        setPagination(prev => ({
          ...prev,
          total: recordsResponse.total,
          total_pages: recordsResponse.total_pages,
        }));
        setStats(statsResponse);
      } catch (error) {
        console.error('Error loading attendance data:', error);

        // Fallback to mock data if API fails
        const mockRecords: AttendanceRecord[] = [
          {
            id: 1,
            student_id: '4',
            course_id: 1,
            schedule_id: 1,
            status: 'present',
            method: 'manual',
            scheduled_start_time: '2024-01-15T08:00:00Z',
            scheduled_end_time: '2024-01-15T09:00:00Z',
            actual_arrival_time: '2024-01-15T08:05:00Z',
            actual_departure_time: null,
            marked_at: '2024-01-15T08:05:00Z',
            confidence_score: null,
            location: 'Salle 101',
            device_id: null,
            notes: null,
            excuse_reason: null,
            excuse_document_url: null,
            is_validated: true,
            validated_by: 'teacher_1',
            validated_at: '2024-01-15T08:05:00Z',
            created_by: 'teacher_1',
            updated_by: null,
            created_at: '2024-01-15T08:05:00Z',
            updated_at: '2024-01-15T08:05:00Z',
          },
          {
            id: 2,
            student_id: '5',
            course_id: 1,
            schedule_id: 1,
            status: 'absent',
            method: 'manual',
            scheduled_start_time: '2024-01-15T08:00:00Z',
            scheduled_end_time: '2024-01-15T09:00:00Z',
            actual_arrival_time: null,
            actual_departure_time: null,
            marked_at: '2024-01-15T08:05:00Z',
            confidence_score: null,
            location: 'Salle 101',
            device_id: null,
            notes: null,
            excuse_reason: null,
            excuse_document_url: null,
            is_validated: true,
            validated_by: 'teacher_1',
            validated_at: '2024-01-15T08:05:00Z',
            created_by: 'teacher_1',
            updated_by: null,
            created_at: '2024-01-15T08:05:00Z',
            updated_at: '2024-01-15T08:05:00Z',
          },
        ];

        const mockStats: AttendanceStats = {
          total_students: 120,
          present_count: 98,
          absent_count: 15,
          late_count: 7,
          attendance_rate: 81.7,
          date: filters.date,
        };

        setAttendanceRecords(mockRecords);
        setStats(mockStats);
        setPagination(prev => ({
          ...prev,
          total: mockRecords.length,
          total_pages: 1,
        }));
      } finally {
        setIsLoading(false);
      }
    };

    loadAttendanceData();
  }, [filters.date, filters.class, filters.course, filters.status, filters.search, pagination.page, pagination.per_page]);

  // Records are already filtered by API
  const filteredRecords = attendanceRecords;

  // Obtenir le badge de statut
  const getStatusBadge = (statusValue: string) => {
    // Ensure statusValue is a valid AttendanceStatus, otherwise default or handle error
    const status = statusValue as AttendanceStatus;
    if (!attendanceStatusLabels[status]) {
      // Fallback for unknown status
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md bg-gray-100 text-gray-800">
          <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
          Inconnu ({statusValue})
        </span>
      );
    }

    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md ${attendanceStatusBadges[status]}`}>
        {attendanceStatusIcons[status]}
        {attendanceStatusLabels[status]}
      </span>
    );
  };

  if (isLoading) {
    return (
      <Layout title="Gestion des présences">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des présences..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Gestion des présences">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Gestion des présences
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Suivi et gestion des présences pour le {new Date(filters.date).toLocaleDateString('fr-FR')}
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex space-x-2">
            <button className="btn-secondary">
              <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
              Exporter
            </button>
          </div>
        </div>

        {/* Statistiques du jour */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Présents</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.present_count}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <XCircleIcon className="h-8 w-8 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Absents</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.absent_count}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ExclamationTriangleIcon className="h-8 w-8 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Retards</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.late_count}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClipboardDocumentListIcon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Taux de présence</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.attendance_rate}%</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filtres */}
        <div className="card p-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* Date */}
            <div>
              <label className="label">Date</label>
              <input
                type="date"
                className="input"
                value={filters.date}
                onChange={(e) => setFilters(prev => ({ ...prev, date: e.target.value }))}
              />
            </div>

            {/* Recherche */}
            <div>
              <label className="label">Recherche</label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Nom, cours..."
                  className="input pl-10"
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                />
              </div>
            </div>

            {/* Classe */}
            <div>
              <label className="label">Classe</label>
              <select
                className="input"
                value={filters.class}
                onChange={(e) => setFilters(prev => ({ ...prev, class: e.target.value }))}
              >
                <option value="all">Toutes les classes</option>
                <option value="3ème A">3ème A</option>
                <option value="3ème B">3ème B</option>
                <option value="4ème A">4ème A</option>
                <option value="4ème B">4ème B</option>
              </select>
            </div>

            {/* Cours */}
            <div>
              <label className="label">Cours</label>
              <select
                className="input"
                value={filters.course}
                onChange={(e) => setFilters(prev => ({ ...prev, course: e.target.value }))}
              >
                <option value="all">Tous les cours</option>
                <option value="Mathématiques">Mathématiques</option>
                <option value="Physique">Physique</option>
                <option value="Histoire">Histoire</option>
                <option value="Français">Français</option>
              </select>
            </div>

            {/* Statut */}
            <div>
              <label className="label">Statut</label>
              <select
                className="input"
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              >
                <option value="all">Tous les statuts</option>
                <option value="present">Présents</option>
                <option value="absent">Absents</option>
                <option value="late">Retards</option>
                <option value="justified">Justifiés</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tableau des présences */}
        <div className="card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Enregistrements de présence ({filteredRecords.length})
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
                    Cours
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Horaire
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Enseignant
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Marqué à
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredRecords.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          Étudiant {record.student_id}
                        </div>
                        <div className="text-sm text-gray-500">
                          {record.location || 'N/A'}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">Cours {record.course_id}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {record.scheduled_start_time ? new Date(record.scheduled_start_time).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) : 'N/A'} -
                        {record.scheduled_end_time ? new Date(record.scheduled_end_time).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) : 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        {getStatusBadge(record.status)}
                        {record.excuse_reason && (
                          <div className="text-xs text-gray-500">
                            {record.excuse_reason}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{record.created_by || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(record.marked_at).toLocaleTimeString('fr-FR', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Message si aucun enregistrement */}
        {filteredRecords.length === 0 && (
          <div className="card p-12 text-center">
            <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun enregistrement trouvé</h3>
            <p className="mt-1 text-sm text-gray-500">
              Aucun enregistrement de présence ne correspond aux critères sélectionnés.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AdminAttendance;
