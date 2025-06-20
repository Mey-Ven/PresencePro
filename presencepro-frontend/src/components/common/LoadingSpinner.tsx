import React from 'react';
import clsx from 'clsx';

// Interface pour les props du composant
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white' | 'gray';
  className?: string;
  text?: string;
  overlay?: boolean;
}

// Composant de spinner de chargement
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className,
  text,
  overlay = false,
}) => {
  // Classes CSS pour les différentes tailles
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  // Classes CSS pour les différentes couleurs
  const colorClasses = {
    primary: 'text-primary-600',
    secondary: 'text-secondary-600',
    white: 'text-white',
    gray: 'text-gray-600',
  };

  // Classes CSS pour le texte selon la taille
  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
  };

  // Composant spinner SVG
  const SpinnerSVG = () => (
    <svg
      className={clsx(
        'animate-spin',
        sizeClasses[size],
        colorClasses[color],
        className
      )}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );

  // Contenu du spinner avec texte optionnel
  const SpinnerContent = () => (
    <div className="flex flex-col items-center justify-center space-y-2">
      <SpinnerSVG />
      {text && (
        <p className={clsx(
          'font-medium',
          textSizeClasses[size],
          colorClasses[color]
        )}>
          {text}
        </p>
      )}
    </div>
  );

  // Si overlay est activé, afficher le spinner en overlay
  if (overlay) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 shadow-lg">
          <SpinnerContent />
        </div>
      </div>
    );
  }

  // Affichage normal du spinner
  return <SpinnerContent />;
};

// Composant de spinner pour les boutons
export const ButtonSpinner: React.FC<{ className?: string }> = ({ className }) => (
  <svg
    className={clsx('animate-spin w-4 h-4', className)}
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    />
  </svg>
);

// Composant de spinner pour les pages
export const PageSpinner: React.FC<{ text?: string }> = ({ text = 'Chargement...' }) => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <LoadingSpinner size="lg" text={text} />
  </div>
);

// Composant de spinner pour les cartes/sections
export const CardSpinner: React.FC<{ text?: string; className?: string }> = ({ 
  text, 
  className 
}) => (
  <div className={clsx('flex items-center justify-center p-8', className)}>
    <LoadingSpinner size="md" text={text} />
  </div>
);

// Composant de spinner en ligne
export const InlineSpinner: React.FC<{ className?: string }> = ({ className }) => (
  <LoadingSpinner size="sm" className={clsx('inline-block', className)} />
);

// Composant de skeleton loader pour les listes
export const SkeletonLoader: React.FC<{ 
  lines?: number; 
  className?: string;
  avatar?: boolean;
}> = ({ 
  lines = 3, 
  className,
  avatar = false 
}) => (
  <div className={clsx('animate-pulse', className)}>
    <div className="flex space-x-4">
      {avatar && (
        <div className="rounded-full bg-gray-300 h-10 w-10"></div>
      )}
      <div className="flex-1 space-y-2 py-1">
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={clsx(
              'h-4 bg-gray-300 rounded',
              index === lines - 1 ? 'w-3/4' : 'w-full'
            )}
          ></div>
        ))}
      </div>
    </div>
  </div>
);

// Composant de skeleton pour les cartes
export const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={clsx('animate-pulse bg-white rounded-lg shadow p-6', className)}>
    <div className="flex items-center space-x-4">
      <div className="rounded-full bg-gray-300 h-12 w-12"></div>
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-gray-300 rounded w-3/4"></div>
        <div className="h-4 bg-gray-300 rounded w-1/2"></div>
      </div>
    </div>
    <div className="mt-4 space-y-2">
      <div className="h-4 bg-gray-300 rounded"></div>
      <div className="h-4 bg-gray-300 rounded w-5/6"></div>
    </div>
  </div>
);

// Composant de skeleton pour les tableaux
export const TableSkeleton: React.FC<{ 
  rows?: number; 
  columns?: number;
  className?: string;
}> = ({ 
  rows = 5, 
  columns = 4,
  className 
}) => (
  <div className={clsx('animate-pulse', className)}>
    <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            {Array.from({ length: columns }).map((_, index) => (
              <th key={index} className="px-6 py-3">
                <div className="h-4 bg-gray-300 rounded"></div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <td key={colIndex} className="px-6 py-4">
                  <div className="h-4 bg-gray-300 rounded"></div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export default LoadingSpinner;
