import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, Table, Badge, Form, Spinner, Alert } from 'react-bootstrap';
import { Justification, PaginatedResponse } from '../types';
import { useApp } from '../contexts/AppContext';

const JustificationsPage: React.FC = () => {
  const { addNotification } = useApp();
  
  const [justifications, setJustifications] = useState<PaginatedResponse<Justification> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  useEffect(() => {
    loadJustifications();
  }, [statusFilter, typeFilter]);

  const loadJustifications = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Données simulées
      const mockData: PaginatedResponse<Justification> = {
        data: [
          {
            id: '1',
            student_id: 'student_1',
            title: 'Rendez-vous médical',
            description: 'Consultation chez le médecin spécialiste',
            justification_type: 'medical',
            priority: 'high',
            status: 'submitted',
            absence_start_date: '2025-06-21T08:00:00Z',
            absence_end_date: '2025-06-21T12:00:00Z',
            created_at: '2025-06-20T10:00:00Z',
            updated_at: '2025-06-20T10:00:00Z',
            student: {
              id: 'student_1',
              user_id: 'user_1',
              student_number: 'STU001',
              class_id: 'class_1',
              enrollment_date: '2024-09-01',
              is_active: true,
              user: {
                id: 'user_1',
                email: 'marie.dupont@email.com',
                first_name: 'Marie',
                last_name: 'Dupont',
                role: 'student',
                is_active: true,
                created_at: '2024-09-01T00:00:00Z',
                updated_at: '2024-09-01T00:00:00Z',
              }
            }
          },
          {
            id: '2',
            student_id: 'student_2',
            title: 'Événement familial',
            description: 'Mariage dans la famille',
            justification_type: 'family',
            priority: 'medium',
            status: 'parent_approved',
            absence_start_date: '2025-06-25T08:00:00Z',
            absence_end_date: '2025-06-25T18:00:00Z',
            created_at: '2025-06-18T14:00:00Z',
            updated_at: '2025-06-19T09:00:00Z',
            student: {
              id: 'student_2',
              user_id: 'user_2',
              student_number: 'STU002',
              class_id: 'class_1',
              enrollment_date: '2024-09-01',
              is_active: true,
              user: {
                id: 'user_2',
                email: 'pierre.martin@email.com',
                first_name: 'Pierre',
                last_name: 'Martin',
                role: 'student',
                is_active: true,
                created_at: '2024-09-01T00:00:00Z',
                updated_at: '2024-09-01T00:00:00Z',
              }
            }
          }
        ],
        total: 2,
        page: 1,
        per_page: 20,
        total_pages: 1,
      };
      
      setJustifications(mockData);
    } catch (err: any) {
      setError(err.message || 'Erreur lors du chargement des justifications');
      addNotification({
        type: 'error',
        title: 'Erreur',
        message: 'Impossible de charger les justifications',
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'draft': return 'secondary';
      case 'submitted': return 'warning';
      case 'parent_approved': return 'info';
      case 'admin_validated': return 'success';
      case 'rejected': return 'danger';
      default: return 'secondary';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'draft': return 'Brouillon';
      case 'submitted': return 'Soumise';
      case 'parent_approved': return 'Approuvée par le parent';
      case 'admin_validated': return 'Validée';
      case 'rejected': return 'Rejetée';
      default: return status;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'medical': return 'Médical';
      case 'family': return 'Familial';
      case 'transport': return 'Transport';
      case 'personal': return 'Personnel';
      case 'academic': return 'Académique';
      default: return type;
    }
  };

  const getPriorityBadgeVariant = (priority: string) => {
    switch (priority) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'danger';
      case 'urgent': return 'dark';
      default: return 'secondary';
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'low': return 'Faible';
      case 'medium': return 'Moyenne';
      case 'high': return 'Élevée';
      case 'urgent': return 'Urgente';
      default: return priority;
    }
  };

  const handleApprove = async (id: string) => {
    try {
      // Simuler l'approbation
      addNotification({
        type: 'success',
        title: 'Justification approuvée',
        message: 'La justification a été approuvée avec succès',
      });
      loadJustifications();
    } catch (err: any) {
      addNotification({
        type: 'error',
        title: 'Erreur',
        message: 'Impossible d\'approuver la justification',
      });
    }
  };

  const handleReject = async (id: string) => {
    try {
      // Simuler le rejet
      addNotification({
        type: 'info',
        title: 'Justification rejetée',
        message: 'La justification a été rejetée',
      });
      loadJustifications();
    } catch (err: any) {
      addNotification({
        type: 'error',
        title: 'Erreur',
        message: 'Impossible de rejeter la justification',
      });
    }
  };

  return (
    <div className="justifications-page">
      {/* En-tête */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="mb-1">Gestion des justifications</h2>
          <p className="text-muted mb-0">
            Gérez les demandes de justification d'absence des étudiants
          </p>
        </div>
        <Button variant="primary">
          <i className="fas fa-plus me-2"></i>
          Nouvelle justification
        </Button>
      </div>

      {/* Filtres */}
      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={4}>
              <Form.Group>
                <Form.Label>Statut</Form.Label>
                <Form.Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">Tous les statuts</option>
                  <option value="submitted">Soumises</option>
                  <option value="parent_approved">Approuvées par le parent</option>
                  <option value="admin_validated">Validées</option>
                  <option value="rejected">Rejetées</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label>Type</Form.Label>
                <Form.Select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                >
                  <option value="">Tous les types</option>
                  <option value="medical">Médical</option>
                  <option value="family">Familial</option>
                  <option value="transport">Transport</option>
                  <option value="personal">Personnel</option>
                  <option value="academic">Académique</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label>&nbsp;</Form.Label>
                <div className="d-flex gap-2">
                  <Button variant="outline-primary" className="w-100">
                    <i className="fas fa-search me-2"></i>
                    Rechercher
                  </Button>
                  <Button variant="outline-secondary" className="w-100">
                    <i className="fas fa-download me-2"></i>
                    Exporter
                  </Button>
                </div>
              </Form.Group>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Statistiques rapides */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-clock text-warning fa-2x mb-2"></i>
              <h4 className="text-warning">12</h4>
              <small className="text-muted">En attente</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-check-circle text-success fa-2x mb-2"></i>
              <h4 className="text-success">45</h4>
              <small className="text-muted">Approuvées</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-times-circle text-danger fa-2x mb-2"></i>
              <h4 className="text-danger">3</h4>
              <small className="text-muted">Rejetées</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-file-medical text-info fa-2x mb-2"></i>
              <h4 className="text-info">60</h4>
              <small className="text-muted">Total ce mois</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Tableau des justifications */}
      <Card>
        <Card.Header>
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">
              <i className="fas fa-file-medical me-2"></i>
              Liste des justifications
            </h5>
            {justifications && (
              <small className="text-muted">
                {justifications.total} justification(s)
              </small>
            )}
          </div>
        </Card.Header>
        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" />
              <div className="mt-2">Chargement des justifications...</div>
            </div>
          ) : error ? (
            <Alert variant="danger" className="m-3">
              {error}
            </Alert>
          ) : justifications && justifications.data.length > 0 ? (
            <Table responsive hover className="mb-0">
              <thead>
                <tr>
                  <th>Étudiant</th>
                  <th>Titre</th>
                  <th>Type</th>
                  <th>Priorité</th>
                  <th>Période d'absence</th>
                  <th>Statut</th>
                  <th>Créée le</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {justifications.data.map((justification) => (
                  <tr key={justification.id}>
                    <td>
                      <div className="d-flex align-items-center">
                        <i className="fas fa-user-circle text-muted me-2"></i>
                        <div>
                          <div className="fw-semibold">
                            {justification.student?.user.first_name} {justification.student?.user.last_name}
                          </div>
                          <small className="text-muted">
                            {justification.student?.student_number}
                          </small>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="fw-semibold">{justification.title}</div>
                      <small className="text-muted">{justification.description}</small>
                    </td>
                    <td>
                      <Badge bg="secondary">
                        {getTypeLabel(justification.justification_type)}
                      </Badge>
                    </td>
                    <td>
                      <Badge bg={getPriorityBadgeVariant(justification.priority)}>
                        {getPriorityLabel(justification.priority)}
                      </Badge>
                    </td>
                    <td>
                      <div>
                        <small>Du: {new Date(justification.absence_start_date).toLocaleDateString('fr-FR')}</small>
                        <br />
                        <small>Au: {new Date(justification.absence_end_date).toLocaleDateString('fr-FR')}</small>
                      </div>
                    </td>
                    <td>
                      <Badge bg={getStatusBadgeVariant(justification.status)}>
                        {getStatusLabel(justification.status)}
                      </Badge>
                    </td>
                    <td>
                      {new Date(justification.created_at).toLocaleDateString('fr-FR')}
                    </td>
                    <td>
                      <div className="d-flex gap-1">
                        <Button variant="outline-primary" size="sm">
                          <i className="fas fa-eye"></i>
                        </Button>
                        {justification.status === 'submitted' && (
                          <>
                            <Button 
                              variant="outline-success" 
                              size="sm"
                              onClick={() => handleApprove(justification.id)}
                            >
                              <i className="fas fa-check"></i>
                            </Button>
                            <Button 
                              variant="outline-danger" 
                              size="sm"
                              onClick={() => handleReject(justification.id)}
                            >
                              <i className="fas fa-times"></i>
                            </Button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : (
            <div className="text-center py-5">
              <i className="fas fa-file-medical text-muted" style={{ fontSize: '3rem' }}></i>
              <div className="mt-3">
                <h5>Aucune justification</h5>
                <p className="text-muted">
                  Aucune demande de justification trouvée.
                </p>
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default JustificationsPage;
