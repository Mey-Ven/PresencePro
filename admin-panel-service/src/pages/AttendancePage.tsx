import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, Table, Badge, Form, InputGroup, Spinner, Alert } from 'react-bootstrap';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { AttendanceRecord, PaginatedResponse, AttendanceFilters } from '../types';
import { useApp } from '../contexts/AppContext';

const AttendancePage: React.FC = () => {
  const { addNotification } = useApp();
  
  const [attendanceRecords, setAttendanceRecords] = useState<PaginatedResponse<AttendanceRecord> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [filters, setFilters] = useState<AttendanceFilters>({
    start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
  });
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    loadAttendanceRecords();
  }, [currentPage, filters]);

  const loadAttendanceRecords = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Données simulées
      const mockData: PaginatedResponse<AttendanceRecord> = {
        data: [
          {
            id: '1',
            student_id: 'student_1',
            course_id: 'course_1',
            date: '2025-06-20',
            status: 'present',
            method: 'face_recognition',
            marked_by: 'system',
            marked_at: '2025-06-20T08:00:00Z',
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
            course_id: 'course_1',
            date: '2025-06-20',
            status: 'absent',
            method: 'manual',
            marked_by: 'teacher_1',
            marked_at: '2025-06-20T08:30:00Z',
            notes: 'Absence non justifiée',
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
          },
          {
            id: '3',
            student_id: 'student_3',
            course_id: 'course_1',
            date: '2025-06-20',
            status: 'late',
            method: 'manual',
            marked_by: 'teacher_1',
            marked_at: '2025-06-20T08:15:00Z',
            notes: 'Arrivé 15 minutes en retard',
            student: {
              id: 'student_3',
              user_id: 'user_3',
              student_number: 'STU003',
              class_id: 'class_1',
              enrollment_date: '2024-09-01',
              is_active: true,
              user: {
                id: 'user_3',
                email: 'sophie.bernard@email.com',
                first_name: 'Sophie',
                last_name: 'Bernard',
                role: 'student',
                is_active: true,
                created_at: '2024-09-01T00:00:00Z',
                updated_at: '2024-09-01T00:00:00Z',
              }
            }
          }
        ],
        total: 3,
        page: 1,
        per_page: 20,
        total_pages: 1,
      };
      
      setAttendanceRecords(mockData);
    } catch (err: any) {
      setError(err.message || 'Erreur lors du chargement des présences');
      addNotification({
        type: 'error',
        title: 'Erreur',
        message: 'Impossible de charger les données de présence',
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'present': return 'success';
      case 'absent': return 'danger';
      case 'late': return 'warning';
      case 'excused': return 'info';
      default: return 'secondary';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'present': return 'Présent';
      case 'absent': return 'Absent';
      case 'late': return 'Retard';
      case 'excused': return 'Excusé';
      default: return status;
    }
  };

  const getMethodIcon = (method: string) => {
    switch (method) {
      case 'face_recognition': return 'fas fa-camera';
      case 'manual': return 'fas fa-hand-paper';
      case 'qr_code': return 'fas fa-qrcode';
      default: return 'fas fa-question';
    }
  };

  const getMethodLabel = (method: string) => {
    switch (method) {
      case 'face_recognition': return 'Reconnaissance faciale';
      case 'manual': return 'Manuel';
      case 'qr_code': return 'QR Code';
      default: return method;
    }
  };

  return (
    <div className="attendance-page">
      {/* En-tête */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="mb-1">Gestion des présences</h2>
          <p className="text-muted mb-0">
            Consultez et gérez les présences des étudiants
          </p>
        </div>
        <div className="d-flex gap-2">
          <Button variant="outline-primary">
            <i className="fas fa-download me-2"></i>
            Exporter
          </Button>
          <Button variant="primary">
            <i className="fas fa-plus me-2"></i>
            Marquer présence
          </Button>
        </div>
      </div>

      {/* Filtres */}
      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={3}>
              <Form.Group>
                <Form.Label>Date de début</Form.Label>
                <Form.Control
                  type="date"
                  value={filters.start_date}
                  onChange={(e) => setFilters({...filters, start_date: e.target.value})}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group>
                <Form.Label>Date de fin</Form.Label>
                <Form.Control
                  type="date"
                  value={filters.end_date}
                  onChange={(e) => setFilters({...filters, end_date: e.target.value})}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group>
                <Form.Label>Statut</Form.Label>
                <Form.Select
                  value={filters.status || ''}
                  onChange={(e) => setFilters({...filters, status: e.target.value || undefined})}
                >
                  <option value="">Tous les statuts</option>
                  <option value="present">Présent</option>
                  <option value="absent">Absent</option>
                  <option value="late">Retard</option>
                  <option value="excused">Excusé</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group>
                <Form.Label>Méthode</Form.Label>
                <Form.Select
                  value={filters.method || ''}
                  onChange={(e) => setFilters({...filters, method: e.target.value || undefined})}
                >
                  <option value="">Toutes les méthodes</option>
                  <option value="face_recognition">Reconnaissance faciale</option>
                  <option value="manual">Manuel</option>
                  <option value="qr_code">QR Code</option>
                </Form.Select>
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
              <i className="fas fa-check-circle text-success fa-2x mb-2"></i>
              <h4 className="text-success">85%</h4>
              <small className="text-muted">Taux de présence</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-user-check text-primary fa-2x mb-2"></i>
              <h4 className="text-primary">127</h4>
              <small className="text-muted">Présents aujourd'hui</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-user-times text-danger fa-2x mb-2"></i>
              <h4 className="text-danger">23</h4>
              <small className="text-muted">Absents aujourd'hui</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-clock text-warning fa-2x mb-2"></i>
              <h4 className="text-warning">8</h4>
              <small className="text-muted">Retards aujourd'hui</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Tableau des présences */}
      <Card>
        <Card.Header>
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">
              <i className="fas fa-calendar-check me-2"></i>
              Registre des présences
            </h5>
            {attendanceRecords && (
              <small className="text-muted">
                {attendanceRecords.total} enregistrement(s)
              </small>
            )}
          </div>
        </Card.Header>
        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" />
              <div className="mt-2">Chargement des présences...</div>
            </div>
          ) : error ? (
            <Alert variant="danger" className="m-3">
              {error}
            </Alert>
          ) : attendanceRecords && attendanceRecords.data.length > 0 ? (
            <Table responsive hover className="mb-0">
              <thead>
                <tr>
                  <th>Étudiant</th>
                  <th>Date</th>
                  <th>Statut</th>
                  <th>Méthode</th>
                  <th>Marqué par</th>
                  <th>Notes</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {attendanceRecords.data.map((record) => (
                  <tr key={record.id}>
                    <td>
                      <div className="d-flex align-items-center">
                        <i className="fas fa-user-circle text-muted me-2"></i>
                        <div>
                          <div className="fw-semibold">
                            {record.student?.user.first_name} {record.student?.user.last_name}
                          </div>
                          <small className="text-muted">
                            {record.student?.student_number}
                          </small>
                        </div>
                      </div>
                    </td>
                    <td>
                      {new Date(record.date).toLocaleDateString('fr-FR')}
                      <br />
                      <small className="text-muted">
                        {new Date(record.marked_at).toLocaleTimeString('fr-FR')}
                      </small>
                    </td>
                    <td>
                      <Badge bg={getStatusBadgeVariant(record.status)}>
                        {getStatusLabel(record.status)}
                      </Badge>
                    </td>
                    <td>
                      <div className="d-flex align-items-center">
                        <i className={`${getMethodIcon(record.method)} me-2`}></i>
                        {getMethodLabel(record.method)}
                      </div>
                    </td>
                    <td>
                      {record.marked_by === 'system' ? 'Système' : record.marked_by}
                    </td>
                    <td>
                      {record.notes && (
                        <small className="text-muted">{record.notes}</small>
                      )}
                    </td>
                    <td>
                      <div className="d-flex gap-1">
                        <Button variant="outline-primary" size="sm">
                          <i className="fas fa-edit"></i>
                        </Button>
                        <Button variant="outline-danger" size="sm">
                          <i className="fas fa-trash"></i>
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : (
            <div className="text-center py-5">
              <i className="fas fa-calendar-times text-muted" style={{ fontSize: '3rem' }}></i>
              <div className="mt-3">
                <h5>Aucune donnée de présence</h5>
                <p className="text-muted">
                  Aucun enregistrement de présence trouvé pour la période sélectionnée.
                </p>
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default AttendancePage;
