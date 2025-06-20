import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { LoginCredentials } from '../../types';

const Login: React.FC = () => {
  const { state, login } = useAuth();
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: '',
    password: '',
  });
  const [error, setError] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Rediriger si déjà connecté
  if (state.isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  // Gérer la soumission du formulaire
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await login(credentials);
    } catch (err: any) {
      setError(err.message || 'Erreur de connexion');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Gérer les changements dans les champs
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="login-page" style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center'
    }}>
      <Container>
        <Row className="justify-content-center">
          <Col md={6} lg={4}>
            <Card className="shadow-lg border-0" style={{ borderRadius: '15px' }}>
              <Card.Body className="p-5">
                <div className="text-center mb-4">
                  <h2 className="fw-bold text-primary mb-2">PresencePro</h2>
                  <p className="text-muted">Panneau d'administration</p>
                </div>

                {error && (
                  <Alert variant="danger" className="mb-4">
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    {error}
                  </Alert>
                )}

                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      <i className="fas fa-envelope me-2"></i>
                      Email
                    </Form.Label>
                    <Form.Control
                      type="email"
                      name="email"
                      value={credentials.email}
                      onChange={handleChange}
                      placeholder="Entrez votre email"
                      required
                      disabled={isSubmitting}
                      style={{ borderRadius: '10px', padding: '12px' }}
                    />
                  </Form.Group>

                  <Form.Group className="mb-4">
                    <Form.Label>
                      <i className="fas fa-lock me-2"></i>
                      Mot de passe
                    </Form.Label>
                    <Form.Control
                      type="password"
                      name="password"
                      value={credentials.password}
                      onChange={handleChange}
                      placeholder="Entrez votre mot de passe"
                      required
                      disabled={isSubmitting}
                      style={{ borderRadius: '10px', padding: '12px' }}
                    />
                  </Form.Group>

                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    className="w-100 mb-3"
                    disabled={isSubmitting}
                    style={{ 
                      borderRadius: '10px',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      border: 'none',
                      padding: '12px'
                    }}
                  >
                    {isSubmitting ? (
                      <>
                        <Spinner
                          as="span"
                          animation="border"
                          size="sm"
                          role="status"
                          aria-hidden="true"
                          className="me-2"
                        />
                        Connexion...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-sign-in-alt me-2"></i>
                        Se connecter
                      </>
                    )}
                  </Button>
                </Form>

                <div className="text-center">
                  <small className="text-muted">
                    Mot de passe oublié ? 
                    <a href="#" className="text-primary ms-1">
                      Cliquez ici
                    </a>
                  </small>
                </div>

                {/* Comptes de démonstration */}
                <div className="mt-4 pt-4 border-top">
                  <small className="text-muted d-block text-center mb-2">
                    Comptes de démonstration :
                  </small>
                  <div className="demo-accounts">
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      className="w-100 mb-2"
                      onClick={() => setCredentials({
                        email: 'admin@presencepro.com',
                        password: 'admin123'
                      })}
                      disabled={isSubmitting}
                    >
                      <i className="fas fa-user-shield me-2"></i>
                      Admin
                    </Button>
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      className="w-100"
                      onClick={() => setCredentials({
                        email: 'teacher@presencepro.com',
                        password: 'teacher123'
                      })}
                      disabled={isSubmitting}
                    >
                      <i className="fas fa-chalkboard-teacher me-2"></i>
                      Enseignant
                    </Button>
                  </div>
                </div>
              </Card.Body>
            </Card>

            {/* Informations sur les services */}
            <div className="text-center mt-4">
              <small className="text-white-50">
                <i className="fas fa-info-circle me-1"></i>
                Système de gestion des présences scolaires
              </small>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default Login;
