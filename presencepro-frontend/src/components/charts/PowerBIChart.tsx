import React, { useEffect, useRef } from 'react';
import { PowerBIEmbed } from 'powerbi-client-react';
import { models } from 'powerbi-client';

// Interface pour les props du composant Power BI
interface PowerBIChartProps {
  reportId?: string;
  embedUrl?: string;
  accessToken?: string;
  title: string;
  height?: string;
  width?: string;
  className?: string;
  mockData?: any;
  chartType?: 'line' | 'bar' | 'doughnut' | 'area';
}

// Composant Power BI Chart
const PowerBIChart: React.FC<PowerBIChartProps> = ({
  reportId,
  embedUrl,
  accessToken,
  title,
  height = '400px',
  width = '100%',
  className = '',
  mockData,
  chartType = 'line',
}) => {
  const chartRef = useRef<HTMLDivElement>(null);

  // Configuration Power BI
  const embedConfig = {
    type: 'report',
    id: reportId || 'demo-report-id',
    embedUrl: embedUrl || 'https://app.powerbi.com/reportEmbed',
    accessToken: accessToken || 'demo-access-token',
    tokenType: models.TokenType.Embed,
    settings: {
      panes: {
        filters: {
          expanded: false,
          visible: false,
        },
        pageNavigation: {
          visible: false,
        },
      },
      background: models.BackgroundType.Transparent,
    },
  };

  // Fonction pour créer un graphique de démonstration avec Canvas
  const createMockChart = () => {
    if (!chartRef.current || !mockData) return;

    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 400;
    canvas.style.width = '100%';
    canvas.style.height = height;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Nettoyer le conteneur
    chartRef.current.innerHTML = '';
    chartRef.current.appendChild(canvas);

    // Configuration du graphique
    const padding = 60;
    const chartWidth = canvas.width - 2 * padding;
    const chartHeight = canvas.height - 2 * padding;

    // Couleurs
    const primaryColor = '#2563eb';
    const gridColor = '#e5e7eb';
    const textColor = '#374151';

    // Dessiner le fond
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Dessiner la grille
    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 1;

    // Lignes horizontales
    for (let i = 0; i <= 5; i++) {
      const y = padding + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(padding + chartWidth, y);
      ctx.stroke();
    }

    // Lignes verticales
    if (mockData.labels) {
      const stepX = chartWidth / (mockData.labels.length - 1);
      for (let i = 0; i < mockData.labels.length; i++) {
        const x = padding + stepX * i;
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.lineTo(x, padding + chartHeight);
        ctx.stroke();
      }
    }

    // Dessiner les données selon le type de graphique
    if (chartType === 'line' && mockData.data) {
      drawLineChart(ctx, mockData, padding, chartWidth, chartHeight, primaryColor);
    } else if (chartType === 'bar' && mockData.data) {
      drawBarChart(ctx, mockData, padding, chartWidth, chartHeight, primaryColor);
    } else if (chartType === 'doughnut' && mockData.data) {
      drawDoughnutChart(ctx, mockData, canvas.width, canvas.height, primaryColor);
    }

    // Dessiner les labels
    ctx.fillStyle = textColor;
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';

    if (mockData.labels) {
      const stepX = chartWidth / (mockData.labels.length - 1);
      mockData.labels.forEach((label: string, index: number) => {
        const x = padding + stepX * index;
        ctx.fillText(label, x, padding + chartHeight + 20);
      });
    }

    // Titre
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(title, canvas.width / 2, 30);
  };

  // Fonction pour dessiner un graphique en ligne
  const drawLineChart = (
    ctx: CanvasRenderingContext2D,
    data: any,
    padding: number,
    chartWidth: number,
    chartHeight: number,
    color: string
  ) => {
    if (!data.data || data.data.length === 0) return;

    const maxValue = Math.max(...data.data);
    const stepX = chartWidth / (data.data.length - 1);

    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.beginPath();

    data.data.forEach((value: number, index: number) => {
      const x = padding + stepX * index;
      const y = padding + chartHeight - (value / maxValue) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // Points
    ctx.fillStyle = color;
    data.data.forEach((value: number, index: number) => {
      const x = padding + stepX * index;
      const y = padding + chartHeight - (value / maxValue) * chartHeight;
      
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fill();
    });
  };

  // Fonction pour dessiner un graphique en barres
  const drawBarChart = (
    ctx: CanvasRenderingContext2D,
    data: any,
    padding: number,
    chartWidth: number,
    chartHeight: number,
    color: string
  ) => {
    if (!data.data || data.data.length === 0) return;

    const maxValue = Math.max(...data.data);
    const barWidth = chartWidth / data.data.length * 0.8;
    const barSpacing = chartWidth / data.data.length * 0.2;

    ctx.fillStyle = color;

    data.data.forEach((value: number, index: number) => {
      const x = padding + (chartWidth / data.data.length) * index + barSpacing / 2;
      const barHeight = (value / maxValue) * chartHeight;
      const y = padding + chartHeight - barHeight;
      
      ctx.fillRect(x, y, barWidth, barHeight);
    });
  };

  // Fonction pour dessiner un graphique en donut
  const drawDoughnutChart = (
    ctx: CanvasRenderingContext2D,
    data: any,
    canvasWidth: number,
    canvasHeight: number,
    baseColor: string
  ) => {
    if (!data.data || data.data.length === 0) return;

    const centerX = canvasWidth / 2;
    const centerY = canvasHeight / 2;
    const radius = Math.min(canvasWidth, canvasHeight) / 3;
    const innerRadius = radius * 0.6;

    const total = data.data.reduce((sum: number, value: number) => sum + value, 0);
    let currentAngle = -Math.PI / 2;

    const colors = [
      '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'
    ];

    data.data.forEach((value: number, index: number) => {
      const sliceAngle = (value / total) * 2 * Math.PI;
      
      ctx.fillStyle = colors[index % colors.length];
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
      ctx.closePath();
      ctx.fill();

      currentAngle += sliceAngle;
    });
  };

  useEffect(() => {
    if (mockData) {
      createMockChart();
    }
  }, [mockData, chartType, title, height]);

  // Si on a des données mockées, utiliser le graphique de démonstration
  if (mockData) {
    return (
      <div className={`power-bi-chart ${className}`}>
        <div
          ref={chartRef}
          style={{ width, height }}
          className="border border-gray-200 rounded-lg bg-white"
        />
      </div>
    );
  }

  // Si on a une configuration Power BI valide, utiliser Power BI Embedded
  if (reportId && embedUrl && accessToken) {
    return (
      <div className={`power-bi-chart ${className}`} style={{ width, height }}>
        <PowerBIEmbed
          embedConfig={embedConfig}
          cssClassName="power-bi-embed"
        />
      </div>
    );
  }

  // Placeholder par défaut
  return (
    <div 
      className={`power-bi-chart ${className} bg-gray-100 rounded flex items-center justify-center border border-gray-200`}
      style={{ width, height }}
    >
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-500">Configuration Power BI requise</p>
        <p className="text-sm text-gray-400 mt-2">
          Veuillez configurer reportId, embedUrl et accessToken
        </p>
      </div>
    </div>
  );
};

export default PowerBIChart;
