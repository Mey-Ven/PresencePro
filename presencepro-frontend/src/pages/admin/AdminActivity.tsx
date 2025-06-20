import React from 'react';
import Layout from '../../components/common/Layout';

const AdminActivity: React.FC = () => {
  return (
    <Layout title="Activité système">
      <div className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Activité système
          </h1>
          <p className="text-gray-600">
            Cette page est en cours de développement. Elle affichera toute l'activité du système.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default AdminActivity;
