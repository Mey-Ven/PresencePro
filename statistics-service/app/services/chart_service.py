"""
Service de génération de graphiques
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from app.core.config import settings
from app.models.statistics import ChartType, ExportFormat

logger = logging.getLogger(__name__)

# Configuration matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class ChartService:
    """Service de génération de graphiques"""
    
    def __init__(self):
        self.export_dir = settings.export_dir
        self.chart_width = settings.chart_width
        self.chart_height = settings.chart_height
        self.chart_dpi = settings.chart_dpi
        self.chart_theme = settings.chart_theme
        
        # Créer le répertoire d'export s'il n'existe pas
        os.makedirs(f"{self.export_dir}/charts", exist_ok=True)
    
    async def generate_chart(
        self,
        chart_type: ChartType,
        data: Dict[str, Any],
        title: str = None,
        x_axis_label: str = None,
        y_axis_label: str = None,
        export_format: ExportFormat = ExportFormat.PNG,
        use_plotly: bool = True
    ) -> Dict[str, Any]:
        """Générer un graphique"""
        try:
            chart_id = str(uuid.uuid4())
            
            if use_plotly:
                return await self._generate_plotly_chart(
                    chart_type, data, title, x_axis_label, y_axis_label,
                    export_format, chart_id
                )
            else:
                return await self._generate_matplotlib_chart(
                    chart_type, data, title, x_axis_label, y_axis_label,
                    export_format, chart_id
                )
                
        except Exception as e:
            logger.error(f"Erreur génération graphique: {e}")
            raise
    
    async def _generate_plotly_chart(
        self,
        chart_type: ChartType,
        data: Dict[str, Any],
        title: str,
        x_axis_label: str,
        y_axis_label: str,
        export_format: ExportFormat,
        chart_id: str
    ) -> Dict[str, Any]:
        """Générer un graphique avec Plotly"""
        
        # Créer le graphique selon le type
        if chart_type == ChartType.LINE_CHART:
            fig = self._create_plotly_line_chart(data, title, x_axis_label, y_axis_label)
        elif chart_type == ChartType.BAR_CHART:
            fig = self._create_plotly_bar_chart(data, title, x_axis_label, y_axis_label)
        elif chart_type == ChartType.PIE_CHART:
            fig = self._create_plotly_pie_chart(data, title)
        elif chart_type == ChartType.HEATMAP:
            fig = self._create_plotly_heatmap(data, title)
        elif chart_type == ChartType.HISTOGRAM:
            fig = self._create_plotly_histogram(data, title, x_axis_label, y_axis_label)
        elif chart_type == ChartType.BOX_PLOT:
            fig = self._create_plotly_box_plot(data, title, x_axis_label, y_axis_label)
        elif chart_type == ChartType.SCATTER_PLOT:
            fig = self._create_plotly_scatter_plot(data, title, x_axis_label, y_axis_label)
        elif chart_type == ChartType.AREA_CHART:
            fig = self._create_plotly_area_chart(data, title, x_axis_label, y_axis_label)
        else:
            raise ValueError(f"Type de graphique non supporté: {chart_type}")
        
        # Appliquer le thème
        fig.update_layout(
            template=self.chart_theme,
            width=self.chart_width,
            height=self.chart_height,
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Exporter le graphique
        file_extension = export_format.value
        filename = f"chart_{chart_id}.{file_extension}"
        file_path = f"{self.export_dir}/charts/{filename}"
        
        if export_format == ExportFormat.PNG:
            fig.write_image(file_path, format="png", engine="kaleido")
        elif export_format == ExportFormat.SVG:
            fig.write_image(file_path, format="svg", engine="kaleido")
        elif export_format == ExportFormat.PDF:
            fig.write_image(file_path, format="pdf", engine="kaleido")
        else:
            # HTML par défaut
            fig.write_html(file_path.replace(f".{file_extension}", ".html"))
            file_path = file_path.replace(f".{file_extension}", ".html")
            filename = filename.replace(f".{file_extension}", ".html")
        
        # Obtenir la taille du fichier
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        return {
            "chart_id": chart_id,
            "chart_type": chart_type.value,
            "file_path": file_path,
            "file_url": f"/exports/charts/{filename}",
            "file_size": file_size,
            "format": export_format.value,
            "width": self.chart_width,
            "height": self.chart_height,
            "generated_at": datetime.now()
        }
    
    def _create_plotly_line_chart(
        self, 
        data: Dict[str, Any], 
        title: str, 
        x_axis_label: str, 
        y_axis_label: str
    ) -> go.Figure:
        """Créer un graphique en ligne avec Plotly"""
        fig = go.Figure()
        
        if "series" in data:
            for series in data["series"]:
                fig.add_trace(go.Scatter(
                    x=series.get("x", []),
                    y=series.get("y", []),
                    mode='lines+markers',
                    name=series.get("name", "Série"),
                    line=dict(width=3),
                    marker=dict(size=6)
                ))
        else:
            fig.add_trace(go.Scatter(
                x=data.get("x", []),
                y=data.get("y", []),
                mode='lines+markers',
                name=data.get("name", "Données"),
                line=dict(width=3),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title=title or "Graphique en ligne",
            xaxis_title=x_axis_label or "X",
            yaxis_title=y_axis_label or "Y",
            hovermode='x unified'
        )
        
        return fig
    
    def _create_plotly_bar_chart(
        self, 
        data: Dict[str, Any], 
        title: str, 
        x_axis_label: str, 
        y_axis_label: str
    ) -> go.Figure:
        """Créer un graphique en barres avec Plotly"""
        fig = go.Figure()
        
        if "series" in data:
            for series in data["series"]:
                fig.add_trace(go.Bar(
                    x=series.get("x", []),
                    y=series.get("y", []),
                    name=series.get("name", "Série"),
                    text=series.get("y", []),
                    textposition='auto'
                ))
        else:
            fig.add_trace(go.Bar(
                x=data.get("x", []),
                y=data.get("y", []),
                name=data.get("name", "Données"),
                text=data.get("y", []),
                textposition='auto'
            ))
        
        fig.update_layout(
            title=title or "Graphique en barres",
            xaxis_title=x_axis_label or "Catégories",
            yaxis_title=y_axis_label or "Valeurs",
            barmode='group'
        )
        
        return fig
    
    def _create_plotly_pie_chart(self, data: Dict[str, Any], title: str) -> go.Figure:
        """Créer un graphique en secteurs avec Plotly"""
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=data.get("labels", []),
            values=data.get("values", []),
            hole=0.3,  # Donut chart
            textinfo='label+percent',
            textposition='auto'
        ))
        
        fig.update_layout(
            title=title or "Répartition",
            showlegend=True
        )
        
        return fig
    
    def _create_plotly_heatmap(self, data: Dict[str, Any], title: str) -> go.Figure:
        """Créer une heatmap avec Plotly"""
        fig = go.Figure()
        
        fig.add_trace(go.Heatmap(
            z=data.get("z", []),
            x=data.get("x", []),
            y=data.get("y", []),
            colorscale='RdYlBu_r',
            showscale=True
        ))
        
        fig.update_layout(
            title=title or "Carte de chaleur",
            xaxis_title=data.get("x_label", "X"),
            yaxis_title=data.get("y_label", "Y")
        )
        
        return fig
    
    def _create_plotly_histogram(
        self, 
        data: Dict[str, Any], 
        title: str, 
        x_axis_label: str, 
        y_axis_label: str
    ) -> go.Figure:
        """Créer un histogramme avec Plotly"""
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=data.get("values", []),
            nbinsx=data.get("bins", 20),
            name="Distribution"
        ))
        
        fig.update_layout(
            title=title or "Distribution",
            xaxis_title=x_axis_label or "Valeurs",
            yaxis_title=y_axis_label or "Fréquence",
            bargap=0.1
        )
        
        return fig
    
    def _create_plotly_box_plot(
        self, 
        data: Dict[str, Any], 
        title: str, 
        x_axis_label: str, 
        y_axis_label: str
    ) -> go.Figure:
        """Créer un box plot avec Plotly"""
        fig = go.Figure()
        
        if "groups" in data:
            for group in data["groups"]:
                fig.add_trace(go.Box(
                    y=group.get("values", []),
                    name=group.get("name", "Groupe"),
                    boxpoints='outliers'
                ))
        else:
            fig.add_trace(go.Box(
                y=data.get("values", []),
                name=data.get("name", "Données"),
                boxpoints='outliers'
            ))
        
        fig.update_layout(
            title=title or "Boîte à moustaches",
            xaxis_title=x_axis_label or "Groupes",
            yaxis_title=y_axis_label or "Valeurs"
        )
        
        return fig
    
    def _create_plotly_scatter_plot(
        self, 
        data: Dict[str, Any], 
        title: str, 
        x_axis_label: str, 
        y_axis_label: str
    ) -> go.Figure:
        """Créer un nuage de points avec Plotly"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.get("x", []),
            y=data.get("y", []),
            mode='markers',
            marker=dict(
                size=data.get("sizes", 8),
                color=data.get("colors", 'blue'),
                opacity=0.7
            ),
            text=data.get("labels", []),
            name=data.get("name", "Points")
        ))
        
        fig.update_layout(
            title=title or "Nuage de points",
            xaxis_title=x_axis_label or "X",
            yaxis_title=y_axis_label or "Y"
        )
        
        return fig
    
    def _create_plotly_area_chart(
        self, 
        data: Dict[str, Any], 
        title: str, 
        x_axis_label: str, 
        y_axis_label: str
    ) -> go.Figure:
        """Créer un graphique en aires avec Plotly"""
        fig = go.Figure()
        
        if "series" in data:
            for series in data["series"]:
                fig.add_trace(go.Scatter(
                    x=series.get("x", []),
                    y=series.get("y", []),
                    fill='tonexty' if len(fig.data) > 0 else 'tozeroy',
                    mode='lines',
                    name=series.get("name", "Série"),
                    line=dict(width=0)
                ))
        else:
            fig.add_trace(go.Scatter(
                x=data.get("x", []),
                y=data.get("y", []),
                fill='tozeroy',
                mode='lines',
                name=data.get("name", "Données"),
                line=dict(width=0)
            ))
        
        fig.update_layout(
            title=title or "Graphique en aires",
            xaxis_title=x_axis_label or "X",
            yaxis_title=y_axis_label or "Y"
        )
        
        return fig
    
    async def generate_attendance_trend_chart(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer un graphique de tendance de présence"""
        if "weekly_trends" not in stats_data:
            raise ValueError("Données de tendances hebdomadaires manquantes")
        
        trends = stats_data["weekly_trends"]
        
        chart_data = {
            "x": [f"Semaine {trend['week']}" for trend in trends],
            "y": [trend["attendance_rate"] for trend in trends],
            "name": "Taux de présence"
        }
        
        return await self.generate_chart(
            ChartType.LINE_CHART,
            chart_data,
            title="Évolution du taux de présence",
            x_axis_label="Semaines",
            y_axis_label="Taux de présence (%)"
        )
    
    async def generate_course_comparison_chart(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer un graphique de comparaison par cours"""
        if "course_breakdown" not in stats_data:
            raise ValueError("Données de répartition par cours manquantes")
        
        courses = stats_data["course_breakdown"]
        
        chart_data = {
            "x": [course["course_id"] for course in courses],
            "y": [course["attendance_rate"] for course in courses],
            "name": "Taux de présence par cours"
        }
        
        return await self.generate_chart(
            ChartType.BAR_CHART,
            chart_data,
            title="Comparaison des taux de présence par cours",
            x_axis_label="Cours",
            y_axis_label="Taux de présence (%)"
        )
    
    async def generate_attendance_distribution_chart(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer un graphique de répartition des présences"""
        chart_data = {
            "labels": ["Présent", "Absent", "Retard"],
            "values": [
                stats_data.get("present_count", 0),
                stats_data.get("absent_count", 0),
                stats_data.get("late_count", 0)
            ]
        }
        
        return await self.generate_chart(
            ChartType.PIE_CHART,
            chart_data,
            title="Répartition des présences"
        )


# Instance globale du service
chart_service = ChartService()
