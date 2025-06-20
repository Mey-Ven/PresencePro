import React from 'react';
import { useParams } from 'react-router-dom';
import Layout from '../../components/common/Layout';

const TeacherClasses: React.FC = () => {
  const { classId } = useParams<{ classId: string }>();

  return (
    <Layout title="Détails de la classe">
      <div className="space-y-6">
        <div className="card p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Détails de la classe {classId}
          </h1>
          <p className="text-gray-600">
            Cette page est en cours de développement. Elle affichera les détails de la classe sélectionnée.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default TeacherClasses;
