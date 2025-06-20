import React from 'react';
import Layout from '../../components/common/Layout';

const TeacherStatistics: React.FC = () => {
  return (
    <Layout title="Statistiques">
      <div className="space-y-6">
        <div className="card p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Mes statistiques
          </h1>
          <p className="text-gray-600">
            Cette page est en cours de développement. Elle affichera vos statistiques de présence.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default TeacherStatistics;
