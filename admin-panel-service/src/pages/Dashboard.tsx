import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Alert, Spinner } from 'react-bootstrap';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import statisticsService from '../services/statisticsService';
import userService from '../services/userService';

// Enregistrer les composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface DashboardStats {
  totalStudents: number;
  totalTeachers: number;
  totalClasses: number;
  attendanceRate: number;
  absentToday: number;
  lateToday: number;
  trendDirection: 'up' | 'down' | 'stable';
  trendPercentage: number;
}

const Dashboard: React.FC = () => {
  const { state: authState } = useAuth();
  const { addNotification } = useApp();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  // Données pour les graphiques
  const [attendanceChartData, setAttendanceChartData] = useState<any>(null);
  const [classComparisonData, setClassComparisonData] = useState<any>(null);
  const [statusDistributionData, setStatusDistributionData] = useState<any>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Charger les statistiques principales
      const [userStats, globalStats, kpis] = await Promise.all([
        userService.getUserStats(),
        statisticsService.getGlobalStatistics({
          start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 jours
          end_date: new Date(),
        }),
        statisticsService.getMainKPIs(),
      ]);

      setStats({
        totalStudents: userStats.students_count,
        totalTeachers: userStats.teachers_count,
        totalClasses: kpis.total_classes,
        attendanceRate: kpis.overall_attendance_rate,
        absentToday: kpis.absent_today,
        lateToday: kpis.late_today,
        trendDirection: kpis.trend_direction,
        trendPercentage: kpis.trend_percentage,
      });

      // Charger les données des graphiques
      await loadChartData();

      addNotification({
        type: 'success',
        title: 'Tableau de bord',
        message: 'Données chargées avec succès',
      });
    } catch (err: any) {
      setError(err.message || 'Erreur lors du chargement des données');
      addNotification({
        type: 'error',
        title: 'Erreur',
        message: 'Impossible de charger les données du tableau de bord',
      });
    } finally {
      setLoading(false);
    }
  };

  const loadChartData = async () => {
    try {
      // Données pour le graphique de tendance des présences
      const attendanceData = await statisticsService.getChartData('global', undefined, {
        start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 jours
        end_date: new Date(),
      });

      setAttendanceChartData({
        labels: attendanceData.labels,
        datasets: [
          {
            label: 'Taux de présence (%)',
            data: attendanceData.datasets[0]?.data || [],
            borderColor: 'rgb(102, 126, 234)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true,
          },
        ],
      });

      // Données pour la comparaison des classes
      setClassComparisonData({
        labels: ['Classe A', 'Classe B', 'Classe C', 'Classe D', 'Classe E'],
        datasets: [
          {
            label: 'Taux de présence (%)',
            data: [95, 87, 92, 89, 94],
            backgroundColor: [
              'rgba(102, 126, 234, 0.8)',
              'rgba(118, 75, 162, 0.8)',
              'rgba(255, 99, 132, 0.8)',
              'rgba(54, 162, 235, 0.8)',
              'rgba(255, 206, 86, 0.8)',
            ],
          },
        ],
      });

      // Données pour la distribution des statuts
      setStatusDistributionData({
        labels: ['Présent', 'Absent', 'Retard', 'Excusé'],
        datasets: [
          {
            data: [75, 15, 7, 3],
            backgroundColor: [
              '#28a745',
              '#dc3545',
              '#ffc107',
              '#17a2b8',
            ],
          },
        ],
      });
    } catch (err) {
      console.error('Erreur lors du chargement des graphiques:', err);
    }
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
        <div className="text-center">
          <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
          <div className="mt-3">
            <h5>Chargement du tableau de bord...</h5>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Erreur</Alert.Heading>
        <p>{error}</p>
      </Alert>
    );
  }

  return (
    <div className="dashboard">
      {/* En-tête */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="mb-1">Tableau de bord</h2>
          <p className="text-muted mb-0">
            Bienvenue {authState.user?.first_name}, voici un aperçu de votre établissement
          </p>
        </div>
        <div className="text-end">
          <small className="text-muted">
            Dernière mise à jour: {new Date().toLocaleString('fr-FR')}
          </small>
        </div>
      </div>

      {/* Cartes de statistiques */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stat-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="stat-number">{stats?.totalStudents || 0}</div>
                  <div className="stat-label">Étudiants</div>
                </div>
                <i className="fas fa-user-graduate fa-2x opacity-75"></i>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={3}>
          <Card className="stat-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="stat-number">{stats?.attendanceRate.toFixed(1) || 0}%</div>
                  <div className="stat-label">Taux de présence</div>
                </div>
                <i className="fas fa-chart-line fa-2x opacity-75"></i>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={3}>
          <Card className="stat-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="stat-number">{stats?.absentToday || 0}</div>
                  <div className="stat-label">Absents aujourd'hui</div>
                </div>
                <i className="fas fa-user-times fa-2x opacity-75"></i>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={3}>
          <Card className="stat-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="stat-number">{stats?.totalClasses || 0}</div>
                  <div className="stat-label">Classes</div>
                </div>
                <i className="fas fa-chalkboard fa-2x opacity-75"></i>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Graphiques */}
      <Row>
        <Col lg={8}>
          <Card className="chart-container">
            <Card.Header>
              <h5 className="mb-0">
                <i className="fas fa-chart-line me-2"></i>
                Évolution des présences (7 derniers jours)
              </h5>
            </Card.Header>
            <Card.Body>
              {attendanceChartData ? (
                <Line data={attendanceChartData} options={chartOptions} />
              ) : (
                <div className="loading-spinner">
                  <Spinner animation="border" />
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={4}>
          <Card className="chart-container">
            <Card.Header>
              <h5 className="mb-0">
                <i className="fas fa-chart-pie me-2"></i>
                Distribution des statuts
              </h5>
            </Card.Header>
            <Card.Body>
              {statusDistributionData ? (
                <Doughnut data={statusDistributionData} options={doughnutOptions} />
              ) : (
                <div className="loading-spinner">
                  <Spinner animation="border" />
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mt-4">
        <Col lg={12}>
          <Card className="chart-container">
            <Card.Header>
              <h5 className="mb-0">
                <i className="fas fa-chart-bar me-2"></i>
                Comparaison des classes
              </h5>
            </Card.Header>
            <Card.Body>
              {classComparisonData ? (
                <Bar data={classComparisonData} options={chartOptions} />
              ) : (
                <div className="loading-spinner">
                  <Spinner animation="border" />
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
