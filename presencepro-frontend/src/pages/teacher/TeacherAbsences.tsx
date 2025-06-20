import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  ExclamationTriangleIcon,
  CalendarDaysIcon,
  ClockIcon,
  UserIcon,
  AcademicCapIcon,
  EnvelopeIcon,
  PhoneIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

// Types pour les absences
interface AbsentStudent {
  id: string;
  firstName: string;
  lastName: string;
  studentNumber: string;
  className: string;
  courseName: string;
  startTime: string;
  endTime: string;
  room: string;
  absentSince: string;
  hasJustification: boolean;
  justificationStatus?: 'pending' | 'approved' | 'rejected';
  parentName: string;
  parentEmail: string;
  parentPhone?: string;
  photo?: string;
}

interface AbsenceStats {
  totalAbsences: number;
  unjustifiedAbsences: number;
  justifiedAbsences: number;
  pendingJustifications: number;
}

const TeacherAbsences: React.FC = () => {
  const [absentStudents, setAbsentStudents] = useState<AbsentStudent[]>([]);
  const [stats, setStats] = useState<AbsenceStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [filterClass, setFilterClass] = useState('all');

  // Simuler le chargement des données
  useEffect(() => {
    const loadAbsences = async () => {
      setIsLoading(true);

      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Données simulées
      const mockAbsentStudents: AbsentStudent[] = [
        {
          id: '1',
          firstName: 'Lucas',
          lastName: 'Moreau',
          studentNumber: '2024001',
          className: '3ème A',
          courseName: 'Mathématiques',
          startTime: '08:00',
          endTime: '09:00',
          room: 'Salle 101',
          absentSince: '08:05',
          hasJustification: true,
          justificationStatus: 'pending',
          parentName: 'Pierre Moreau',
          parentEmail: 'pierre.moreau@email.com',
          parentPhone: '+33 6 12 34 56 78',
        },
        {
          id: '2',
          firstName: 'Emma',
          lastName: 'Leroy',
          studentNumber: '2024002',
          className: '3ème A',
          courseName: 'Mathématiques',
          startTime: '08:00',
          endTime: '09:00',
          room: 'Salle 101',
          absentSince: '08:00',
          hasJustification: false,
          parentName: 'Marie Leroy',
          parentEmail: 'marie.leroy@email.com',
        },
        {
          id: '3',
          firstName: 'Thomas',
          lastName: 'Dubois',
          studentNumber: '2024003',
          className: '3ème B',
          courseName: 'Mathématiques',
          startTime: '10:00',
          endTime: '11:00',
          room: 'Salle 102',
          absentSince: '10:15',
          hasJustification: false,
          parentName: 'Claire Dubois',
          parentEmail: 'claire.dubois@email.com',
          parentPhone: '+33 6 23 45 67 89',
        },
        {
          id: '4',
          firstName: 'Marie',
          lastName: 'Petit',
          studentNumber: '2024004',
          className: '4ème A',
          courseName: 'Algèbre',
          startTime: '14:00',
          endTime: '15:00',
          room: 'Salle 103',
          absentSince: '14:00',
          hasJustification: true,
          justificationStatus: 'approved',
          parentName: 'Jean Petit',
          parentEmail: 'jean.petit@email.com',
        },
      ];

      const mockStats: AbsenceStats = {
        totalAbsences: mockAbsentStudents.length,
        unjustifiedAbsences: mockAbsentStudents.filter(s => !s.hasJustification).length,
        justifiedAbsences: mockAbsentStudents.filter(s => s.hasJustification && s.justificationStatus === 'approved').length,
        pendingJustifications: mockAbsentStudents.filter(s => s.hasJustification && s.justificationStatus === 'pending').length,
      };

      setAbsentStudents(mockAbsentStudents);
      setStats(mockStats);
      setIsLoading(false);
    };

    loadAbsences();
  }, [selectedDate]);

  // Filtrer les étudiants absents
  const filteredStudents = absentStudents.filter(student => {
    if (filterClass === 'all') return true;
    return student.className === filterClass;
  });

  // Contacter un parent
  const contactParent = (student: AbsentStudent, method: 'email' | 'phone') => {
    if (method === 'email') {
      window.open(`mailto:${student.parentEmail}?subject=Absence de ${student.firstName} ${student.lastName}&body=Bonjour ${student.parentName},%0D%0A%0D%0AVotre enfant ${student.firstName} est absent au cours de ${student.courseName} aujourd'hui.%0D%0A%0D%0ACordialement`);
    } else if (method === 'phone' && student.parentPhone) {
      window.open(`tel:${student.parentPhone}`);
    }
  };

  // Obtenir le badge de justification
  const getJustificationBadge = (student: AbsentStudent) => {
    if (!student.hasJustification) {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md bg-red-100 text-red-800">
          <ExclamationTriangleIcon className="h-3 w-3 mr-1" />
          Non justifiée
        </span>
      );
    }

    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    };

    const labels = {
      pending: 'En attente',
      approved: 'Justifiée',
      rejected: 'Rejetée',
    };

    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md ${badges[student.justificationStatus as keyof typeof badges]}`}>
        <DocumentTextIcon className="h-3 w-3 mr-1" />
        {labels[student.justificationStatus as keyof typeof labels]}
      </span>
    );
  };

  if (isLoading) {
    return (
      <Layout title="Absences du jour">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des absences..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Absences du jour">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Absences du jour
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Suivi des étudiants absents pour le {new Date(selectedDate).toLocaleDateString('fr-FR')}
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex space-x-2">
            <input
              type="date"
              className="input"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
            <select
              className="input"
              value={filterClass}
              onChange={(e) => setFilterClass(e.target.value)}
            >
              <option value="all">Toutes les classes</option>
              <option value="3ème A">3ème A</option>
              <option value="3ème B">3ème B</option>
              <option value="4ème A">4ème A</option>
              <option value="4ème B">4ème B</option>
            </select>
          </div>
        </div>

        {/* Statistiques */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total absences</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalAbsences}</p>
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

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentTextIcon className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Justifiées</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.justifiedAbsences}</p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClockIcon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">En attente</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.pendingJustifications}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Liste des étudiants absents */}
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Étudiants absents ({filteredStudents.length})
            </h3>
          </div>

          {filteredStudents.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {filteredStudents.map((student) => (
                <div key={student.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {/* Photo de l'étudiant */}
                      <div className="flex-shrink-0 h-12 w-12">
                        {student.photo ? (
                          <img
                            className="h-12 w-12 rounded-full object-cover"
                            src={student.photo}
                            alt={`${student.firstName} ${student.lastName}`}
                          />
                        ) : (
                          <div className="h-12 w-12 rounded-full bg-gray-300 flex items-center justify-center">
                            <UserIcon className="h-6 w-6 text-gray-600" />
                          </div>
                        )}
                      </div>

                      {/* Informations de l'étudiant */}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="text-lg font-medium text-gray-900">
                            {student.firstName} {student.lastName}
                          </h4>
                          {getJustificationBadge(student)}
                        </div>
                        <div className="mt-1 space-y-1">
                          <div className="flex items-center text-sm text-gray-500">
                            <AcademicCapIcon className="h-4 w-4 mr-1" />
                            {student.className} • N° {student.studentNumber}
                          </div>
                          <div className="flex items-center text-sm text-gray-500">
                            <CalendarDaysIcon className="h-4 w-4 mr-1" />
                            {student.courseName} • {student.startTime} - {student.endTime} • {student.room}
                          </div>
                          <div className="flex items-center text-sm text-red-600">
                            <ClockIcon className="h-4 w-4 mr-1" />
                            Absent depuis {student.absentSince}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-2">
                      <div className="text-right mr-4">
                        <div className="text-sm font-medium text-gray-900">{student.parentName}</div>
                        <div className="text-sm text-gray-500">{student.parentEmail}</div>
                        {student.parentPhone && (
                          <div className="text-sm text-gray-500">{student.parentPhone}</div>
                        )}
                      </div>

                      <div className="flex flex-col space-y-1">
                        <button
                          onClick={() => contactParent(student, 'email')}
                          className="flex items-center px-3 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100"
                        >
                          <EnvelopeIcon className="h-3 w-3 mr-1" />
                          Email
                        </button>
                        {student.parentPhone && (
                          <button
                            onClick={() => contactParent(student, 'phone')}
                            className="flex items-center px-3 py-1 text-xs font-medium text-green-600 bg-green-50 rounded hover:bg-green-100"
                          >
                            <PhoneIcon className="h-3 w-3 mr-1" />
                            Appeler
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune absence</h3>
              <p className="mt-1 text-sm text-gray-500">
                Tous les étudiants sont présents aujourd'hui !
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default TeacherAbsences;
