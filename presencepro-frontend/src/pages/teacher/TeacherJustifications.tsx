import React from 'react';
import Layout from '../../components/common/Layout';

const TeacherJustifications: React.FC = () => {
  return (
    <Layout title="Justifications">
      <div className="space-y-6">
        <div className="card p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Gestion des justifications
          </h1>
          <p className="text-gray-600">
            Cette page est en cours de développement. Elle permettra de gérer les justifications d'absence.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default TeacherJustifications;
