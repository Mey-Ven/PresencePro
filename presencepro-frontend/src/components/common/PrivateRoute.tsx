import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';

// Interface pour les props du composant
interface PrivateRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
  requireAuth?: boolean;
  fallbackPath?: string;
}

// Composant pour protéger les routes
const PrivateRoute: React.FC<PrivateRouteProps> = ({
  children,
  allowedRoles = [],
  requireAuth = true,
  fallbackPath = '/login',
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Afficher le spinner pendant le chargement
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Rediriger vers la page de connexion si non authentifié
  if (requireAuth && !isAuthenticated) {
    return (
      <Navigate 
        to={fallbackPath} 
        state={{ from: location.pathname }} 
        replace 
      />
    );
  }

  // Vérifier les rôles autorisés
  if (allowedRoles.length > 0 && user) {
    const hasRequiredRole = allowedRoles.includes(user.role);
    
    if (!hasRequiredRole) {
      // Rediriger vers une page d'erreur ou le dashboard selon le rôle
      const redirectPath = getRedirectPathByRole(user.role);
      return <Navigate to={redirectPath} replace />;
    }
  }

  // Rendre le composant enfant si toutes les conditions sont remplies
  return <>{children}</>;
};

// Fonction pour déterminer la redirection selon le rôle
const getRedirectPathByRole = (role: string): string => {
  switch (role) {
    case 'admin':
      return '/admin/dashboard';
    case 'teacher':
      return '/teacher/dashboard';
    case 'student':
      return '/student/dashboard';
    case 'parent':
      return '/parent/dashboard';
    default:
      return '/unauthorized';
  }
};

// Composant spécialisé pour les routes admin
export const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <PrivateRoute allowedRoles={['admin']}>
    {children}
  </PrivateRoute>
);

// Composant spécialisé pour les routes enseignant
export const TeacherRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <PrivateRoute allowedRoles={['admin', 'teacher']}>
    {children}
  </PrivateRoute>
);

// Composant spécialisé pour les routes étudiant
export const StudentRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <PrivateRoute allowedRoles={['admin', 'teacher', 'student']}>
    {children}
  </PrivateRoute>
);

// Composant spécialisé pour les routes parent
export const ParentRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <PrivateRoute allowedRoles={['admin', 'parent']}>
    {children}
  </PrivateRoute>
);

// Composant pour les routes publiques (pas d'authentification requise)
export const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <PrivateRoute requireAuth={false}>
    {children}
  </PrivateRoute>
);

// Hook pour rediriger automatiquement selon le rôle
export const useRoleBasedRedirect = () => {
  const { user, isAuthenticated } = useAuth();
  
  const getDefaultPath = (): string => {
    if (!isAuthenticated || !user) {
      return '/login';
    }
    
    return getRedirectPathByRole(user.role);
  };
  
  return { getDefaultPath };
};

export default PrivateRoute;
