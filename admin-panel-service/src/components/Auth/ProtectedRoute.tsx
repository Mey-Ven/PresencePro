import React from 'react';
import { Navigate } from 'react-router-dom';
import { Container, Row, Col, Spinner } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
  requiredRoles?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole, 
  requiredRoles 
}) => {
  const { state, hasRole } = useAuth();

  // Afficher le spinner pendant le chargement
  if (state.isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
        <div className="text-center">
          <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
          <div className="mt-3">
            <h5>Chargement...</h5>
            <p className="text-muted">Vérification de l'authentification</p>
          </div>
        </div>
      </div>
    );
  }

  // Rediriger vers la page de connexion si non authentifié
  if (!state.isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Vérifier les rôles requis
  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <Container className="mt-5">
        <Row className="justify-content-center">
          <Col md={6}>
            <div className="text-center">
              <i className="fas fa-ban text-danger" style={{ fontSize: '4rem' }}></i>
              <h3 className="mt-3">Accès refusé</h3>
              <p className="text-muted">
                Vous n'avez pas les permissions nécessaires pour accéder à cette page.
              </p>
              <p className="text-muted">
                Rôle requis: <strong>{requiredRole}</strong>
              </p>
              <p className="text-muted">
                Votre rôle: <strong>{state.user?.role}</strong>
              </p>
            </div>
          </Col>
        </Row>
      </Container>
    );
  }

  // Vérifier les rôles multiples requis
  if (requiredRoles && !requiredRoles.some(role => hasRole(role))) {
    return (
      <Container className="mt-5">
        <Row className="justify-content-center">
          <Col md={6}>
            <div className="text-center">
              <i className="fas fa-ban text-danger" style={{ fontSize: '4rem' }}></i>
              <h3 className="mt-3">Accès refusé</h3>
              <p className="text-muted">
                Vous n'avez pas les permissions nécessaires pour accéder à cette page.
              </p>
              <p className="text-muted">
                Rôles requis: <strong>{requiredRoles.join(', ')}</strong>
              </p>
              <p className="text-muted">
                Votre rôle: <strong>{state.user?.role}</strong>
              </p>
            </div>
          </Col>
        </Row>
      </Container>
    );
  }

  // Afficher le contenu si tout est OK
  return <>{children}</>;
};

export default ProtectedRoute;
