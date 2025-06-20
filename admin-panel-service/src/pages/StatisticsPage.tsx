import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, Form, Spinner, Alert } from 'react-bootstrap';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
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
import { useApp } from '../contexts/AppContext';

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

const StatisticsPage: React.FC = () => {
  const { addNotification } = useApp();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  });

  // Données des graphiques
  const [attendanceTrendData, setAttendanceTrendData] = useState<any>(null);
  const [classComparisonData, setClassComparisonData] = useState<any>(null);
  const [statusDistributionData, setStatusDistributionData] = useState<any>(null);
  const [monthlyTrendData, setMonthlyTrendData] = useState<any>(null);

  useEffect(() => {
    loadStatistics();
  }, [dateRange]);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Données simulées pour les graphiques
      setAttendanceTrendData({
        labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
        datasets: [
          {
            label: 'Taux de présence (%)',
            data: [95, 87, 92, 89, 94, 85, 88],
            borderColor: 'rgb(102, 126, 234)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true,
          },
          {
            label: 'Objectif (90%)',
            data: [90, 90, 90, 90, 90, 90, 90],
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            borderDash: [5, 5],
            fill: false,
          },
        ],
      });

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
            borderColor: [
              'rgb(102, 126, 234)',
              'rgb(118, 75, 162)',
              'rgb(255, 99, 132)',
              'rgb(54, 162, 235)',
              'rgb(255, 206, 86)',
            ],
            borderWidth: 1,
          },
        ],
      });

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
            borderWidth: 2,
            borderColor: '#fff',
          },
        ],
      });

      setMonthlyTrendData({
        labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
        datasets: [
          {
            label: 'Présences',
            data: [1200, 1350, 1280, 1400, 1320, 1450],
            backgroundColor: 'rgba(40, 167, 69, 0.8)',
          },
          {
            label: 'Absences',
            data: [200, 180, 220, 160, 190, 150],
            backgroundColor: 'rgba(220, 53, 69, 0.8)',
          },
          {
            label: 'Retards',
            data: [80, 70, 90, 60, 75, 65],
            backgroundColor: 'rgba(255, 193, 7, 0.8)',
          },
        ],
      });

      addNotification({
        type: 'success',
        title: 'Statistiques',
        message: 'Données chargées avec succès',
      });
    } catch (err: any) {
      setError(err.message || 'Erreur lors du chargement des statistiques');
      addNotification({
        type: 'error',
        title: 'Erreur',
        message: 'Impossible de charger les statistiques',
      });
    } finally {
      setLoading(false);
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

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const pieChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  const handleExport = (format: 'pdf' | 'excel' | 'csv') => {
    addNotification({
      type: 'info',
      title: 'Export en cours',
      message: `Export des statistiques en format ${format.toUpperCase()}...`,
    });
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
        <div className="text-center">
          <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
          <div className="mt-3">
            <h5>Chargement des statistiques...</h5>
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
    <div className="statistics-page">
      {/* En-tête */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="mb-1">Statistiques et analyses</h2>
          <p className="text-muted mb-0">
            Analysez les données de présence et générez des rapports
          </p>
        </div>
        <div className="d-flex gap-2">
          <Button variant="outline-success" onClick={() => handleExport('excel')}>
            <i className="fas fa-file-excel me-2"></i>
            Excel
          </Button>
          <Button variant="outline-danger" onClick={() => handleExport('pdf')}>
            <i className="fas fa-file-pdf me-2"></i>
            PDF
          </Button>
          <Button variant="outline-primary" onClick={() => handleExport('csv')}>
            <i className="fas fa-file-csv me-2"></i>
            CSV
          </Button>
        </div>
      </div>

      {/* Filtres de période */}
      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={4}>
              <Form.Group>
                <Form.Label>Date de début</Form.Label>
                <Form.Control
                  type="date"
                  value={dateRange.start}
                  onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label>Date de fin</Form.Label>
                <Form.Control
                  type="date"
                  value={dateRange.end}
                  onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label>&nbsp;</Form.Label>
                <div className="d-flex gap-2">
                  <Button variant="primary" className="w-100" onClick={loadStatistics}>
                    <i className="fas fa-sync me-2"></i>
                    Actualiser
                  </Button>
                </div>
              </Form.Group>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* KPIs principaux */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stat-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="stat-number">91.2%</div>
                  <div className="stat-label">Taux de présence moyen</div>
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
                  <div className="stat-number">1,247</div>
                  <div className="stat-label">Total présences</div>
                </div>
                <i className="fas fa-user-check fa-2x opacity-75"></i>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="stat-number">127</div>
                  <div className="stat-label">Total absences</div>
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
                  <div className="stat-number">45</div>
                  <div className="stat-label">Total retards</div>
                </div>
                <i className="fas fa-clock fa-2x opacity-75"></i>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Graphiques principaux */}
      <Row className="mb-4">
        <Col lg={8}>
          <Card className="chart-container">
            <Card.Header>
              <h5 className="mb-0">
                <i className="fas fa-chart-line me-2"></i>
                Évolution du taux de présence
              </h5>
            </Card.Header>
            <Card.Body>
              {attendanceTrendData ? (
                <Line data={attendanceTrendData} options={chartOptions} />
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
                <Doughnut data={statusDistributionData} options={pieChartOptions} />
              ) : (
                <div className="loading-spinner">
                  <Spinner animation="border" />
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col lg={6}>
          <Card className="chart-container">
            <Card.Header>
              <h5 className="mb-0">
                <i className="fas fa-chart-bar me-2"></i>
                Comparaison par classe
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
        
        <Col lg={6}>
          <Card className="chart-container">
            <Card.Header>
              <h5 className="mb-0">
                <i className="fas fa-chart-area me-2"></i>
                Tendance mensuelle
              </h5>
            </Card.Header>
            <Card.Body>
              {monthlyTrendData ? (
                <Bar data={monthlyTrendData} options={barChartOptions} />
              ) : (
                <div className="loading-spinner">
                  <Spinner animation="border" />
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Tableau de synthèse */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">
            <i className="fas fa-table me-2"></i>
            Synthèse par classe
          </h5>
        </Card.Header>
        <Card.Body>
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>Classe</th>
                  <th>Étudiants</th>
                  <th>Taux de présence</th>
                  <th>Présences</th>
                  <th>Absences</th>
                  <th>Retards</th>
                  <th>Tendance</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Classe A</strong></td>
                  <td>25</td>
                  <td><span className="badge bg-success">95%</span></td>
                  <td>475</td>
                  <td>20</td>
                  <td>5</td>
                  <td><i className="fas fa-arrow-up text-success"></i> +2%</td>
                </tr>
                <tr>
                  <td><strong>Classe B</strong></td>
                  <td>28</td>
                  <td><span className="badge bg-warning">87%</span></td>
                  <td>487</td>
                  <td>65</td>
                  <td>8</td>
                  <td><i className="fas fa-arrow-down text-danger"></i> -3%</td>
                </tr>
                <tr>
                  <td><strong>Classe C</strong></td>
                  <td>26</td>
                  <td><span className="badge bg-success">92%</span></td>
                  <td>479</td>
                  <td>35</td>
                  <td>6</td>
                  <td><i className="fas fa-arrow-up text-success"></i> +1%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default StatisticsPage;
