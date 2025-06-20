import React from 'react';
import Layout from '../../components/common/Layout';

const StudentCourses: React.FC = () => {
  return (
    <Layout title="Mes cours">
      <div className="space-y-6">
        <div className="card p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Mes cours
          </h1>
          <p className="text-gray-600">
            Cette page est en cours de développement. Elle affichera tous vos cours.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default StudentCourses;
