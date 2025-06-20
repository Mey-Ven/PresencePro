import React, { useState, useEffect } from 'react';
import { Navbar, Nav, Dropdown, Badge, Button, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { useApp } from '../../contexts/AppContext';
import { checkAllServicesHealth } from '../../services/api';

const Header: React.FC = () => {
  const { logout } = useAuth();
  const { state, toggleSidebar, updateServicesHealth } = useApp();
  const [currentTime, setCurrentTime] = useState(new Date());

  // Mettre à jour l'heure toutes les secondes
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Vérifier la santé des services périodiquement
  useEffect(() => {
    const checkServices = async () => {
      try {
        const health = await checkAllServicesHealth();
        updateServicesHealth(health);
      } catch (error) {
        console.error('Erreur lors de la vérification des services:', error);
      }
    };

    // Vérification initiale
    checkServices();

    // Vérification périodique toutes les 30 secondes
    const interval = setInterval(checkServices, 30000);

    return () => clearInterval(interval);
  }, [updateServicesHealth]);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getServicesStatus = () => {
    const services = Object.values(state.servicesHealth);
    const healthyCount = services.filter(Boolean).length;
    const totalCount = services.length;
    
    if (totalCount === 0) return { status: 'unknown', color: 'secondary' };
    if (healthyCount === totalCount) return { status: 'healthy', color: 'success' };
    if (healthyCount === 0) return { status: 'down', color: 'danger' };
    return { status: 'partial', color: 'warning' };
  };

  const servicesStatus = getServicesStatus();

  return (
    <Navbar bg="white" className="border-bottom px-3 py-2 shadow-sm">
      <div className="d-flex align-items-center">
        {/* Toggle Sidebar Button */}
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={toggleSidebar}
          className="me-3"
        >
          <i className="fas fa-bars"></i>
        </Button>

        {/* Page Title */}
        <div className="page-title">
          <h5 className="mb-0 text-dark">Panneau d'administration</h5>
        </div>
      </div>

      <Nav className="ms-auto d-flex align-items-center">
        {/* Date et Heure */}
        <div className="me-4 text-center d-none d-md-block">
          <div className="text-muted small">{formatDate(currentTime)}</div>
          <div className="fw-bold text-primary">{formatTime(currentTime)}</div>
        </div>

        {/* Status des Services */}
        <OverlayTrigger
          placement="bottom"
          overlay={
            <Tooltip>
              <div>
                <strong>État des services:</strong>
                {Object.entries(state.servicesHealth).map(([service, healthy]) => (
                  <div key={service}>
                    <i className={`fas fa-circle text-${healthy ? 'success' : 'danger'} me-1`}></i>
                    {service}: {healthy ? 'OK' : 'KO'}
                  </div>
                ))}
              </div>
            </Tooltip>
          }
        >
          <div className="me-3 cursor-pointer">
            <i className={`fas fa-server text-${servicesStatus.color}`}></i>
            <Badge bg={servicesStatus.color} className="ms-1">
              {Object.values(state.servicesHealth).filter(Boolean).length}/
              {Object.values(state.servicesHealth).length}
            </Badge>
          </div>
        </OverlayTrigger>

        {/* Notifications */}
        <Dropdown className="me-3">
          <Dropdown.Toggle variant="outline-secondary" size="sm" className="position-relative">
            <i className="fas fa-bell"></i>
            {state.notifications.filter(n => !n.read).length > 0 && (
              <Badge 
                bg="danger" 
                pill 
                className="position-absolute top-0 start-100 translate-middle"
                style={{ fontSize: '0.6rem' }}
              >
                {state.notifications.filter(n => !n.read).length}
              </Badge>
            )}
          </Dropdown.Toggle>

          <Dropdown.Menu align="end" style={{ minWidth: '300px' }}>
            <Dropdown.Header>
              <i className="fas fa-bell me-2"></i>
              Notifications
            </Dropdown.Header>
            
            {state.notifications.length === 0 ? (
              <Dropdown.Item disabled>
                <div className="text-center text-muted py-2">
                  <i className="fas fa-inbox"></i>
                  <div>Aucune notification</div>
                </div>
              </Dropdown.Item>
            ) : (
              state.notifications.slice(0, 5).map((notification) => (
                <Dropdown.Item key={notification.id} className={!notification.read ? 'bg-light' : ''}>
                  <div className="d-flex">
                    <div className="me-2">
                      <i className={`fas fa-${
                        notification.type === 'success' ? 'check-circle text-success' :
                        notification.type === 'error' ? 'exclamation-circle text-danger' :
                        notification.type === 'warning' ? 'exclamation-triangle text-warning' :
                        'info-circle text-info'
                      }`}></i>
                    </div>
                    <div className="flex-grow-1">
                      <div className="fw-semibold">{notification.title}</div>
                      <div className="text-muted small">{notification.message}</div>
                      <div className="text-muted small">
                        {new Date(notification.timestamp).toLocaleString('fr-FR')}
                      </div>
                    </div>
                  </div>
                </Dropdown.Item>
              ))
            )}
            
            {state.notifications.length > 5 && (
              <Dropdown.Divider />
            )}
            
            {state.notifications.length > 0 && (
              <Dropdown.Item className="text-center">
                <small>Voir toutes les notifications</small>
              </Dropdown.Item>
            )}
          </Dropdown.Menu>
        </Dropdown>

        {/* Menu Utilisateur */}
        <Dropdown>
          <Dropdown.Toggle variant="outline-primary" size="sm">
            <i className="fas fa-user-circle me-2"></i>
            Mon compte
          </Dropdown.Toggle>

          <Dropdown.Menu align="end">
            <Dropdown.Header>
              <div className="fw-semibold">Mon profil</div>
              <small className="text-muted">Connecté en tant qu'administrateur</small>
            </Dropdown.Header>
            
            <Dropdown.Divider />
            
            <Dropdown.Item>
              <i className="fas fa-user me-2"></i>
              Profil
            </Dropdown.Item>
            
            <Dropdown.Item>
              <i className="fas fa-cog me-2"></i>
              Paramètres
            </Dropdown.Item>
            
            <Dropdown.Item>
              <i className="fas fa-question-circle me-2"></i>
              Aide
            </Dropdown.Item>
            
            <Dropdown.Divider />
            
            <Dropdown.Item onClick={handleLogout} className="text-danger">
              <i className="fas fa-sign-out-alt me-2"></i>
              Déconnexion
            </Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </Nav>
    </Navbar>
  );
};

export default Header;
