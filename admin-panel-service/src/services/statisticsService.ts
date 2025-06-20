import { statisticsApi, apiCall, formatQueryParams, formatDateForApi } from './api';
import { 
  StudentStatistics, 
  ClassStatistics, 
  GlobalStatistics,
  ChartData 
} from '../types';

export interface StatisticsFilters {
  start_date?: string | Date;
  end_date?: string | Date;
  include_trends?: boolean;
  include_rankings?: boolean;
  include_comparisons?: boolean;
}

export interface ChartRequest {
  chart_type: 'line_chart' | 'bar_chart' | 'pie_chart' | 'heatmap' | 'histogram' | 'box_plot' | 'scatter_plot' | 'area_chart';
  data_source: string;
  title: string;
  x_axis_label?: string;
  y_axis_label?: string;
  export_format: 'png' | 'jpg' | 'pdf' | 'svg';
  width?: number;
  height?: number;
}

export interface ExportRequest {
  data_type: 'student_stats' | 'class_stats' | 'global_stats' | 'attendance_records';
  format: 'json' | 'csv' | 'xlsx' | 'pdf';
  entity_type?: 'student' | 'class' | 'global';
  entity_id?: string;
  start_date?: string | Date;
  end_date?: string | Date;
}

class StatisticsService {
  // === Statistiques des étudiants ===
  
  // Obtenir les statistiques d'un étudiant
  async getStudentStatistics(
    studentId: string, 
    filters?: StatisticsFilters
  ): Promise<StudentStatistics> {
    const params = this.formatFilters(filters);
    const queryString = formatQueryParams(params);
    
    return await apiCall(() =>
      statisticsApi.get<StudentStatistics>(`/stats/student/${studentId}?${queryString}`)
    );
  }

  // Comparer plusieurs étudiants
  async compareStudents(
    studentIds: string[], 
    filters?: StatisticsFilters
  ): Promise<StudentStatistics[]> {
    const params = {
      student_ids: studentIds.join(','),
      ...this.formatFilters(filters),
    };
    
    const queryString = formatQueryParams(params);
    return await apiCall(() =>
      statisticsApi.get<StudentStatistics[]>(`/stats/students/compare?${queryString}`)
    );
  }

  // === Statistiques des classes ===
  
  // Obtenir les statistiques d'une classe
  async getClassStatistics(
    classId: string, 
    filters?: StatisticsFilters
  ): Promise<ClassStatistics> {
    const params = this.formatFilters(filters);
    const queryString = formatQueryParams(params);
    
    return await apiCall(() =>
      statisticsApi.get<ClassStatistics>(`/stats/class/${classId}?${queryString}`)
    );
  }

  // Comparer plusieurs classes
  async compareClasses(
    classIds: string[], 
    filters?: StatisticsFilters
  ): Promise<ClassStatistics[]> {
    const params = {
      class_ids: classIds.join(','),
      ...this.formatFilters(filters),
    };
    
    const queryString = formatQueryParams(params);
    return await apiCall(() =>
      statisticsApi.get<ClassStatistics[]>(`/stats/classes/compare?${queryString}`)
    );
  }

  // === Statistiques globales ===
  
  // Obtenir les statistiques globales
  async getGlobalStatistics(filters?: StatisticsFilters): Promise<GlobalStatistics> {
    const params = this.formatFilters(filters);
    const queryString = formatQueryParams(params);
    
    return await apiCall(() =>
      statisticsApi.get<GlobalStatistics>(`/stats/global?${queryString}`)
    );
  }

  // Obtenir les tendances par période
  async getTrendsByPeriod(
    period: 'daily' | 'weekly' | 'monthly',
    filters?: StatisticsFilters
  ): Promise<any[]> {
    const params = {
      period,
      ...this.formatFilters(filters),
    };
    
    const queryString = formatQueryParams(params);
    return await apiCall(() =>
      statisticsApi.get<any[]>(`/stats/trends?${queryString}`)
    );
  }

  // === Génération de graphiques ===
  
  // Générer un graphique
  async generateChart(request: ChartRequest): Promise<{ chart_id: string; url: string }> {
    return await apiCall(() =>
      statisticsApi.post<{ chart_id: string; url: string }>('/stats/charts/generate', request)
    );
  }

