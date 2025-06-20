import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import { courseService } from '../../services/courseService';
import { Course, Schedule, PaginatedResponse } from '../../services/api';
import {
  AcademicCapIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  CalendarDaysIcon,
  ClockIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';

// Define specific types for course status
type CourseStatus = 'active' | 'inactive';

const courseStatusLabels: Record<CourseStatus, string> = {
  active: 'Actif',
  inactive: 'Inactif',
};

const courseStatusBadges: Record<CourseStatus, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
};


// Local interfaces for filters
interface CourseFilters {
  search: string;
  subject: string; // Assuming subject name, not ID
  level: string;   // Assuming level name, not ID
  status: string;  // Can be 'all' or CourseStatus
}

const AdminCourses: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<CourseFilters>({
    search: '',
    subject: 'all',
    level: 'all',
    status: 'all',
  });
  const [selectedCourses, setSelectedCourses] = useState<string[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0,
  });

  // Load courses from API
  useEffect(() => {
    const loadCourses = async () => {
      setIsLoading(true);

      try {
        // Prepare API filters
        const apiFilters = {
          search: filters.search || undefined,
          subject: filters.subject !== 'all' ? filters.subject : undefined,
          level: filters.level !== 'all' ? filters.level : undefined,
          status: filters.status !== 'all' ? filters.status : undefined,
          page: pagination.page,
          per_page: pagination.per_page,
        };

        // Load courses from API
        const response = await courseService.getCourses(apiFilters);
        setCourses(response.data);
        setPagination(prev => ({
          ...prev,
          total: response.total,
          total_pages: response.total_pages,
        }));
      } catch (error) {
        console.error('Error loading courses:', error);

        // Fallback to mock data if API fails
        const mockCourses: Course[] = [
          {
            id: 1,
            name: 'Mathématiques Avancées',
            code: 'MATH301',
            description: 'Cours de mathématiques niveau avancé',
            subject: 'Mathématiques',
            level: '3ème',
            credits: 3,
            max_students: 30,
            status: 'active',
            academic_year: '2024-2025',
            semester: 'S1',
            created_at: '2024-01-10T08:00:00Z',
            updated_at: '2024-01-15T14:30:00Z',
          },
          {
            id: 2,
            name: 'Physique Quantique',
            code: 'PHYS401',
            description: 'Introduction à la physique quantique',
            subject: 'Physique',
            level: '4ème',
            credits: 4,
            max_students: 25,
            status: 'active',
            academic_year: '2024-2025',
            semester: 'S1',
            created_at: '2024-01-08T09:15:00Z',
            updated_at: '2024-01-15T10:45:00Z',
          },
          {
            id: 3,
            name: 'Histoire Contemporaine',
            code: 'HIST201',
            description: 'Histoire du 20ème siècle',
            subject: 'Histoire',
            level: '5ème',
            credits: 2,
            max_students: 35,
            status: 'active',
            academic_year: '2024-2025',
            semester: 'S1',
            created_at: '2024-01-05T11:20:00Z',
            updated_at: '2024-01-14T16:20:00Z',
          },
        ];

        setCourses(mockCourses);
        setPagination(prev => ({
          ...prev,
          total: mockCourses.length,
          total_pages: 1,
        }));
      } finally {
        setIsLoading(false);
      }
    };

    loadCourses();
  }, [filters, pagination.page, pagination.per_page]);

  // Courses are already filtered by API
  const filteredCourses = courses;

  // Handle course selection
  const handleSelectCourse = (courseId: string) => {
    setSelectedCourses(prev =>
      prev.includes(courseId)
        ? prev.filter(id => id !== courseId)
        : [...prev, courseId]
    );
  };

  const handleSelectAll = () => {
    if (selectedCourses.length === filteredCourses.length) {
      setSelectedCourses([]);
    } else {
      setSelectedCourses(filteredCourses.map(course => course.id.toString()));
    }
  };

  // CRUD operations
  const handleDeleteCourse = async (courseId: number) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce cours ?')) {
      try {
        await courseService.deleteCourse(courseId);
        setCourses(prev => prev.filter(course => course.id !== courseId));
        setSelectedCourses(prev => prev.filter(id => id !== courseId.toString()));
      } catch (error) {
        console.error('Error deleting course:', error);
        alert('Erreur lors de la suppression du cours');
      }
    }
  };

  const handleBulkDeleteSelectedCourses = async () => {
    if (selectedCourses.length === 0) return;
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer ${selectedCourses.length} cours ?`)) {
      try {
        // Assuming courseService.bulkDeleteCourses exists or similar
        // For now, let's simulate by deleting one by one
        // In a real scenario, a bulk delete endpoint is preferred.
        for (const courseIdStr of selectedCourses) {
          await courseService.deleteCourse(parseInt(courseIdStr, 10));
        }
        setCourses(prev => prev.filter(course => !selectedCourses.includes(course.id.toString())));
        setSelectedCourses([]);
      } catch (error) {
        console.error('Error deleting selected courses:', error);
        alert('Erreur lors de la suppression des cours sélectionnés.');
      }
    }
  };

  const handleToggleCourseStatus = async (courseId: number, currentStatus: CourseStatus) => {
    try {
      const newStatus: CourseStatus = currentStatus === 'active' ? 'inactive' : 'active';
      await courseService.updateCourse(courseId, { status: newStatus });

      // Refresh the course list
      setCourses(prev => prev.map(course =>
        course.id === courseId
          ? { ...course, status: newStatus }
          : course
      ));
    } catch (error) {
      console.error('Error toggling course status:', error);
      alert('Erreur lors de la modification du statut');
    }
  };

  // Get status badge
  const getStatusBadge = (statusValue: string) => {
    const status = statusValue as CourseStatus;
    if (!courseStatusLabels[status]) {
      return (
        <span className="px-2 py-1 text-xs font-medium rounded-md bg-gray-200 text-gray-700">
          Inconnu ({statusValue})
        </span>
      );
    }
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-md ${courseStatusBadges[status]}`}>
        {courseStatusLabels[status]}
      </span>
    );
  };

  // Get subject badge
  const getSubjectBadge = (subject: string) => {
    const badges: { [key: string]: string } = {
      'Mathématiques': 'bg-blue-100 text-blue-800',
      'Physique': 'bg-purple-100 text-purple-800',
      'Histoire': 'bg-yellow-100 text-yellow-800',
      'Français': 'bg-green-100 text-green-800',
      'Anglais': 'bg-red-100 text-red-800',
    };

    const badgeClass = badges[subject] || 'bg-gray-100 text-gray-800';

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-md ${badgeClass}`}>
        {subject}
      </span>
    );
  };

  if (isLoading) {
    return (
      <Layout title="Gestion des cours">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des cours..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Gestion des cours">
      <div className="space-y-6">
        {/* En-tête avec actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Gestion des cours
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              {filteredCourses.length} cours trouvé{filteredCourses.length > 1 ? 's' : ''}
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex space-x-2">
            {selectedCourses.length > 0 && (
              <div className="flex space-x-2 mr-4">
                <button
                  onClick={handleBulkDeleteSelectedCourses}
                  className="bg-red-600 text-white px-3 py-2 rounded-md text-sm hover:bg-red-700"
                >
                  Supprimer ({selectedCourses.length})
                </button>
              </div>
            )}
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Nouveau cours
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
                  placeholder="Rechercher par nom ou code..."
                  className="input pl-10"
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                />
              </div>
            </div>

            {/* Filtre par matière */}
            <div>
              <select
                className="input"
                value={filters.subject}
                onChange={(e) => setFilters(prev => ({ ...prev, subject: e.target.value }))}
              >
                <option value="all">Toutes les matières</option>
                <option value="Mathématiques">Mathématiques</option>
                <option value="Physique">Physique</option>
                <option value="Histoire">Histoire</option>
                <option value="Français">Français</option>
                <option value="Anglais">Anglais</option>
              </select>
            </div>

            {/* Filtre par niveau */}
            <div>
              <select
                className="input"
                value={filters.level}
                onChange={(e) => setFilters(prev => ({ ...prev, level: e.target.value }))}
              >
                <option value="all">Tous les niveaux</option>
                <option value="6ème">6ème</option>
                <option value="5ème">5ème</option>
                <option value="4ème">4ème</option>
                <option value="3ème">3ème</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tableau des cours */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedCourses.length === filteredCourses.length && filteredCourses.length > 0}
                      onChange={handleSelectAll}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cours
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Matière
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Niveau
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Étudiants
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
                {filteredCourses.map((course) => (
                  <tr key={course.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedCourses.includes(course.id.toString())}
                        onChange={() => handleSelectCourse(course.id.toString())}
                        className="h-4 w-4 text-blue-600 rounded border-gray-300"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <AcademicCapIcon className="h-6 w-6 text-blue-600" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {course.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {course.code}
                          </div>
                          {course.description && (
                            <div className="text-xs text-gray-400 mt-1">
                              {course.description}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getSubjectBadge(course.subject)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {course.level}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <UserGroupIcon className="h-4 w-4 mr-1" />
                        0/{course.max_students}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(course.status)}
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
                          onClick={() => handleToggleCourseStatus(course.id, course.status)}
                          className={course.status === 'active' ? "text-orange-600 hover:text-orange-700" : "text-green-600 hover:text-green-700"}
                          title={course.status === 'active' ? "Désactiver" : "Activer"}
                        >
                          {course.status === 'active' ? "🔒" : "🔓"}
                        </button>
                        <button
                          onClick={() => handleDeleteCourse(course.id)}
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

        {/* Message si aucun cours */}
        {filteredCourses.length === 0 && (
          <div className="card p-12 text-center">
            <AcademicCapIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun cours trouvé</h3>
            <p className="mt-1 text-sm text-gray-500">
              Aucun cours ne correspond aux critères de recherche.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AdminCourses;
