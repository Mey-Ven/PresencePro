import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

// Composant App simple pour tester
const App = () => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>PresencePro Admin Panel</h1>
      <p>Application en cours de chargement...</p>
    </div>
  );
};

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
