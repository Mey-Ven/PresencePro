import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Header from './Header';
import Sidebar from './Sidebar';

// Interface pour les props du layout
interface LayoutProps {
  title?: string;
  children?: React.ReactNode;
}

// Composant Layout principal
const Layout: React.FC<LayoutProps> = ({ title, children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Gérer l'ouverture/fermeture du menu mobile
  const handleMenuToggle = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Fermer le menu mobile
  const handleMenuClose = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Sidebar moderne */}
      <Sidebar isOpen={isMobileMenuOpen} onClose={handleMenuClose} />

      {/* Contenu principal */}
      <div className="lg:ml-64 transition-all duration-300">
        {/* Header moderne */}
        <Header
          title={title}
          onMenuToggle={handleMenuToggle}
          isMobileMenuOpen={isMobileMenuOpen}
        />

        {/* Zone de contenu moderne */}
        <main className="flex-1">
          <div className="py-8">
            <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-8">
              <div className="animate-fade-in-up">
                {children || <Outlet />}
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Toast notifications modernes */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 5000,
          style: {
            background: 'linear-gradient(145deg, #ffffff 0%, #fafbfc 100%)',
            color: '#1f2937',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            padding: '16px 20px',
            fontSize: '14px',
            fontWeight: '500',
            backdropFilter: 'blur(10px)',
          },
          success: {
            style: {
              background: 'linear-gradient(145deg, #ecfdf5 0%, #d1fae5 100%)',
              border: '1px solid #10b981',
              color: '#047857',
            },
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            style: {
              background: 'linear-gradient(145deg, #fef2f2 0%, #fee2e2 100%)',
              border: '1px solid #ef4444',
              color: '#dc2626',
            },
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
          loading: {
            style: {
              background: 'linear-gradient(145deg, #eff6ff 0%, #dbeafe 100%)',
              border: '1px solid #3b82f6',
              color: '#1d4ed8',
            },
            iconTheme: {
              primary: '#3b82f6',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
};

// Layout spécialisé pour les pages d'authentification
export const AuthLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {children}

      {/* Toast notifications pour les pages d'auth */}
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#374151',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem',
            padding: '16px',
          },
        }}
      />
    </div>
  );
};

// Layout pour les pages d'erreur
export const ErrorLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-lg">
        {children}
      </div>
    </div>
  );
};

// Layout pour les pages de chargement
export const LoadingLayout: React.FC<{ message?: string }> = ({ 
  message = 'Chargement...' 
}) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-primary-600 rounded-lg flex items-center justify-center mb-4 mx-auto">
          <span className="text-white font-bold text-2xl">P</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">PresencePro</h2>
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
          <span className="text-gray-600">{message}</span>
        </div>
      </div>
    </div>
  );
};

// Layout pour les modales
export const ModalLayout: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}> = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'md' 
}) => {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    '2xl': 'max-w-6xl',
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Overlay */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />
        
        {/* Modal */}
        <div className={`relative bg-white rounded-lg shadow-xl w-full ${sizeClasses[size]}`}>
          {title && (
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">{title}</h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500 focus:outline-none focus:text-gray-500"
              >
                <span className="sr-only">Fermer</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}
          
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

// Layout pour les pages vides (états vides)
export const EmptyStateLayout: React.FC<{
  icon?: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}> = ({ 
  icon: Icon, 
  title, 
  description, 
  action 
}) => {
  return (
    <div className="text-center py-12">
      {Icon && (
        <Icon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
      )}
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6 max-w-sm mx-auto">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="btn-primary"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};

export default Layout;