  // Télécharger un graphique
  async downloadChart(chartId: string): Promise<Blob> {
    const response = await statisticsApi.get(`/stats/charts/${chartId}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Générer un graphique de tendance pour un étudiant
  async generateStudentTrendChart(
    studentId: string,
    filters?: StatisticsFilters
  ): Promise<{ chart_id: string; url: string }> {
    const request: ChartRequest = {
      chart_type: 'line_chart',
      data_source: `student_${studentId}`,
      title: 'Évolution de la présence',
      x_axis_label: 'Date',
      y_axis_label: 'Taux de présence (%)',
      export_format: 'png',
    };
    
    return this.generateChart(request);
  }

  // Générer un graphique de comparaison de classe
  async generateClassComparisonChart(
    classId: string,
    filters?: StatisticsFilters
  ): Promise<{ chart_id: string; url: string }> {
    const request: ChartRequest = {
      chart_type: 'bar_chart',
      data_source: `class_${classId}`,
      title: 'Comparaison des étudiants',
      x_axis_label: 'Étudiants',
      y_axis_label: 'Taux de présence (%)',
      export_format: 'png',
    };
    
    return this.generateChart(request);
  }

  // Générer un graphique global
  async generateGlobalChart(
    chartType: ChartRequest['chart_type'] = 'bar_chart',
    filters?: StatisticsFilters
  ): Promise<{ chart_id: string; url: string }> {
    const request: ChartRequest = {
      chart_type: chartType,
      data_source: 'global',
      title: 'Statistiques globales',
      x_axis_label: 'Classes',
      y_axis_label: 'Taux de présence (%)',
      export_format: 'png',
    };
    
    return this.generateChart(request);
  }

  // === Export de données ===
  
  // Exporter des statistiques
  async exportStatistics(request: ExportRequest): Promise<{ export_id: string; download_url: string }> {
    const formattedRequest = {
      ...request,
      start_date: request.start_date ? formatDateForApi(request.start_date) : undefined,
      end_date: request.end_date ? formatDateForApi(request.end_date) : undefined,
    };
    
    return await apiCall(() =>
      statisticsApi.post<{ export_id: string; download_url: string }>('/stats/export', formattedRequest)
    );
  }

  // Télécharger un export
  async downloadExport(exportId: string): Promise<Blob> {
    const response = await statisticsApi.get(`/stats/exports/${exportId}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // === Gestion du cache ===
  
  // Vider le cache
  async clearCache(pattern?: string): Promise<{ cleared_keys: number }> {
    const params = pattern ? { pattern } : {};
    const queryString = formatQueryParams(params);
    
    return await apiCall(() =>
      statisticsApi.delete<{ cleared_keys: number }>(`/stats/cache?${queryString}`)
    );
  }

  // Obtenir les informations du cache
  async getCacheInfo(): Promise<{
    total_keys: number;
    memory_usage: string;
    hit_rate: number;
  }> {
    return await apiCall(() =>
      statisticsApi.get('/stats/cache/info')
    );
  }

  // === Fonctions utilitaires ===
  
  // Formater les filtres pour l'API
  private formatFilters(filters?: StatisticsFilters): Record<string, any> {
    if (!filters) return {};
    
    return {
      ...filters,
      start_date: filters.start_date ? formatDateForApi(filters.start_date) : undefined,
      end_date: filters.end_date ? formatDateForApi(filters.end_date) : undefined,
    };
  }

  // Obtenir les données pour Chart.js
  async getChartData(
    type: 'student' | 'class' | 'global',
    id?: string,
    filters?: StatisticsFilters
  ): Promise<ChartData> {
    let endpoint = '';
    
    switch (type) {
      case 'student':
        endpoint = `/stats/student/${id}/chart-data`;
        break;
      case 'class':
        endpoint = `/stats/class/${id}/chart-data`;
        break;
      case 'global':
        endpoint = '/stats/global/chart-data';
        break;
    }
    
    const params = this.formatFilters(filters);
    const queryString = formatQueryParams(params);
    
    return await apiCall(() =>
      statisticsApi.get<ChartData>(`${endpoint}?${queryString}`)
    );
  }

  // Obtenir les KPIs principaux
  async getMainKPIs(filters?: StatisticsFilters): Promise<{
    total_students: number;
    total_classes: number;
    overall_attendance_rate: number;
    absent_today: number;
    late_today: number;
    trend_direction: 'up' | 'down' | 'stable';
    trend_percentage: number;
  }> {
    const params = this.formatFilters(filters);
    const queryString = formatQueryParams(params);
    
    return await apiCall(() =>
      statisticsApi.get(`/stats/kpis?${queryString}`)
    );
  }

  // Obtenir les alertes basées sur les statistiques
  async getStatisticsAlerts(): Promise<{
    low_attendance_students: Array<{ student_id: string; student_name: string; attendance_rate: number }>;
    declining_classes: Array<{ class_id: string; class_name: string; trend: number }>;
    high_absence_days: Array<{ date: string; absence_count: number }>;
  }> {
    return await apiCall(() =>
      statisticsApi.get('/stats/alerts')
    );
  }
}

export const statisticsService = new StatisticsService();
export default statisticsService;
