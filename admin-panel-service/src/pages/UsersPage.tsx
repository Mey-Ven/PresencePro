import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Row, Col, Card, Button, Table, Badge, Form, InputGroup, Spinner, Alert } from 'react-bootstrap';
import { User, Student, Teacher, Parent, PaginatedResponse } from '../types';
import userService from '../services/userService';
import { useApp } from '../contexts/AppContext';

const UsersPage: React.FC = () => {
  const navigate = useNavigate();
  const { addNotification } = useApp();
  
  const [users, setUsers] = useState<PaginatedResponse<User> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    loadUsers();
  }, [currentPage, selectedRole]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError('');
      
      const filters = {
        ...(selectedRole && { role: selectedRole }),
        ...(searchTerm && { search: searchTerm }),
      };
      
      const response = await userService.getUsers(currentPage, 20, filters);
      setUsers(response);
    } catch (err: any) {
      setError(err.message || 'Erreur lors du chargement des utilisateurs');
      addNotification({
        type: 'error',
        title: 'Erreur',
        message: 'Impossible de charger les utilisateurs',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1);
    loadUsers();
  };

  const handleRoleFilter = (role: string) => {
    setSelectedRole(role);
    setCurrentPage(1);
  };

  const handleToggleUserStatus = async (userId: string) => {
    try {
      await userService.toggleUserStatus(userId);
      addNotification({
        type: 'success',
        title: 'Succès',
        message: 'Statut de l\'utilisateur mis à jour',
      });
      loadUsers();
    } catch (err: any) {
      addNotification({
        type: 'error',
        title: 'Erreur',
        message: err.message || 'Erreur lors de la mise à jour',
      });
    }
  };

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'admin': return 'danger';
      case 'teacher': return 'primary';
      case 'student': return 'success';
      case 'parent': return 'info';
      default: return 'secondary';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin': return 'Administrateur';
      case 'teacher': return 'Enseignant';
      case 'student': return 'Étudiant';
      case 'parent': return 'Parent';
      default: return role;
    }
  };

  return (
    <div className="users-page">
      <Routes>
        <Route path="/" element={
          <>
            {/* En-tête */}
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h2 className="mb-1">Gestion des utilisateurs</h2>
                <p className="text-muted mb-0">
                  Gérez les comptes utilisateurs de votre établissement
                </p>
              </div>
              <Button 
                variant="primary" 
                onClick={() => navigate('/users/create')}
              >
                <i className="fas fa-plus me-2"></i>
                Nouvel utilisateur
              </Button>
            </div>

            {/* Filtres et recherche */}
            <Card className="mb-4">
              <Card.Body>
                <Row>
                  <Col md={6}>
                    <InputGroup>
                      <Form.Control
                        type="text"
                        placeholder="Rechercher un utilisateur..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                      />
                      <Button variant="outline-secondary" onClick={handleSearch}>
                        <i className="fas fa-search"></i>
                      </Button>
                    </InputGroup>
                  </Col>
                  <Col md={6}>
                    <div className="d-flex gap-2">
                      <Button
                        variant={selectedRole === '' ? 'primary' : 'outline-primary'}
                        size="sm"
                        onClick={() => handleRoleFilter('')}
                      >
                        Tous
                      </Button>
                      <Button
                        variant={selectedRole === 'admin' ? 'danger' : 'outline-danger'}
                        size="sm"
                        onClick={() => handleRoleFilter('admin')}
                      >
                        Admins
                      </Button>
                      <Button
                        variant={selectedRole === 'teacher' ? 'primary' : 'outline-primary'}
                        size="sm"
                        onClick={() => handleRoleFilter('teacher')}
                      >
                        Enseignants
                      </Button>
                      <Button
                        variant={selectedRole === 'student' ? 'success' : 'outline-success'}
                        size="sm"
                        onClick={() => handleRoleFilter('student')}
                      >
                        Étudiants
                      </Button>
                      <Button
                        variant={selectedRole === 'parent' ? 'info' : 'outline-info'}
                        size="sm"
                        onClick={() => handleRoleFilter('parent')}
                      >
                        Parents
                      </Button>
                    </div>
                  </Col>
                </Row>
              </Card.Body>
            </Card>

            {/* Tableau des utilisateurs */}
            <Card>
              <Card.Header>
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">
                    <i className="fas fa-users me-2"></i>
                    Liste des utilisateurs
                  </h5>
                  {users && (
                    <small className="text-muted">
                      {users.total} utilisateur(s) trouvé(s)
                    </small>
                  )}
                </div>
              </Card.Header>
              <Card.Body className="p-0">
                {loading ? (
                  <div className="text-center py-5">
                    <Spinner animation="border" />
                    <div className="mt-2">Chargement des utilisateurs...</div>
                  </div>
                ) : error ? (
                  <Alert variant="danger" className="m-3">
                    {error}
                  </Alert>
                ) : users && users.data.length > 0 ? (
                  <Table responsive hover className="mb-0">
                    <thead>
                      <tr>
                        <th>Nom</th>
                        <th>Email</th>
                        <th>Rôle</th>
                        <th>Statut</th>
                        <th>Créé le</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.data.map((user) => (
                        <tr key={user.id}>
                          <td>
                            <div className="d-flex align-items-center">
                              <i className="fas fa-user-circle text-muted me-2"></i>
                              <div>
                                <div className="fw-semibold">
                                  {user.first_name} {user.last_name}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td>{user.email}</td>
                          <td>
                            <Badge bg={getRoleBadgeVariant(user.role)}>
                              {getRoleLabel(user.role)}
                            </Badge>
                          </td>
                          <td>
                            <Badge bg={user.is_active ? 'success' : 'secondary'}>
                              {user.is_active ? 'Actif' : 'Inactif'}
                            </Badge>
                          </td>
                          <td>
                            {new Date(user.created_at).toLocaleDateString('fr-FR')}
                          </td>
                          <td>
                            <div className="d-flex gap-1">
                              <Button
                                variant="outline-primary"
                                size="sm"
                                onClick={() => navigate(`/users/${user.id}`)}
                              >
                                <i className="fas fa-eye"></i>
                              </Button>
                              <Button
                                variant="outline-secondary"
                                size="sm"
                                onClick={() => navigate(`/users/${user.id}/edit`)}
                              >
                                <i className="fas fa-edit"></i>
                              </Button>
                              <Button
                                variant={user.is_active ? 'outline-warning' : 'outline-success'}
                                size="sm"
                                onClick={() => handleToggleUserStatus(user.id)}
                              >
                                <i className={`fas fa-${user.is_active ? 'ban' : 'check'}`}></i>
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                ) : (
                  <div className="text-center py-5">
                    <i className="fas fa-users text-muted" style={{ fontSize: '3rem' }}></i>
                    <div className="mt-3">
                      <h5>Aucun utilisateur trouvé</h5>
                      <p className="text-muted">
                        {searchTerm || selectedRole 
                          ? 'Aucun utilisateur ne correspond à vos critères de recherche.'
                          : 'Commencez par créer votre premier utilisateur.'
                        }
                      </p>
                    </div>
                  </div>
                )}
              </Card.Body>
              
              {/* Pagination */}
              {users && users.total_pages > 1 && (
                <Card.Footer>
                  <div className="d-flex justify-content-between align-items-center">
                    <small className="text-muted">
                      Page {users.page} sur {users.total_pages}
                    </small>
                    <div className="d-flex gap-1">
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        disabled={users.page <= 1}
                        onClick={() => setCurrentPage(users.page - 1)}
                      >
                        <i className="fas fa-chevron-left"></i>
                      </Button>
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        disabled={users.page >= users.total_pages}
                        onClick={() => setCurrentPage(users.page + 1)}
                      >
                        <i className="fas fa-chevron-right"></i>
                      </Button>
                    </div>
                  </div>
                </Card.Footer>
              )}
            </Card>
          </>
        } />
        
        {/* Routes pour les sous-pages */}
        <Route path="/create" element={<div>Créer un utilisateur</div>} />
        <Route path="/:id" element={<div>Détails utilisateur</div>} />
        <Route path="/:id/edit" element={<div>Modifier utilisateur</div>} />
      </Routes>
    </div>
  );
};

export default UsersPage;
