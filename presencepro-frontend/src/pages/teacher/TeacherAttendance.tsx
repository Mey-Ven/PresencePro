import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import { attendanceService } from '../../services/attendanceService';
import { courseService } from '../../services/courseService';
import { userService } from '../../services/userService';
import { useAuth } from '../../contexts/AuthContext';
import { AttendanceRecord, Schedule, Student } from '../../services/api';
import {
  ClipboardDocumentListIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  CalendarDaysIcon,
  ClockIcon,
  UserIcon,
  AcademicCapIcon,
} from '@heroicons/react/24/outline';

// Local interfaces for teacher attendance
interface LocalStudent extends Student {
  status: 'present' | 'absent' | 'late' | 'justified' | 'not_marked';
  notes?: string;
}

interface ClassSession {
  id: string;
  schedule_id: number;
  course_id: number;
  courseName: string;
  className: string;
  date: string;
  startTime: string;
  endTime: string;
  room: string;
  students: LocalStudent[];
  isCompleted: boolean;
  attendanceMarkedAt?: string;
}

interface LocalAttendanceStats {
  totalStudents: number;
  present: number;
  absent: number;
  late: number;
  notMarked: number;
}

const TeacherAttendance: React.FC = () => {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<ClassSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Load teacher's sessions from API
  useEffect(() => {
    const loadSessions = async () => {
      if (!user) return;

      setIsLoading(true);

      try {
        // Get today's date
        const today = new Date().toISOString().split('T')[0];

        // Load teacher's schedules for today
        const schedules = await courseService.getTeacherSchedules(user.id, today);

        // Convert schedules to sessions with students
        const sessionsPromises = schedules.map(async (schedule) => {
          try {
            // Get students enrolled in this course
            const enrolledStudents = await courseService.getCourseStudents(schedule.course_id);

            // Get existing attendance records for this session
            const existingAttendance = await attendanceService.getAttendanceBySchedule(schedule.id);

            // Map students with their attendance status
            const studentsWithStatus: LocalStudent[] = enrolledStudents.map(student => {
              const attendanceRecord = existingAttendance.find(record => record.student_id === student.id);
              return {
                ...student,
                status: attendanceRecord ? attendanceRecord.status as any : 'not_marked',
                notes: attendanceRecord?.notes || undefined,
              };
            });

            const session: ClassSession = {
              id: schedule.id.toString(),
              schedule_id: schedule.id,
              course_id: schedule.course_id,
              courseName: schedule.course_name || `Cours ${schedule.course_id}`,
              className: schedule.class_name || 'Classe inconnue',
              date: schedule.date,
              startTime: new Date(schedule.start_time).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
              endTime: new Date(schedule.end_time).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
              room: schedule.room || 'Salle non définie',
              students: studentsWithStatus,
              isCompleted: existingAttendance.length > 0 && existingAttendance.every(record => record.status !== 'not_marked'),
              attendanceMarkedAt: existingAttendance.length > 0 ? existingAttendance[0].marked_at : undefined,
            };

            return session;
          } catch (error) {
            console.error(`Error loading session data for schedule ${schedule.id}:`, error);
            return null;
          }
        });

        const loadedSessions = (await Promise.all(sessionsPromises)).filter(Boolean) as ClassSession[];
        setSessions(loadedSessions);

        if (loadedSessions.length > 0) {
          setSelectedSession(loadedSessions[0].id);
        }
      } catch (error) {
        console.error('Error loading teacher sessions:', error);

        // Fallback to mock data if API fails
        const mockSessions: ClassSession[] = [
          {
            id: '1',
            schedule_id: 1,
            course_id: 1,
            courseName: 'Mathématiques',
            className: '3ème A',
            date: '2024-01-15',
            startTime: '08:00',
            endTime: '09:00',
            room: 'Salle 101',
            isCompleted: false,
            students: [
              {
                id: '1',
                first_name: 'Lucas',
                last_name: 'Moreau',
                email: 'lucas.moreau@student.presencepro.fr',
                role: 'student',
                is_active: true,
                created_at: '2024-01-10T08:00:00Z',
                updated_at: '2024-01-15T14:30:00Z',
                status: 'not_marked',
              },
              {
                id: '2',
                first_name: 'Emma',
                last_name: 'Leroy',
                email: 'emma.leroy@student.presencepro.fr',
                role: 'student',
                is_active: true,
                created_at: '2024-01-10T08:00:00Z',
                updated_at: '2024-01-15T14:30:00Z',
                status: 'not_marked',
              },
            ],
          },
        ];

        setSessions(mockSessions);
        if (mockSessions.length > 0) {
          setSelectedSession(mockSessions[0].id);
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadSessions();
  }, [user]);

  // Obtenir la session sélectionnée
  const currentSession = sessions.find(s => s.id === selectedSession);

  // Calculer les statistiques de présence
  const getAttendanceStats = (students: LocalStudent[]): LocalAttendanceStats => {
    return {
      totalStudents: students.length,
      present: students.filter(s => s.status === 'present').length,
      absent: students.filter(s => s.status === 'absent').length,
      late: students.filter(s => s.status === 'late').length,
      notMarked: students.filter(s => s.status === 'not_marked').length,
    };
  };

  // Marquer la présence d'un étudiant
  const markAttendance = (studentId: string, status: 'present' | 'absent' | 'late' | 'justified') => {
    setSessions(prev => prev.map(session =>
      session.id === selectedSession
        ? {
            ...session,
            students: session.students.map(student =>
              student.id === studentId ? { ...student, status } : student
            )
          }
        : session
    ));
  };

  // Sauvegarder la présence
  const saveAttendance = async () => {
    if (!currentSession || !user) return;

    setIsSaving(true);

    try {
      // Create attendance records for all students
      const attendancePromises = currentSession.students.map(student => {
        if (student.status === 'not_marked') return null;

        return attendanceService.markAttendance({
          student_id: student.id,
          course_id: currentSession.course_id,
          schedule_id: currentSession.schedule_id,
          status: student.status,
          method: 'manual',
          scheduled_start_time: `${currentSession.date}T${currentSession.startTime}:00Z`,
          scheduled_end_time: `${currentSession.date}T${currentSession.endTime}:00Z`,
          location: currentSession.room,
          notes: student.notes,
          created_by: user.id,
        });
      });

      await Promise.all(attendancePromises.filter(Boolean));

      // Update local state
      setSessions(prev => prev.map(session =>
        session.id === selectedSession
          ? {
              ...session,
              isCompleted: true,
              attendanceMarkedAt: new Date().toISOString(),
            }
          : session
      ));
    } catch (error) {
      console.error('Error saving attendance:', error);
      alert('Erreur lors de la sauvegarde de la présence');
    } finally {
      setIsSaving(false);
    }
  };

  // Filtrer les étudiants selon la recherche
  const filteredStudents = currentSession?.students.filter(student =>
    student.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    student.last_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    student.email.includes(searchQuery)
  ) || [];

  // Obtenir l'icône de statut
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'present':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'absent':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'late':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'justified':
        return <ClipboardDocumentListIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  if (isLoading) {
    return (
      <Layout title="Prise de présence">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des sessions..." />
          </div>
        </div>
      </Layout>
    );
  }

  const stats = currentSession ? getAttendanceStats(currentSession.students) : null;

  return (
    <Layout title="Prise de présence">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Prise de présence
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Marquez la présence de vos étudiants pour chaque session
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Liste des sessions */}
          <div className="lg:col-span-1">
            <div className="card">
              <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="text-sm font-medium text-gray-900">Sessions du jour</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    onClick={() => setSelectedSession(session.id)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 ${
                      selectedSession === session.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {session.courseName}
                        </p>
                        <p className="text-sm text-gray-500">{session.className}</p>
                        <div className="flex items-center mt-1 text-xs text-gray-400">
                          <CalendarDaysIcon className="h-3 w-3 mr-1" />
                          {session.startTime} - {session.endTime}
                          <span className="mx-1">•</span>
                          {session.room}
                        </div>
                      </div>
                      <div className="ml-2">
                        {session.isCompleted ? (
                          <CheckCircleIcon className="h-5 w-5 text-green-500" />
                        ) : (
                          <ClockIcon className="h-5 w-5 text-gray-400" />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Zone principale */}
          <div className="lg:col-span-3">
            {currentSession ? (
              <div className="space-y-6">
                {/* Informations de la session */}
                <div className="card p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">
                        {currentSession.courseName} - {currentSession.className}
                      </h2>
                      <div className="flex items-center mt-2 text-sm text-gray-500">
                        <CalendarDaysIcon className="h-4 w-4 mr-1" />
                        {new Date(currentSession.date).toLocaleDateString('fr-FR')}
                        <span className="mx-2">•</span>
                        <ClockIcon className="h-4 w-4 mr-1" />
                        {currentSession.startTime} - {currentSession.endTime}
                        <span className="mx-2">•</span>
                        <AcademicCapIcon className="h-4 w-4 mr-1" />
                        {currentSession.room}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {currentSession.isCompleted ? (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                          <CheckCircleIcon className="h-4 w-4 mr-1" />
                          Terminé
                        </span>
                      ) : (
                        <button
                          onClick={saveAttendance}
                          disabled={isSaving}
                          className="btn-primary"
                        >
                          {isSaving ? 'Sauvegarde...' : 'Terminer la présence'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Statistiques */}
                {stats && (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="card p-4">
                      <div className="flex items-center">
                        <UserIcon className="h-6 w-6 text-gray-600 mr-2" />
                        <div>
                          <p className="text-sm text-gray-500">Total</p>
                          <p className="text-lg font-bold text-gray-900">{stats.totalStudents}</p>
                        </div>
                      </div>
                    </div>
                    <div className="card p-4">
                      <div className="flex items-center">
                        <CheckCircleIcon className="h-6 w-6 text-green-600 mr-2" />
                        <div>
                          <p className="text-sm text-gray-500">Présents</p>
                          <p className="text-lg font-bold text-gray-900">{stats.present}</p>
                        </div>
                      </div>
                    </div>
                    <div className="card p-4">
                      <div className="flex items-center">
                        <XCircleIcon className="h-6 w-6 text-red-600 mr-2" />
                        <div>
                          <p className="text-sm text-gray-500">Absents</p>
                          <p className="text-lg font-bold text-gray-900">{stats.absent}</p>
                        </div>
                      </div>
                    </div>
                    <div className="card p-4">
                      <div className="flex items-center">
                        <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 mr-2" />
                        <div>
                          <p className="text-sm text-gray-500">Retards</p>
                          <p className="text-lg font-bold text-gray-900">{stats.late}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Recherche */}
                <div className="card p-4">
                  <input
                    type="text"
                    placeholder="Rechercher un étudiant..."
                    className="input"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>

                {/* Liste des étudiants */}
                <div className="card">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900">
                      Liste des étudiants ({filteredStudents.length})
                    </h3>
                  </div>
                  <div className="divide-y divide-gray-200">
                    {filteredStudents.map((student) => (
                      <div key={student.id} className="p-6">
                        <div className="flex items-center justify-between">
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
                                  <UserIcon className="h-6 w-6 text-gray-600" />
                                </div>
                              )}
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {student.first_name} {student.last_name}
                              </div>
                              <div className="text-sm text-gray-500">
                                {student.email}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-2">
                            {/* Statut actuel */}
                            <div className="mr-4">
                              {getStatusIcon(student.status)}
                            </div>

                            {/* Boutons d'action */}
                            {!currentSession.isCompleted && (
                              <div className="flex space-x-1">
                                <button
                                  onClick={() => markAttendance(student.id, 'present')}
                                  className={`px-3 py-1 text-xs font-medium rounded ${
                                    student.status === 'present'
                                      ? 'bg-green-100 text-green-800'
                                      : 'bg-gray-100 text-gray-700 hover:bg-green-50'
                                  }`}
                                >
                                  Présent
                                </button>
                                <button
                                  onClick={() => markAttendance(student.id, 'absent')}
                                  className={`px-3 py-1 text-xs font-medium rounded ${
                                    student.status === 'absent'
                                      ? 'bg-red-100 text-red-800'
                                      : 'bg-gray-100 text-gray-700 hover:bg-red-50'
                                  }`}
                                >
                                  Absent
                                </button>
                                <button
                                  onClick={() => markAttendance(student.id, 'late')}
                                  className={`px-3 py-1 text-xs font-medium rounded ${
                                    student.status === 'late'
                                      ? 'bg-yellow-100 text-yellow-800'
                                      : 'bg-gray-100 text-gray-700 hover:bg-yellow-50'
                                  }`}
                                >
                                  Retard
                                </button>
                                <button
                                  onClick={() => markAttendance(student.id, 'justified')}
                                  className={`px-3 py-1 text-xs font-medium rounded ${
                                    student.status === 'justified'
                                      ? 'bg-blue-100 text-blue-800'
                                      : 'bg-gray-100 text-gray-700 hover:bg-blue-50'
                                  }`}
                                >
                                  Justifié
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="card p-12 text-center">
                <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune session sélectionnée</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Sélectionnez une session dans la liste pour commencer la prise de présence.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default TeacherAttendance;
