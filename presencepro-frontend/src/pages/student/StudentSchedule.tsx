import React from 'react';
import Layout from '../../components/common/Layout';

const StudentSchedule: React.FC = () => {
  return (
    <Layout title="Mon planning">
      <div className="space-y-6">
        <div className="card p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Mon planning
          </h1>
          <p className="text-gray-600">
            Cette page est en cours de développement. Elle affichera votre planning de cours.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default StudentSchedule;
