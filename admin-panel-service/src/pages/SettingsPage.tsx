import React, { useState } from 'react';
import { Row, Col, Card, Button, Form, Alert, Badge } from 'react-bootstrap';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';

const SettingsPage: React.FC = () => {
  const { state: appState, updateSettings, updateServicesHealth } = useApp();
  const { state: authState } = useAuth();
  const [activeTab, setActiveTab] = useState('general');
  const [saveMessage, setSaveMessage] = useState<string>('');

  const handleSettingsChange = (key: string, value: any) => {
    updateSettings({ [key]: value });
    setSaveMessage('Paramètres sauvegardés automatiquement');
    setTimeout(() => setSaveMessage(''), 3000);
  };

  const checkServicesHealth = async () => {
    // Simuler la vérification des services
    const mockHealth = {
      auth: true,
      user: true,
      course: true,
      face_recognition: false,
      attendance: true,
      justification: true,
      messaging: true,
      notification: false,
      statistics: true,
    };
    
    updateServicesHealth(mockHealth);
  };

  const renderGeneralSettings = () => (
    <Card>
      <Card.Header>
        <h5 className="mb-0">
          <i className="fas fa-cog me-2"></i>
          Paramètres généraux
        </h5>
      </Card.Header>
      <Card.Body>
        <Form>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Thème</Form.Label>
                <Form.Select
                  value={appState.settings.theme}
                  onChange={(e) => handleSettingsChange('theme', e.target.value)}
                >
                  <option value="light">Clair</option>
                  <option value="dark">Sombre</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Langue</Form.Label>
                <Form.Select
                  value={appState.settings.language}
                  onChange={(e) => handleSettingsChange('language', e.target.value)}
                >
                  <option value="fr">Français</option>
                  <option value="en">English</option>
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>
          
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Intervalle de rafraîchissement automatique (secondes)</Form.Label>
                <Form.Control
                  type="number"
                  min="10"
                  max="300"
                  value={appState.settings.auto_refresh_interval / 1000}
                  onChange={(e) => handleSettingsChange('auto_refresh_interval', parseInt(e.target.value) * 1000)}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Check
                  type="switch"
                  id="notifications-switch"
                  label="Activer les notifications"
                  checked={appState.settings.notifications_enabled}
                  onChange={(e) => handleSettingsChange('notifications_enabled', e.target.checked)}
                />
              </Form.Group>
            </Col>
          </Row>
        </Form>
      </Card.Body>
    </Card>
  );

  const renderServicesStatus = () => (
    <Card>
      <Card.Header>
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">
            <i className="fas fa-server me-2"></i>
            État des services
          </h5>
          <Button variant="outline-primary" size="sm" onClick={checkServicesHealth}>
            <i className="fas fa-sync me-2"></i>
            Vérifier
          </Button>
        </div>
      </Card.Header>
      <Card.Body>
        <Row>
          {Object.entries(appState.servicesHealth).map(([service, healthy]) => (
            <Col md={6} lg={4} key={service} className="mb-3">
              <div className="d-flex align-items-center justify-content-between p-3 border rounded">
                <div>
                  <div className="fw-semibold">{service.replace('_', '-')}-service</div>
                  <small className="text-muted">Port: 800{Object.keys(appState.servicesHealth).indexOf(service) + 1}</small>
                </div>
                <Badge bg={healthy ? 'success' : 'danger'}>
                  <i className={`fas fa-${healthy ? 'check' : 'times'} me-1`}></i>
                  {healthy ? 'OK' : 'KO'}
                </Badge>
              </div>
            </Col>
          ))}
        </Row>
      </Card.Body>
    </Card>
  );

  const renderUserProfile = () => (
    <Card>
      <Card.Header>
        <h5 className="mb-0">
          <i className="fas fa-user me-2"></i>
          Profil utilisateur
        </h5>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={4} className="text-center">
            <div className="mb-3">
              <i className="fas fa-user-circle text-muted" style={{ fontSize: '5rem' }}></i>
            </div>
            <Button variant="outline-primary" size="sm">
              <i className="fas fa-camera me-2"></i>
              Changer la photo
            </Button>
          </Col>
          <Col md={8}>
            <Form>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Prénom</Form.Label>
                    <Form.Control
                      type="text"
                      value={authState.user?.first_name || ''}
                      readOnly
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Nom</Form.Label>
                    <Form.Control
                      type="text"
                      value={authState.user?.last_name || ''}
                      readOnly
                    />
                  </Form.Group>
                </Col>
              </Row>
              
              <Form.Group className="mb-3">
                <Form.Label>Email</Form.Label>
                <Form.Control
                  type="email"
                  value={authState.user?.email || ''}
                  readOnly
                />
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Rôle</Form.Label>
                <Form.Control
                  type="text"
                  value={authState.user?.role || ''}
                  readOnly
                />
              </Form.Group>
              
              <div className="d-flex gap-2">
                <Button variant="primary">
                  <i className="fas fa-edit me-2"></i>
                  Modifier le profil
                </Button>
                <Button variant="outline-secondary">
                  <i className="fas fa-key me-2"></i>
                  Changer le mot de passe
                </Button>
              </div>
            </Form>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );

  const renderSystemInfo = () => (
    <Card>
      <Card.Header>
        <h5 className="mb-0">
          <i className="fas fa-info-circle me-2"></i>
          Informations système
        </h5>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={6}>
            <table className="table table-borderless">
              <tbody>
                <tr>
                  <td><strong>Version de l'application:</strong></td>
                  <td>1.0.0</td>
                </tr>
                <tr>
                  <td><strong>Environnement:</strong></td>
                  <td><Badge bg="success">Production</Badge></td>
                </tr>
                <tr>
                  <td><strong>Base de données:</strong></td>
                  <td>PostgreSQL 14.2</td>
                </tr>
                <tr>
                  <td><strong>Cache:</strong></td>
                  <td>Redis 6.2</td>
                </tr>
              </tbody>
            </table>
          </Col>
          <Col md={6}>
            <table className="table table-borderless">
              <tbody>
                <tr>
                  <td><strong>Dernière sauvegarde:</strong></td>
                  <td>20/06/2025 02:00</td>
                </tr>
                <tr>
                  <td><strong>Espace disque utilisé:</strong></td>
                  <td>2.3 GB / 10 GB</td>
                </tr>
                <tr>
                  <td><strong>Utilisateurs connectés:</strong></td>
                  <td>12</td>
                </tr>
                <tr>
                  <td><strong>Uptime:</strong></td>
                  <td>15 jours, 3 heures</td>
                </tr>
              </tbody>
            </table>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );

  return (
    <div className="settings-page">
      {/* En-tête */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="mb-1">Paramètres</h2>
          <p className="text-muted mb-0">
            Configurez votre application et gérez vos préférences
          </p>
        </div>
        {saveMessage && (
          <Alert variant="success" className="mb-0 py-2">
            <i className="fas fa-check me-2"></i>
            {saveMessage}
          </Alert>
        )}
      </div>

      <Row>
        {/* Menu de navigation */}
        <Col md={3}>
          <Card>
            <Card.Body className="p-0">
              <div className="list-group list-group-flush">
                <button
                  className={`list-group-item list-group-item-action ${activeTab === 'general' ? 'active' : ''}`}
                  onClick={() => setActiveTab('general')}
                >
                  <i className="fas fa-cog me-2"></i>
                  Général
                </button>
                <button
                  className={`list-group-item list-group-item-action ${activeTab === 'profile' ? 'active' : ''}`}
                  onClick={() => setActiveTab('profile')}
                >
                  <i className="fas fa-user me-2"></i>
                  Profil
                </button>
                <button
                  className={`list-group-item list-group-item-action ${activeTab === 'services' ? 'active' : ''}`}
                  onClick={() => setActiveTab('services')}
                >
                  <i className="fas fa-server me-2"></i>
                  Services
                </button>
                <button
                  className={`list-group-item list-group-item-action ${activeTab === 'system' ? 'active' : ''}`}
                  onClick={() => setActiveTab('system')}
                >
                  <i className="fas fa-info-circle me-2"></i>
                  Système
                </button>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Contenu */}
        <Col md={9}>
          {activeTab === 'general' && renderGeneralSettings()}
          {activeTab === 'profile' && renderUserProfile()}
          {activeTab === 'services' && renderServicesStatus()}
          {activeTab === 'system' && renderSystemInfo()}
        </Col>
      </Row>
    </div>
  );
};

export default SettingsPage;
