import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap/dist/css/bootstrap.min.css';

// Contexts
import { AuthProvider } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';

// Components
import Layout from './components/Layout/Layout';
import Login from './components/Auth/Login';
import ProtectedRoute from './components/Auth/ProtectedRoute';

// Pages
import Dashboard from './pages/Dashboard';
import UsersPage from './pages/UsersPage';
import AttendancePage from './pages/AttendancePage';
import JustificationsPage from './pages/JustificationsPage';
import StatisticsPage from './pages/StatisticsPage';
import SettingsPage from './pages/SettingsPage';

// Styles
import './App.css';

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <AppProvider>
          <Router>
            <Routes>
              {/* Route de connexion */}
              <Route path="/login" element={<Login />} />
              
              {/* Routes protégées */}
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/users/*" element={<UsersPage />} />
                        <Route path="/attendance" element={<AttendancePage />} />
                        <Route path="/justifications" element={<JustificationsPage />} />
                        <Route path="/statistics" element={<StatisticsPage />} />
                        <Route path="/settings" element={<SettingsPage />} />
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </Router>
          
          {/* Notifications Toast */}
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
          />
        </AppProvider>
      </AuthProvider>
    </div>
  );
}

export default App;
