import React from 'react';
import { Nav, Navbar } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useApp } from '../../contexts/AppContext';

const Sidebar: React.FC = () => {
  const { state: authState } = useAuth();
  const { state: appState } = useApp();
  const location = useLocation();

  const menuItems = [
    {
      path: '/dashboard',
      icon: 'fas fa-tachometer-alt',
      label: 'Tableau de bord',
      roles: ['admin', 'teacher'],
    },
    {
      path: '/users',
      icon: 'fas fa-users',
      label: 'Utilisateurs',
      roles: ['admin'],
    },
    {
      path: '/attendance',
      icon: 'fas fa-calendar-check',
      label: 'Présences',
      roles: ['admin', 'teacher'],
    },
    {
      path: '/justifications',
      icon: 'fas fa-file-medical',
      label: 'Justifications',
      roles: ['admin', 'teacher'],
    },
    {
      path: '/statistics',
      icon: 'fas fa-chart-bar',
      label: 'Statistiques',
      roles: ['admin', 'teacher'],
    },
    {
      path: '/settings',
      icon: 'fas fa-cog',
      label: 'Paramètres',
      roles: ['admin'],
    },
  ];

  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(authState.user?.role || '')
  );

  return (
    <div className="sidebar">
      <Navbar className="flex-column h-100 p-0">
        {/* Logo */}
        <div className="sidebar-header p-3 w-100 text-center">
          {!appState.sidebarCollapsed ? (
            <>
              <h4 className="text-white mb-0 fw-bold">PresencePro</h4>
              <small className="text-white-50">Admin Panel</small>
            </>
          ) : (
            <i className="fas fa-graduation-cap text-white" style={{ fontSize: '1.5rem' }}></i>
          )}
        </div>

        {/* Navigation */}
        <Nav className="sidebar-nav flex-column w-100 px-2">
          {filteredMenuItems.map((item) => (
            <Nav.Item key={item.path} className="w-100">
              <Nav.Link
                as={Link}
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                title={appState.sidebarCollapsed ? item.label : ''}
              >
                <i className={item.icon}></i>
                {!appState.sidebarCollapsed && (
                  <span className="ms-2">{item.label}</span>
                )}
              </Nav.Link>
            </Nav.Item>
          ))}
        </Nav>

        {/* User Info */}
        {!appState.sidebarCollapsed && (
          <div className="sidebar-footer p-3 w-100 mt-auto">
            <div className="user-info text-center">
              <div className="user-avatar mb-2">
                <i className="fas fa-user-circle text-white" style={{ fontSize: '2rem' }}></i>
              </div>
              <div className="user-details">
                <div className="text-white fw-semibold">
                  {authState.user?.first_name} {authState.user?.last_name}
                </div>
                <small className="text-white-50">
                  {authState.user?.role === 'admin' && 'Administrateur'}
                  {authState.user?.role === 'teacher' && 'Enseignant'}
                  {authState.user?.role === 'student' && 'Étudiant'}
                  {authState.user?.role === 'parent' && 'Parent'}
                </small>
              </div>
            </div>
          </div>
        )}
      </Navbar>
    </div>
  );
};

export default Sidebar;
