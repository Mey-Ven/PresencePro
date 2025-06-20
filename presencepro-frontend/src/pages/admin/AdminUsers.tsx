import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import { userService } from '../../services/userService';
import { User, Student, Teacher, Parent, PaginatedResponse } from '../../services/api';
import {
  UserIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';

// Use interfaces from API service
interface LocalUserFilters {
  role: string;
  status: string;
  search: string;
}

const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<LocalUserFilters>({
    role: 'all',
    status: 'all',
    search: '',
  });
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0,
  });

  // Load users from API
  useEffect(() => {
    const loadUsers = async () => {
      setIsLoading(true);

      try {
        // Prepare API filters
        const apiFilters = {
          role: filters.role !== 'all' ? filters.role : undefined,
          is_active: filters.status === 'active' ? true : filters.status === 'inactive' ? false : undefined,
          search: filters.search || undefined,
          page: pagination.page,
          per_page: pagination.per_page,
        };

        // Load users from API
        const response = await userService.getUsers(apiFilters);
        setUsers(response.data);
        setPagination(prev => ({
          ...prev,
          total: response.total,
          total_pages: response.total_pages,
        }));
      } catch (error) {
        console.error('Error loading users:', error);

        // Fallback to mock data if API fails
        const mockUsers: User[] = [
          {
            id: '1',
            first_name: 'Marie',
            last_name: 'Dupont',
            email: 'marie.dupont@presencepro.fr',
            role: 'admin',
            is_active: true,
            created_at: '2024-01-10T08:00:00Z',
            updated_at: '2024-01-15T14:30:00Z',
          },
          {
            id: '2',
            first_name: 'Jean',
            last_name: 'Martin',
            email: 'jean.martin@presencepro.fr',
            role: 'teacher',
            is_active: true,
            created_at: '2024-01-08T09:15:00Z',
            updated_at: '2024-01-15T10:45:00Z',
          },
          {
            id: '3',
            first_name: 'Sophie',
            last_name: 'Bernard',
            email: 'sophie.bernard@presencepro.fr',
            role: 'teacher',
            is_active: true,
            created_at: '2024-01-05T11:20:00Z',
            updated_at: '2024-01-14T16:20:00Z',
          },
          {
            id: '4',
            first_name: 'Lucas',
            last_name: 'Moreau',
            email: 'lucas.moreau@student.presencepro.fr',
            role: 'student',
            is_active: true,
            created_at: '2024-01-12T13:45:00Z',
            updated_at: '2024-01-15T08:15:00Z',
          },
          {
            id: '5',
            first_name: 'Emma',
            last_name: 'Leroy',
            email: 'emma.leroy@student.presencepro.fr',
            role: 'student',
            is_active: true,
            created_at: '2024-01-11T10:30:00Z',
            updated_at: '2024-01-14T15:45:00Z',
          },
          {
            id: '6',
            first_name: 'Pierre',
            last_name: 'Moreau',
            email: 'pierre.moreau@parent.presencepro.fr',
            role: 'parent',
            is_active: true,
            created_at: '2024-01-12T14:00:00Z',
            updated_at: '2024-01-15T07:30:00Z',
          },
          {
            id: '7',
            first_name: 'Claire',
            last_name: 'Dubois',
            email: 'claire.dubois@presencepro.fr',
            role: 'teacher',
            is_active: false,
            created_at: '2024-01-03T16:15:00Z',
            updated_at: '2024-01-10T12:00:00Z',
          },
        ];

        setUsers(mockUsers);
        setPagination(prev => ({
          ...prev,
          total: mockUsers.length,
          total_pages: 1,
        }));
      } finally {
        setIsLoading(false);
      }
    };

    loadUsers();
  }, [filters, pagination.page, pagination.per_page]);

  // Users are already filtered by API, so we can use them directly
  const filteredUsers = users;

  // Gérer la sélection des utilisateurs
  const handleSelectUser = (userId: string) => {
    setSelectedUsers(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSelectAll = () => {
    if (selectedUsers.length === filteredUsers.length) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(filteredUsers.map(user => user.id));
    }
  };

  // CRUD operations
  const handleDeleteUser = async (userId: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
      try {
        await userService.deleteUser(userId);
        setUsers(prev => prev.filter(user => user.id !== userId));
        setSelectedUsers(prev => prev.filter(id => id !== userId));
      } catch (error) {
        console.error('Error deleting user:', error);
        alert('Erreur lors de la suppression de l\'utilisateur');
      }
    }
  };

  const handleToggleUserStatus = async (userId: string, currentStatus: boolean) => {
    try {
      if (currentStatus) {
        await userService.deactivateUser(userId);
      } else {
        await userService.activateUser(userId);
      }

      // Refresh the user list
      setUsers(prev => prev.map(user =>
        user.id === userId
          ? { ...user, is_active: !currentStatus }
          : user
      ));
    } catch (error) {
      console.error('Error toggling user status:', error);
      alert('Erreur lors de la modification du statut');
    }
  };

  const handleBulkAction = async (action: 'activate' | 'deactivate' | 'delete') => {
    if (selectedUsers.length === 0) return;

    const confirmMessage = action === 'delete'
      ? `Êtes-vous sûr de vouloir supprimer ${selectedUsers.length} utilisateur(s) ?`
      : `Êtes-vous sûr de vouloir ${action === 'activate' ? 'activer' : 'désactiver'} ${selectedUsers.length} utilisateur(s) ?`;

    if (window.confirm(confirmMessage)) {
      try {
        if (action === 'delete') {
          await userService.bulkDeleteUsers(selectedUsers);
          setUsers(prev => prev.filter(user => !selectedUsers.includes(user.id)));
        } else {
          // For activate/deactivate, we need to call individual endpoints
          const promises = selectedUsers.map(userId =>
            action === 'activate'
              ? userService.activateUser(userId)
              : userService.deactivateUser(userId)
          );
          await Promise.all(promises);

          setUsers(prev => prev.map(user =>
            selectedUsers.includes(user.id)
              ? { ...user, is_active: action === 'activate' }
              : user
          ));
        }

        setSelectedUsers([]);
      } catch (error) {
        console.error(`Error performing bulk ${action}:`, error);
        alert(`Erreur lors de l'opération en lot`);
      }
    }
  };

  // Obtenir le badge de statut
  const getStatusBadge = (isActive: boolean) => {
    const badge = isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
    const label = isActive ? 'Actif' : 'Inactif';

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-md ${badge}`}>
        {label}
      </span>
    );
  };

  // Obtenir le badge de rôle
  const getRoleBadge = (role: string) => {
    const badges = {
      admin: 'bg-purple-100 text-purple-800',
      teacher: 'bg-blue-100 text-blue-800',
      student: 'bg-yellow-100 text-yellow-800',
      parent: 'bg-green-100 text-green-800',
    };

    const labels = {
      admin: 'Administrateur',
      teacher: 'Enseignant',
      student: 'Étudiant',
      parent: 'Parent',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-md ${badges[role as keyof typeof badges]}`}>
        {labels[role as keyof typeof labels]}
      </span>
    );
  };

  if (isLoading) {
    return (
      <Layout title="Gestion des utilisateurs">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des utilisateurs..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Gestion des utilisateurs">
      <div className="space-y-6">
        {/* En-tête avec actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Gestion des utilisateurs
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              {filteredUsers.length} utilisateur{filteredUsers.length > 1 ? 's' : ''} trouvé{filteredUsers.length > 1 ? 's' : ''}
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Nouvel utilisateur
            </button>
          </div>
        </div>

        {/* Filtres et recherche */}
        <div className="card p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Recherche */}
            <div className="md:col-span-2">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher par nom ou email..."
                  className="input pl-10"
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                />
              </div>
            </div>

            {/* Filtre par rôle */}
            <div>
              <select
                className="input"
                value={filters.role}
                onChange={(e) => setFilters(prev => ({ ...prev, role: e.target.value }))}
              >
                <option value="all">Tous les rôles</option>
                <option value="admin">Administrateurs</option>
                <option value="teacher">Enseignants</option>
                <option value="student">Étudiants</option>
                <option value="parent">Parents</option>
              </select>
            </div>

            {/* Filtre par statut */}
            <div>
              <select
                className="input"
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              >
                <option value="all">Tous les statuts</option>
                <option value="active">Actifs</option>
                <option value="inactive">Inactifs</option>
              </select>
            </div>
          </div>
        </div>

        {/* Actions en lot */}
        {selectedUsers.length > 0 && (
          <div className="card p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">
                {selectedUsers.length} utilisateur{selectedUsers.length > 1 ? 's' : ''} sélectionné{selectedUsers.length > 1 ? 's' : ''}
              </span>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleBulkAction('activate')}
                  className="btn-secondary text-sm"
                >
                  Activer
                </button>
                <button
                  onClick={() => handleBulkAction('deactivate')}
                  className="btn-secondary text-sm"
                >
                  Désactiver
                </button>
                <button
                  onClick={() => handleBulkAction('delete')}
                  className="btn-secondary text-sm text-red-600"
                >
                  Supprimer
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Tableau des utilisateurs */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedUsers.length === filteredUsers.length && filteredUsers.length > 0}
                      onChange={handleSelectAll}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Utilisateur
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rôle
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dernière connexion
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.id)}
                        onChange={() => handleSelectUser(user.id)}
                        className="h-4 w-4 text-blue-600 rounded border-gray-300"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                            <UserIcon className="h-6 w-6 text-gray-600" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {user.first_name} {user.last_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {user.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        {getRoleBadge(user.role)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(user.is_active)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div>
                        <div>{new Date(user.updated_at).toLocaleDateString('fr-FR')}</div>
                        <div className="text-xs text-gray-400">
                          {new Date(user.updated_at).toLocaleTimeString('fr-FR', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex space-x-2">
                        <button
                          className="text-blue-600 hover:text-blue-700"
                          title="Voir les détails"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button
                          className="text-gray-600 hover:text-gray-700"
                          title="Modifier"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                          className={user.is_active ? "text-orange-600 hover:text-orange-700" : "text-green-600 hover:text-green-700"}
                          title={user.is_active ? "Désactiver" : "Activer"}
                        >
                          {user.is_active ? "🔒" : "🔓"}
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-600 hover:text-red-700"
                          title="Supprimer"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Message si aucun utilisateur */}
        {filteredUsers.length === 0 && (
          <div className="card p-12 text-center">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun utilisateur trouvé</h3>
            <p className="mt-1 text-sm text-gray-500">
              Aucun utilisateur ne correspond aux critères de recherche.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AdminUsers;
