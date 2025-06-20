import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AdminRoute, TeacherRoute, StudentRoute, ParentRoute } from './components/common/PrivateRoute';

// Pages d'authentification
import LoginPage from './pages/auth/LoginPage';

// Pages Admin
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminAttendance from './pages/admin/AdminAttendance';
import AdminJustifications from './pages/admin/AdminJustifications';
import AdminActivity from './pages/admin/AdminActivity';
import AdminCourses from './pages/admin/AdminCourses';
import AdminMessaging from './pages/admin/AdminMessaging';
import AdminStatistics from './pages/admin/AdminStatistics';
import AdminSettings from './pages/admin/AdminSettings';

// Pages Teacher
import TeacherDashboard from './pages/teacher/TeacherDashboard';
import TeacherCourses from './pages/teacher/TeacherCourses';
import TeacherStudents from './pages/teacher/TeacherStudents';
import TeacherAttendance from './pages/teacher/TeacherAttendance';
import TeacherAbsences from './pages/teacher/TeacherAbsences';
import TeacherClasses from './pages/teacher/TeacherClasses';
import TeacherJustifications from './pages/teacher/TeacherJustifications';
import TeacherClassesList from './pages/teacher/TeacherClassesList';
import TeacherStatistics from './pages/teacher/TeacherStatistics';

// Pages Student
import StudentDashboard from './pages/student/StudentDashboard';
import StudentCourses from './pages/student/StudentCourses';
import StudentAttendance from './pages/student/StudentAttendance';
import StudentJustify from './pages/student/StudentJustify';
import StudentSchedule from './pages/student/StudentSchedule';
import StudentStatistics from './pages/student/StudentStatistics';

// Pages Parent
import ParentDashboard from './pages/parent/ParentDashboard';
import ParentAttendance from './pages/parent/ParentAttendance';
import ParentJustifications from './pages/parent/ParentJustifications';
import ParentMessaging from './pages/parent/ParentMessaging';
import ParentNotifications from './pages/parent/ParentNotifications';
import ParentSchedule from './pages/parent/ParentSchedule';

// Page de test
import TestAuth from './pages/TestAuth';

// Composant pour rediriger vers le bon dashboard selon le rôle
const DashboardRedirect: React.FC = () => {
  const { isAuthenticated, user, isLoading } = useAuth();

  // Attendre que l'authentification soit initialisée
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  // Si pas connecté, rediriger vers la page de connexion
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  // Rediriger selon le rôle de l'utilisateur
  switch (user.role) {
    case 'admin':
      return <Navigate to="/admin/dashboard" replace />;
    case 'teacher':
      return <Navigate to="/teacher/dashboard" replace />;
    case 'student':
      return <Navigate to="/student/dashboard" replace />;
    case 'parent':
      return <Navigate to="/parent/dashboard" replace />;
    default:
      return <Navigate to="/login" replace />;
  }
};

// Composant principal de l'application
function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <Routes>
            {/* Routes publiques */}
            <Route path="/login" element={<LoginPage />} />

            {/* Page de test d'authentification */}
            <Route path="/test-auth" element={<TestAuth />} />

            {/* Redirection par défaut */}
            <Route path="/" element={<DashboardRedirect />} />
            <Route path="/dashboard" element={<DashboardRedirect />} />

            {/* Routes Admin */}
            <Route path="/admin/dashboard" element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            } />
            <Route path="/admin/users" element={
              <AdminRoute>
                <AdminUsers />
              </AdminRoute>
            } />
            <Route path="/admin/attendance" element={
              <AdminRoute>
                <AdminAttendance />
              </AdminRoute>
            } />
            <Route path="/admin/justifications" element={
              <AdminRoute>
                <AdminJustifications />
              </AdminRoute>
            } />
            <Route path="/admin/activity" element={
              <AdminRoute>
                <AdminActivity />
              </AdminRoute>
            } />
            <Route path="/admin/courses" element={
              <AdminRoute>
                <AdminCourses />
              </AdminRoute>
            } />
            <Route path="/admin/messaging" element={
              <AdminRoute>
                <AdminMessaging />
              </AdminRoute>
            } />
            <Route path="/admin/statistics" element={
              <AdminRoute>
                <AdminStatistics />
              </AdminRoute>
            } />
            <Route path="/admin/settings" element={
              <AdminRoute>
                <AdminSettings />
              </AdminRoute>
            } />

            {/* Routes Teacher */}
            <Route path="/teacher/dashboard" element={
              <TeacherRoute>
                <TeacherDashboard />
              </TeacherRoute>
            } />
            <Route path="/teacher/courses" element={
              <TeacherRoute>
                <TeacherCourses />
              </TeacherRoute>
            } />
            <Route path="/teacher/students" element={
              <TeacherRoute>
                <TeacherStudents />
              </TeacherRoute>
            } />
            <Route path="/teacher/attendance" element={
              <TeacherRoute>
                <TeacherAttendance />
              </TeacherRoute>
            } />
            <Route path="/teacher/absences" element={
              <TeacherRoute>
                <TeacherAbsences />
              </TeacherRoute>
            } />
            <Route path="/teacher/classes/:classId" element={
              <TeacherRoute>
                <TeacherClasses />
              </TeacherRoute>
            } />
            <Route path="/teacher/justifications" element={
              <TeacherRoute>
                <TeacherJustifications />
              </TeacherRoute>
            } />
            <Route path="/teacher/classes" element={
              <TeacherRoute>
                <TeacherClassesList />
              </TeacherRoute>
            } />
            <Route path="/teacher/statistics" element={
              <TeacherRoute>
                <TeacherStatistics />
              </TeacherRoute>
            } />

            {/* Routes Student */}
            <Route path="/student/dashboard" element={
              <StudentRoute>
                <StudentDashboard />
              </StudentRoute>
            } />
            <Route path="/student/courses" element={
              <StudentRoute>
                <StudentCourses />
              </StudentRoute>
            } />
            <Route path="/student/attendance" element={
              <StudentRoute>
                <StudentAttendance />
              </StudentRoute>
            } />
            <Route path="/student/justify" element={
              <StudentRoute>
                <StudentJustify />
              </StudentRoute>
            } />
            <Route path="/student/schedule" element={
              <StudentRoute>
                <StudentSchedule />
              </StudentRoute>
            } />
            <Route path="/student/statistics" element={
              <StudentRoute>
                <StudentStatistics />
              </StudentRoute>
            } />

            {/* Routes Parent */}
            <Route path="/parent/dashboard" element={
              <ParentRoute>
                <ParentDashboard />
              </ParentRoute>
            } />
            <Route path="/parent/attendance" element={
              <ParentRoute>
                <ParentAttendance />
              </ParentRoute>
            } />
            <Route path="/parent/justifications" element={
              <ParentRoute>
                <ParentJustifications />
              </ParentRoute>
            } />
            <Route path="/parent/messaging" element={
              <ParentRoute>
                <ParentMessaging />
              </ParentRoute>
            } />
            <Route path="/parent/notifications" element={
              <ParentRoute>
                <ParentNotifications />
              </ParentRoute>
            } />
            <Route path="/parent/schedule" element={
              <ParentRoute>
                <ParentSchedule />
              </ParentRoute>
            } />

            {/* Route 404 */}
            <Route path="*" element={
              <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900">404</h1>
                  <p className="text-gray-600">Page non trouvée</p>
                </div>
              </div>
            } />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
