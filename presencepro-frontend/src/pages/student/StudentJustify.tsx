import React, { useState, useEffect } from 'react';
import Layout from '../../components/common/Layout';
import { CardSpinner } from '../../components/common/LoadingSpinner';
import {
  DocumentTextIcon,
  CalendarDaysIcon,
  ClockIcon,
  PaperClipIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

// Types pour les justifications
interface Absence {
  id: string;
  date: string;
  courseName: string;
  teacherName: string;
  startTime: string;
  endTime: string;
  status: 'unjustified' | 'pending' | 'approved' | 'rejected';
  canJustify: boolean;
}

interface JustificationForm {
  absenceId: string;
  reason: string;
  description: string;
  attachments: File[];
}

interface JustificationHistory {
  id: string;
  absenceDate: string;
  courseName: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  submittedAt: string;
  reviewedAt?: string;
  reviewComments?: string;
}

const StudentJustify: React.FC = () => {
  const [absences, setAbsences] = useState<Absence[]>([]);
  const [justificationHistory, setJustificationHistory] = useState<JustificationHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAbsence, setSelectedAbsence] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [form, setForm] = useState<JustificationForm>({
    absenceId: '',
    reason: '',
    description: '',
    attachments: [],
  });

  // Simuler le chargement des données
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);

      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Données simulées
      const mockAbsences: Absence[] = [
        {
          id: '1',
          date: '2024-01-15',
          courseName: 'Mathématiques',
          teacherName: 'Jean Martin',
          startTime: '08:00',
          endTime: '09:00',
          status: 'unjustified',
          canJustify: true,
        },
        {
          id: '2',
          date: '2024-01-14',
          courseName: 'Physique',
          teacherName: 'Sophie Bernard',
          startTime: '10:00',
          endTime: '11:00',
          status: 'pending',
          canJustify: false,
        },
        {
          id: '3',
          date: '2024-01-12',
          courseName: 'Histoire',
          teacherName: 'Claire Dubois',
          startTime: '14:00',
          endTime: '15:00',
          status: 'approved',
          canJustify: false,
        },
      ];

      const mockHistory: JustificationHistory[] = [
        {
          id: '1',
          absenceDate: '2024-01-14',
          courseName: 'Physique',
          reason: 'Rendez-vous médical',
          status: 'pending',
          submittedAt: '2024-01-14T18:30:00Z',
        },
        {
          id: '2',
          absenceDate: '2024-01-12',
          courseName: 'Histoire',
          reason: 'Maladie',
          status: 'approved',
          submittedAt: '2024-01-12T20:15:00Z',
          reviewedAt: '2024-01-13T08:00:00Z',
          reviewComments: 'Justification acceptée. Bon rétablissement.',
        },
        {
          id: '3',
          absenceDate: '2024-01-10',
          courseName: 'Français',
          reason: 'Problème familial',
          status: 'rejected',
          submittedAt: '2024-01-10T19:45:00Z',
          reviewedAt: '2024-01-11T09:30:00Z',
          reviewComments: 'Justification insuffisante. Veuillez fournir plus de détails.',
        },
      ];

      setAbsences(mockAbsences);
      setJustificationHistory(mockHistory);
      setIsLoading(false);
    };

    loadData();
  }, []);

  // Gérer la sélection d'une absence
  const handleSelectAbsence = (absenceId: string) => {
    setSelectedAbsence(absenceId);
    setForm(prev => ({ ...prev, absenceId, reason: '', description: '', attachments: [] }));
  };

  // Gérer les changements du formulaire
  const handleFormChange = (field: keyof JustificationForm, value: any) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  // Gérer l'ajout de fichiers
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setForm(prev => ({ ...prev, attachments: [...prev.attachments, ...files] }));
  };

  // Supprimer un fichier
  const removeFile = (index: number) => {
    setForm(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }));
  };

  // Soumettre la justification
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.absenceId || !form.reason || !form.description) return;

    setIsSubmitting(true);

    // Simulation d'un appel API
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Mettre à jour le statut de l'absence
    setAbsences(prev => prev.map(absence =>
      absence.id === form.absenceId
        ? { ...absence, status: 'pending', canJustify: false }
        : absence
    ));

    // Ajouter à l'historique
    const newJustification: JustificationHistory = {
      id: Date.now().toString(),
      absenceDate: absences.find(a => a.id === form.absenceId)?.date || '',
      courseName: absences.find(a => a.id === form.absenceId)?.courseName || '',
      reason: form.reason,
      status: 'pending',
      submittedAt: new Date().toISOString(),
    };

    setJustificationHistory(prev => [newJustification, ...prev]);

    // Réinitialiser le formulaire
    setForm({ absenceId: '', reason: '', description: '', attachments: [] });
    setSelectedAbsence(null);
    setIsSubmitting(false);
  };

  // Obtenir le badge de statut
  const getStatusBadge = (status: string) => {
    const badges = {
      unjustified: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    };

    const labels = {
      unjustified: 'Non justifiée',
      pending: 'En attente',
      approved: 'Approuvée',
      rejected: 'Rejetée',
    };

    const icons = {
      unjustified: <ExclamationTriangleIcon className="h-4 w-4 mr-1" />,
      pending: <ClockIcon className="h-4 w-4 mr-1" />,
      approved: <CheckCircleIcon className="h-4 w-4 mr-1" />,
      rejected: <XCircleIcon className="h-4 w-4 mr-1" />,
    };

    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md ${badges[status as keyof typeof badges]}`}>
        {icons[status as keyof typeof icons]}
        {labels[status as keyof typeof labels]}
      </span>
    );
  };

  if (isLoading) {
    return (
      <Layout title="Justifier une absence">
        <div className="space-y-6">
          <div className="card p-6">
            <CardSpinner text="Chargement des absences..." />
          </div>
        </div>
      </Layout>
    );
  }

  const unjustifiedAbsences = absences.filter(a => a.status === 'unjustified' && a.canJustify);

  return (
    <Layout title="Justifier une absence">
      <div className="space-y-6">
        {/* En-tête */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Justifier une absence
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Soumettez une justification pour vos absences non justifiées
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Formulaire de justification */}
          <div className="space-y-6">
            {/* Sélection de l'absence */}
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Absences à justifier ({unjustifiedAbsences.length})
              </h3>

              {unjustifiedAbsences.length > 0 ? (
                <div className="space-y-3">
                  {unjustifiedAbsences.map((absence) => (
                    <div
                      key={absence.id}
                      onClick={() => handleSelectAbsence(absence.id)}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedAbsence === absence.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">{absence.courseName}</div>
                          <div className="text-sm text-gray-500">
                            {new Date(absence.date).toLocaleDateString('fr-FR')} • {absence.startTime} - {absence.endTime}
                          </div>
                          <div className="text-sm text-gray-500">Enseignant: {absence.teacherName}</div>
                        </div>
                        <div>
                          {getStatusBadge(absence.status)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircleIcon className="mx-auto h-12 w-12 text-green-500" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune absence à justifier</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Toutes vos absences sont justifiées ou en cours de traitement.
                  </p>
                </div>
              )}
            </div>

            {/* Formulaire */}
            {selectedAbsence && (
              <div className="card p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Formulaire de justification
                </h3>

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Raison */}
                  <div>
                    <label className="label">Raison de l'absence *</label>
                    <select
                      className="input"
                      value={form.reason}
                      onChange={(e) => handleFormChange('reason', e.target.value)}
                      required
                    >
                      <option value="">Sélectionnez une raison</option>
                      <option value="Maladie">Maladie</option>
                      <option value="Rendez-vous médical">Rendez-vous médical</option>
                      <option value="Problème familial">Problème familial</option>
                      <option value="Transport">Problème de transport</option>
                      <option value="Autre">Autre</option>
                    </select>
                  </div>

                  {/* Description */}
                  <div>
                    <label className="label">Description détaillée *</label>
                    <textarea
                      rows={4}
                      className="input resize-none"
                      placeholder="Décrivez les circonstances de votre absence..."
                      value={form.description}
                      onChange={(e) => handleFormChange('description', e.target.value)}
                      required
                    />
                  </div>

                  {/* Pièces jointes */}
                  <div>
                    <label className="label">Pièces jointes (optionnel)</label>
                    <div className="mt-1">
                      <input
                        type="file"
                        multiple
                        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                        onChange={handleFileChange}
                        className="input"
                      />
                      <p className="mt-1 text-xs text-gray-500">
                        Formats acceptés: PDF, JPG, PNG, DOC, DOCX (max 5MB par fichier)
                      </p>
                    </div>

                    {/* Liste des fichiers */}
                    {form.attachments.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {form.attachments.map((file, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <div className="flex items-center">
                              <PaperClipIcon className="h-4 w-4 text-gray-400 mr-2" />
                              <span className="text-sm text-gray-700">{file.name}</span>
                            </div>
                            <button
                              type="button"
                              onClick={() => removeFile(index)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <XCircleIcon className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Boutons */}
                  <div className="flex space-x-3 pt-4">
                    <button
                      type="submit"
                      disabled={isSubmitting || !form.reason || !form.description}
                      className="btn-primary flex-1"
                    >
                      {isSubmitting ? 'Envoi en cours...' : 'Soumettre la justification'}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedAbsence(null);
                        setForm({ absenceId: '', reason: '', description: '', attachments: [] });
                      }}
                      className="btn-secondary"
                    >
                      Annuler
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>

          {/* Historique des justifications */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Historique des justifications
            </h3>

            {justificationHistory.length > 0 ? (
              <div className="space-y-4">
                {justificationHistory.map((justification) => (
                  <div key={justification.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium text-gray-900">{justification.courseName}</div>
                      {getStatusBadge(justification.status)}
                    </div>

                    <div className="space-y-1 text-sm text-gray-600">
                      <div className="flex items-center">
                        <CalendarDaysIcon className="h-4 w-4 mr-1" />
                        Absence: {new Date(justification.absenceDate).toLocaleDateString('fr-FR')}
                      </div>
                      <div>Raison: {justification.reason}</div>
                      <div className="flex items-center">
                        <ClockIcon className="h-4 w-4 mr-1" />
                        Soumis: {new Date(justification.submittedAt).toLocaleDateString('fr-FR')}
                      </div>

                      {justification.reviewedAt && (
                        <div className="mt-2 p-2 bg-gray-50 rounded">
                          <div className="text-xs text-gray-500">
                            Révisé le {new Date(justification.reviewedAt).toLocaleDateString('fr-FR')}
                          </div>
                          {justification.reviewComments && (
                            <div className="text-sm text-gray-700 mt-1">
                              {justification.reviewComments}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune justification</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Vous n'avez encore soumis aucune justification.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default StudentJustify;
