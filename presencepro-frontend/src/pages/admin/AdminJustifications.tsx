import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import { justificationService } from '../../services/justificationService';
import { useAuth } from '../../contexts/AuthContext';
import { Justification, JustificationStats, PaginatedResponse } from '../../services/api';
import {
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  EyeIcon,
  DocumentArrowDownIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';

// Local interfaces for filters
interface LocalJustificationFilters {
  status: string;
  class: string;
  dateFrom: string;
  dateTo: string;
  search: string;
}

const AdminJustifications: React.FC = () => {
  const { user } = useAuth();
  const [justifications, setJustifications] = useState<Justification[]>([]);
  const [stats, setStats] = useState<JustificationStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<LocalJustificationFilters>({
    status: 'all',
    class: 'all',
    dateFrom: '',
    dateTo: '',
    search: '',
  });
  const [selectedJustification, setSelectedJustification] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0,
  });

  // Load justifications from API
  useEffect(() => {
    const loadJustifications = async () => {
      setIsLoading(true);

      try {
        // Prepare API filters
        const apiFilters = {
          status: filters.status !== 'all' ? filters.status : undefined,
          date_from: filters.dateFrom || undefined,
          date_to: filters.dateTo || undefined,
          search: filters.search || undefined,
          page: pagination.page,
          per_page: pagination.per_page,
        };

        // Load justifications and stats from API
        const [justificationsResponse, statsResponse] = await Promise.all([
          justificationService.getJustifications(apiFilters),
          justificationService.getJustificationStats()
        ]);

        setJustifications(justificationsResponse.data);
        setPagination(prev => ({
          ...prev,
          total: justificationsResponse.total,
          total_pages: justificationsResponse.total_pages,
        }));
        setStats(statsResponse);
      } catch (error) {
        console.error('Error loading justifications:', error);

        // Fallback to mock data if API fails
        const mockJustifications: Justification[] = [
          {
            id: 1,
            student_id: '4',
            attendance_record_id: 1,
            reason: 'Rendez-vous médical',
            description: 'Consultation chez le dentiste pour un traitement urgent. Certificat médical en pièce jointe.',
            document_url: 'certificat_medical_lucas.pdf',
            status: 'pending',
            submitted_at: '2024-01-15T09:30:00Z',
            reviewed_at: null,
            reviewed_by: null,
            admin_comments: null,
            created_at: '2024-01-15T09:30:00Z',
            updated_at: '2024-01-15T09:30:00Z',
          },
          {
            id: 2,
            student_id: '5',
            attendance_record_id: 2,
            reason: 'Maladie',
            description: 'Grippe avec fièvre. Emma était trop malade pour venir en cours.',
            document_url: null,
            status: 'approved',
            submitted_at: '2024-01-14T18:45:00Z',
            reviewed_at: '2024-01-15T08:00:00Z',
            reviewed_by: 'admin_1',
            admin_comments: 'Justification acceptée. Bon rétablissement.',
            created_at: '2024-01-14T18:45:00Z',
            updated_at: '2024-01-15T08:00:00Z',
          },
        ];

        const mockStats: JustificationStats = {
          total_justifications: mockJustifications.length,
          pending_count: mockJustifications.filter(j => j.status === 'pending').length,
          approved_count: mockJustifications.filter(j => j.status === 'approved').length,
          rejected_count: mockJustifications.filter(j => j.status === 'rejected').length,
          average_response_time_hours: 24,
        };

        setJustifications(mockJustifications);
        setStats(mockStats);
        setPagination(prev => ({
          ...prev,
          total: mockJustifications.length,
          total_pages: 1,
        }));
      } finally {
        setIsLoading(false);
      }
    };

    loadJustifications();
  }, [filters, pagination.page, pagination.per_page]);

  // Justifications are already filtered by API
  const filteredJustifications = justifications;

  // Obtenir le badge de statut
  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      under_review: 'bg-blue-100 text-blue-800',
    };

    const labels = {
      pending: 'En attente',
      approved: 'Approuvée',
      rejected: 'Rejetée',
      under_review: 'En cours d\'examen',
    };

    const icons = {
      pending: <ClockIcon className="h-4 w-4 mr-1" />,
      approved: <CheckCircleIcon className="h-4 w-4 mr-1" />,
      rejected: <XCircleIcon className="h-4 w-4 mr-1" />,
      under_review: <EyeIcon className="h-4 w-4 mr-1" />,
    };

    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md ${badges[status as keyof typeof badges]}`}>
        {icons[status as keyof typeof icons]}
        {labels[status as keyof typeof labels]}
      </span>
    );
  };

  // Gérer l'approbation/rejet
  const handleStatusChange = async (justificationId: number, newStatus: 'approved' | 'rejected', comments?: string) => {
    if (!user) return;

    try {
      await justificationService.updateJustificationStatus(justificationId, {
        status: newStatus,
        admin_comments: comments || '',
        reviewed_by: user.id,
      });

      // Update local state
      setJustifications(prev => prev.map(j =>
        j.id === justificationId
          ? {
              ...j,
              status: newStatus,
              reviewed_by: user.id,
              reviewed_at: new Date().toISOString(),
              admin_comments: comments || '',
            }
          : j
      ));
    } catch (error) {
      console.error('Error updating justification status:', error);
      alert('Erreur lors de la mise à jour du statut');
    }
  };

  if (isLoading) {
    return (
      <Layout title="Gestion des justifications">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des justifications..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Gestion des justifications">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Gestion des justifications
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Traitement et validation des demandes de justification d'absence
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <button className="btn-secondary">
              <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
              Exporter
            </button>
          </div>
        </div>

        {/* Statistiques */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentTextIcon className="h-8 w-8 text-gray-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_justifications}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClockIcon className="h-8 w-8 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">En attente</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.pending_count}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Approuvées</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.approved_count}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <XCircleIcon className="h-8 w-8 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Rejetées</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.rejected_count}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <EyeIcon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Temps de réponse moyen</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.average_response_time_hours}h</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filtres */}
        <div className="card p-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* Recherche */}
            <div>
              <label className="label">Recherche</label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Nom, raison..."
                  className="input pl-10"
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                />
              </div>
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
                <option value="pending">En attente</option>
                <option value="under_review">En examen</option>
                <option value="approved">Approuvées</option>
                <option value="rejected">Rejetées</option>
              </select>
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

            {/* Date de début */}
            <div>
              <label className="label">Date de début</label>
              <input
                type="date"
                className="input"
                value={filters.dateFrom}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
              />
            </div>

            {/* Date de fin */}
            <div>
              <label className="label">Date de fin</label>
              <input
                type="date"
                className="input"
                value={filters.dateTo}
                onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
              />
            </div>
          </div>
        </div>

        {/* Tableau des justifications */}
        <div className="card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Demandes de justification ({filteredJustifications.length})
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
                    Parent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Absence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Raison
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
                {filteredJustifications.map((justification) => (
                  <tr key={justification.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          Étudiant {justification.student_id}
                        </div>
                        <div className="text-sm text-gray-500">
                          Classe inconnue
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm text-gray-900">Parent inconnu</div>
                        <div className="text-sm text-gray-500">email@example.com</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm text-gray-900">
                          {new Date(justification.created_at).toLocaleDateString('fr-FR')}
                        </div>
                        <div className="text-sm text-gray-500">Cours {justification.attendance_record_id}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{justification.reason}</div>
                      {justification.document_url && (
                        <div className="text-xs text-blue-600 mt-1">
                          📎 1 pièce jointe
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(justification.status)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex space-x-2">
                        <button
                          className="text-blue-600 hover:text-blue-700"
                          onClick={() => setSelectedJustification(justification.id.toString())}
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        {justification.status === 'pending' && (
                          <>
                            <button
                              className="text-green-600 hover:text-green-700"
                              onClick={() => handleStatusChange(justification.id, 'approved', 'Justification acceptée')}
                            >
                              <CheckCircleIcon className="h-4 w-4" />
                            </button>
                            <button
                              className="text-red-600 hover:text-red-700"
                              onClick={() => handleStatusChange(justification.id, 'rejected', 'Justification non valide')}
                            >
                              <XCircleIcon className="h-4 w-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Message si aucune justification */}
        {filteredJustifications.length === 0 && (
          <div className="card p-12 text-center">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune justification trouvée</h3>
            <p className="mt-1 text-sm text-gray-500">
              Aucune demande de justification ne correspond aux critères sélectionnés.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AdminJustifications;
