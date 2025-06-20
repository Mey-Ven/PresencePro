import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Composant temporaire pour le dashboard
const Dashboard = () => (
  <div className="container-fluid p-4">
    <h2>Tableau de bord</h2>
    <div className="row">
      <div className="col-md-3">
        <div className="card stat-card">
          <div className="card-body text-center">
            <h3>150</h3>
            <p>Étudiants</p>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card stat-card">
          <div className="card-body text-center">
            <h3>92%</h3>
            <p>Taux de présence</p>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card stat-card">
          <div className="card-body text-center">
            <h3>12</h3>
            <p>Absents aujourd'hui</p>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card stat-card">
          <div className="card-body text-center">
            <h3>5</h3>
            <p>Classes</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Composant temporaire pour les utilisateurs
const UsersPage = () => (
  <div className="container-fluid p-4">
    <h2>Gestion des utilisateurs</h2>
    <div className="card">
      <div className="card-body">
        <p>Interface de gestion des utilisateurs en cours de développement...</p>
      </div>
    </div>
  </div>
);

// Layout simple
const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="d-flex">
    <div className="sidebar bg-primary text-white" style={{ width: '250px', minHeight: '100vh' }}>
      <div className="p-3">
        <h4>PresencePro</h4>
        <nav className="nav flex-column mt-4">
          <a href="/dashboard" className="nav-link text-white">
            <i className="fas fa-tachometer-alt me-2"></i>
            Tableau de bord
          </a>
          <a href="/users" className="nav-link text-white">
            <i className="fas fa-users me-2"></i>
            Utilisateurs
          </a>
          <a href="/attendance" className="nav-link text-white">
            <i className="fas fa-calendar-check me-2"></i>
            Présences
          </a>
        </nav>
      </div>
    </div>
    <div className="flex-grow-1">
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <div className="container-fluid">
          <span className="navbar-brand">Admin Panel</span>
          <div className="navbar-nav ms-auto">
            <span className="nav-link">Administrateur</span>
          </div>
        </div>
      </nav>
      {children}
    </div>
  </div>
);

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={
            <Layout>
              <Dashboard />
            </Layout>
          } />
          <Route path="/users" element={
            <Layout>
              <UsersPage />
            </Layout>
          } />
          <Route path="/attendance" element={
            <Layout>
              <div className="container-fluid p-4">
                <h2>Gestion des présences</h2>
                <div className="card">
                  <div className="card-body">
                    <p>Interface de gestion des présences en cours de développement...</p>
                  </div>
                </div>
              </div>
            </Layout>
          } />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
