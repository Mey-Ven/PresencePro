import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  CalendarDaysIcon,
  ClockIcon,
  AcademicCapIcon,
  MapPinIcon,
  UserIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';

// Types pour le planning
interface Child {
  id: string;
  firstName: string;
  lastName: string;
  className: string;
  photo?: string;
}

interface ScheduleEvent {
  id: string;
  courseName: string;
  teacherName: string;
  room: string;
  startTime: string;
  endTime: string;
  type: 'course' | 'exam' | 'event' | 'break';
  color: string;
  description?: string;
}

interface DaySchedule {
  date: string;
  dayName: string;
  events: ScheduleEvent[];
}

interface WeekSchedule {
  weekStart: string;
  weekEnd: string;
  days: DaySchedule[];
}

const ParentSchedule: React.FC = () => {
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChild, setSelectedChild] = useState<string | null>(null);
  const [weekSchedule, setWeekSchedule] = useState<WeekSchedule | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const [viewMode, setViewMode] = useState<'week' | 'day'>('week');
  const [selectedDay, setSelectedDay] = useState<string | null>(null);

  // Simuler le chargement des données
  useEffect(() => {
    const loadScheduleData = async () => {
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
        },
        {
          id: '2',
          firstName: 'Emma',
          lastName: 'Moreau',
          className: '5ème B',
        },
      ];

      // Générer une semaine de planning
      const startOfWeek = new Date(currentWeek);
      startOfWeek.setDate(currentWeek.getDate() - currentWeek.getDay() + 1); // Lundi

      const mockWeekSchedule: WeekSchedule = {
        weekStart: startOfWeek.toISOString().split('T')[0],
        weekEnd: new Date(startOfWeek.getTime() + 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        days: [],
      };

      // Générer les jours de la semaine
      const dayNames = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];

      for (let i = 0; i < 7; i++) {
        const currentDay = new Date(startOfWeek.getTime() + i * 24 * 60 * 60 * 1000);
        const daySchedule: DaySchedule = {
          date: currentDay.toISOString().split('T')[0],
          dayName: dayNames[i],
          events: [],
        };

        // Ajouter des cours pour les jours de semaine
        if (i < 5) { // Lundi à Vendredi
          const courses = [
            { name: 'Mathématiques', teacher: 'Jean Martin', room: 'Salle 101', color: 'bg-blue-500' },
            { name: 'Physique', teacher: 'Sophie Bernard', room: 'Salle 102', color: 'bg-green-500' },
            { name: 'Histoire', teacher: 'Claire Dubois', room: 'Salle 103', color: 'bg-purple-500' },
            { name: 'Français', teacher: 'Marie Durand', room: 'Salle 104', color: 'bg-red-500' },
            { name: 'Anglais', teacher: 'Paul Smith', room: 'Salle 105', color: 'bg-yellow-500' },
          ];

          // Générer des créneaux horaires
          const timeSlots = [
            { start: '08:00', end: '09:00' },
            { start: '09:00', end: '10:00' },
            { start: '10:15', end: '11:15' },
            { start: '11:15', end: '12:15' },
            { start: '14:00', end: '15:00' },
            { start: '15:00', end: '16:00' },
            { start: '16:15', end: '17:15' },
          ];

          // Ajouter quelques cours par jour
          const coursesPerDay = Math.floor(Math.random() * 4) + 3; // 3-6 cours par jour
          for (let j = 0; j < coursesPerDay && j < timeSlots.length; j++) {
            const course = courses[j % courses.length];
            const timeSlot = timeSlots[j];

            daySchedule.events.push({
              id: `${i}-${j}`,
              courseName: course.name,
              teacherName: course.teacher,
              room: course.room,
              startTime: timeSlot.start,
              endTime: timeSlot.end,
              type: 'course',
              color: course.color,
            });
          }

          // Ajouter une pause déjeuner
          daySchedule.events.push({
            id: `${i}-lunch`,
            courseName: 'Pause déjeuner',
            teacherName: '',
            room: 'Cantine',
            startTime: '12:15',
            endTime: '14:00',
            type: 'break',
            color: 'bg-gray-400',
          });
        }

        mockWeekSchedule.days.push(daySchedule);
      }

      setChildren(mockChildren);
      setSelectedChild(mockChildren[0].id);
      setWeekSchedule(mockWeekSchedule);
      setIsLoading(false);
    };

    loadScheduleData();
  }, [currentWeek]);

  // Navigation entre les semaines
  const navigateWeek = (direction: 'prev' | 'next') => {
    const newWeek = new Date(currentWeek);
    newWeek.setDate(currentWeek.getDate() + (direction === 'next' ? 7 : -7));
    setCurrentWeek(newWeek);
  };

  // Obtenir l'enfant sélectionné
  const currentChild = children.find(c => c.id === selectedChild);

  // Formater l'heure
  const formatTime = (time: string) => {
    return time;
  };

  // Obtenir la couleur du type d'événement
  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'course':
        return 'border-l-blue-500';
      case 'exam':
        return 'border-l-red-500';
      case 'event':
        return 'border-l-green-500';
      case 'break':
        return 'border-l-gray-400';
      default:
        return 'border-l-gray-300';
    }
  };

  if (isLoading) {
    return (
      <Layout title="Planning de mon enfant">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement du planning..." />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Planning de mon enfant">
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Planning de mon enfant
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Consultez l'emploi du temps et les événements à venir
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
            {/* Mode d'affichage */}
            <div className="flex rounded-md shadow-sm">
              <button
                onClick={() => setViewMode('week')}
                className={`px-3 py-2 text-sm font-medium rounded-l-md border ${
                  viewMode === 'week'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                Semaine
              </button>
              <button
                onClick={() => setViewMode('day')}
                className={`px-3 py-2 text-sm font-medium rounded-r-md border-t border-r border-b ${
                  viewMode === 'day'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                Jour
              </button>
            </div>
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
                  Classe: {currentChild.className}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation de semaine */}
        <div className="card p-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigateWeek('prev')}
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <ChevronLeftIcon className="h-4 w-4 mr-1" />
              Semaine précédente
            </button>

            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">
                {weekSchedule && (
                  <>
                    {new Date(weekSchedule.weekStart).toLocaleDateString('fr-FR')} - {new Date(weekSchedule.weekEnd).toLocaleDateString('fr-FR')}
                  </>
                )}
              </h3>
            </div>

            <button
              onClick={() => navigateWeek('next')}
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Semaine suivante
              <ChevronRightIcon className="h-4 w-4 ml-1" />
            </button>
          </div>
        </div>

        {/* Planning */}
        {weekSchedule && (
          <>
            {viewMode === 'week' ? (
              /* Vue semaine */
              <div className="card overflow-hidden">
                <div className="overflow-x-auto">
                  <div className="grid grid-cols-7 gap-px bg-gray-200">
                    {weekSchedule.days.map((day) => (
                      <div key={day.date} className="bg-white">
                        {/* En-tête du jour */}
                        <div className="p-4 border-b border-gray-200">
                          <div className="text-center">
                            <div className="text-sm font-medium text-gray-900">{day.dayName}</div>
                            <div className="text-sm text-gray-500">
                              {new Date(day.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}
                            </div>
                          </div>
                        </div>

                        {/* Événements du jour */}
                        <div className="p-2 space-y-1 min-h-96">
                          {day.events.map((event) => (
                            <div
                              key={event.id}
                              className={`p-2 rounded text-xs border-l-4 ${getEventTypeColor(event.type)} bg-gray-50 hover:bg-gray-100 cursor-pointer`}
                              onClick={() => {
                                setSelectedDay(day.date);
                                setViewMode('day');
                              }}
                            >
                              <div className="font-medium text-gray-900 truncate">
                                {event.courseName}
                              </div>
                              <div className="text-gray-600">
                                {formatTime(event.startTime)} - {formatTime(event.endTime)}
                              </div>
                              {event.teacherName && (
                                <div className="text-gray-500 truncate">
                                  {event.teacherName}
                                </div>
                              )}
                              <div className="text-gray-500 truncate">
                                {event.room}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              /* Vue jour */
              <div className="space-y-4">
                {/* Sélection du jour */}
                <div className="card p-4">
                  <select
                    className="input"
                    value={selectedDay || weekSchedule.days[0]?.date || ''}
                    onChange={(e) => setSelectedDay(e.target.value)}
                  >
                    {weekSchedule.days.map((day) => (
                      <option key={day.date} value={day.date}>
                        {day.dayName} {new Date(day.date).toLocaleDateString('fr-FR')}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Détail du jour */}
                {(() => {
                  const currentDay = weekSchedule.days.find(d => d.date === selectedDay) || weekSchedule.days[0];
                  return (
                    <div className="card">
                      <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-medium text-gray-900">
                          {currentDay.dayName} {new Date(currentDay.date).toLocaleDateString('fr-FR')}
                        </h3>
                      </div>

                      <div className="divide-y divide-gray-200">
                        {currentDay.events.length > 0 ? (
                          currentDay.events.map((event) => (
                            <div key={event.id} className="p-6">
                              <div className="flex items-center space-x-4">
                                <div className="flex-shrink-0">
                                  <div className={`w-4 h-4 rounded ${event.color}`}></div>
                                </div>
                                <div className="flex-1">
                                  <div className="flex items-center justify-between">
                                    <h4 className="text-lg font-medium text-gray-900">
                                      {event.courseName}
                                    </h4>
                                    <div className="flex items-center text-sm text-gray-500">
                                      <ClockIcon className="h-4 w-4 mr-1" />
                                      {formatTime(event.startTime)} - {formatTime(event.endTime)}
                                    </div>
                                  </div>
                                  <div className="mt-2 space-y-1">
                                    {event.teacherName && (
                                      <div className="flex items-center text-sm text-gray-600">
                                        <AcademicCapIcon className="h-4 w-4 mr-1" />
                                        {event.teacherName}
                                      </div>
                                    )}
                                    <div className="flex items-center text-sm text-gray-600">
                                      <MapPinIcon className="h-4 w-4 mr-1" />
                                      {event.room}
                                    </div>
                                  </div>
                                  {event.description && (
                                    <div className="mt-2 text-sm text-gray-600">
                                      {event.description}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="p-12 text-center">
                            <CalendarDaysIcon className="mx-auto h-12 w-12 text-gray-400" />
                            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun cours</h3>
                            <p className="mt-1 text-sm text-gray-500">
                              Aucun cours prévu pour cette journée.
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
};

export default ParentSchedule;
