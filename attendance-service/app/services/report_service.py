"""
Service de génération de rapports avancés
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, case
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
import pandas as pd
from collections import defaultdict

from app.models.attendance import Attendance, AttendanceStatus, AttendanceMethod
from app.core.config import settings


class ReportService:
    """Service de génération de rapports et analytics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def generate_attendance_trends(
        self,
        course_id: Optional[int] = None,
        student_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Générer les tendances de présence"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Requête de base
            query = self.db.query(Attendance).filter(
                func.date(Attendance.marked_at).between(start_date, end_date)
            )
            
            if course_id:
                query = query.filter(Attendance.course_id == course_id)
            if student_id:
                query = query.filter(Attendance.student_id == student_id)
            
            attendances = query.all()
            
            # Grouper par jour
            daily_stats = defaultdict(lambda: {
                'date': None,
                'total': 0,
                'present': 0,
                'absent': 0,
                'late': 0,
                'excused': 0,
                'attendance_rate': 0.0
            })
            
            for att in attendances:
                day = att.marked_at.date()
                daily_stats[day]['date'] = day.isoformat()
                daily_stats[day]['total'] += 1
                
                if att.status == AttendanceStatus.PRESENT:
                    daily_stats[day]['present'] += 1
                elif att.status == AttendanceStatus.ABSENT:
                    daily_stats[day]['absent'] += 1
                elif att.status == AttendanceStatus.LATE:
                    daily_stats[day]['late'] += 1
                elif att.status == AttendanceStatus.EXCUSED:
                    daily_stats[day]['excused'] += 1
            
            # Calculer les taux
            for day_data in daily_stats.values():
                if day_data['total'] > 0:
                    day_data['attendance_rate'] = (
                        day_data['present'] + day_data['late']
                    ) / day_data['total']
            
            # Convertir en liste triée
            trends = sorted(daily_stats.values(), key=lambda x: x['date'])
            
            # Calculer les moyennes mobiles
            if len(trends) >= 7:
                for i in range(6, len(trends)):
                    week_data = trends[i-6:i+1]
                    avg_rate = sum(d['attendance_rate'] for d in week_data) / 7
                    trends[i]['moving_average_7d'] = avg_rate
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'trends': trends,
                'summary': {
                    'total_days': len(trends),
                    'avg_attendance_rate': sum(t['attendance_rate'] for t in trends) / len(trends) if trends else 0,
                    'best_day': max(trends, key=lambda x: x['attendance_rate']) if trends else None,
                    'worst_day': min(trends, key=lambda x: x['attendance_rate']) if trends else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erreur génération tendances: {e}")
            raise
    
    def generate_comparative_report(
        self,
        course_ids: List[int],
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Générer un rapport comparatif entre cours"""
        try:
            course_stats = {}
            
            for course_id in course_ids:
                # Statistiques par cours
                query = self.db.query(Attendance).filter(
                    and_(
                        Attendance.course_id == course_id,
                        func.date(Attendance.marked_at).between(start_date, end_date)
                    )
                )
                
                attendances = query.all()
                
                if attendances:
                    total = len(attendances)
                    present = len([a for a in attendances if a.status == AttendanceStatus.PRESENT])
                    absent = len([a for a in attendances if a.status == AttendanceStatus.ABSENT])
                    late = len([a for a in attendances if a.status == AttendanceStatus.LATE])
                    
                    # Étudiants uniques
                    unique_students = len(set(a.student_id for a in attendances))
                    
                    # Sessions uniques
                    unique_sessions = len(set(a.marked_at.date() for a in attendances))
                    
                    course_stats[course_id] = {
                        'course_id': course_id,
                        'total_attendances': total,
                        'unique_students': unique_students,
                        'unique_sessions': unique_sessions,
                        'present_count': present,
                        'absent_count': absent,
                        'late_count': late,
                        'attendance_rate': (present + late) / total if total > 0 else 0,
                        'punctuality_rate': present / (present + late) if (present + late) > 0 else 0,
                        'avg_students_per_session': total / unique_sessions if unique_sessions > 0 else 0
                    }
                else:
                    course_stats[course_id] = {
                        'course_id': course_id,
                        'total_attendances': 0,
                        'unique_students': 0,
                        'unique_sessions': 0,
                        'present_count': 0,
                        'absent_count': 0,
                        'late_count': 0,
                        'attendance_rate': 0,
                        'punctuality_rate': 0,
                        'avg_students_per_session': 0
                    }
            
            # Classements
            courses_by_attendance = sorted(
                course_stats.values(),
                key=lambda x: x['attendance_rate'],
                reverse=True
            )
            
            courses_by_punctuality = sorted(
                course_stats.values(),
                key=lambda x: x['punctuality_rate'],
                reverse=True
            )
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'course_stats': list(course_stats.values()),
                'rankings': {
                    'by_attendance_rate': courses_by_attendance,
                    'by_punctuality_rate': courses_by_punctuality
                },
                'global_stats': {
                    'total_courses': len(course_ids),
                    'avg_attendance_rate': sum(c['attendance_rate'] for c in course_stats.values()) / len(course_stats) if course_stats else 0,
                    'avg_punctuality_rate': sum(c['punctuality_rate'] for c in course_stats.values()) / len(course_stats) if course_stats else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erreur rapport comparatif: {e}")
            raise
    
    def generate_method_analysis(
        self,
        start_date: date,
        end_date: date,
        course_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyser les méthodes d'enregistrement des présences"""
        try:
            query = self.db.query(Attendance).filter(
                func.date(Attendance.marked_at).between(start_date, end_date)
            )
            
            if course_id:
                query = query.filter(Attendance.course_id == course_id)
            
            attendances = query.all()
            
            # Statistiques par méthode
            method_stats = defaultdict(lambda: {
                'total': 0,
                'present': 0,
                'absent': 0,
                'late': 0,
                'avg_confidence': 0.0,
                'confidence_scores': []
            })
            
            for att in attendances:
                method = att.method.value
                method_stats[method]['total'] += 1
                
                if att.status == AttendanceStatus.PRESENT:
                    method_stats[method]['present'] += 1
                elif att.status == AttendanceStatus.ABSENT:
                    method_stats[method]['absent'] += 1
                elif att.status == AttendanceStatus.LATE:
                    method_stats[method]['late'] += 1
                
                if att.confidence_score is not None:
                    method_stats[method]['confidence_scores'].append(att.confidence_score)
            
            # Calculer les moyennes de confiance
            for method_data in method_stats.values():
                if method_data['confidence_scores']:
                    method_data['avg_confidence'] = sum(method_data['confidence_scores']) / len(method_data['confidence_scores'])
                    method_data['min_confidence'] = min(method_data['confidence_scores'])
                    method_data['max_confidence'] = max(method_data['confidence_scores'])
                del method_data['confidence_scores']  # Nettoyer pour la sérialisation
            
            # Évolution temporelle par méthode
            daily_method_stats = defaultdict(lambda: defaultdict(int))
            
            for att in attendances:
                day = att.marked_at.date().isoformat()
                method = att.method.value
                daily_method_stats[day][method] += 1
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'method_stats': dict(method_stats),
                'daily_evolution': dict(daily_method_stats),
                'summary': {
                    'total_attendances': len(attendances),
                    'methods_used': list(method_stats.keys()),
                    'most_used_method': max(method_stats.keys(), key=lambda k: method_stats[k]['total']) if method_stats else None,
                    'face_recognition_usage': method_stats.get('face_recognition', {}).get('total', 0) / len(attendances) if attendances else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse méthodes: {e}")
            raise
    
    def generate_time_analysis(
        self,
        course_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Analyser les patterns temporels de présence"""
        try:
            attendances = self.db.query(Attendance).filter(
                and_(
                    Attendance.course_id == course_id,
                    func.date(Attendance.marked_at).between(start_date, end_date)
                )
            ).all()
            
            # Analyse par heure
            hourly_stats = defaultdict(lambda: {'total': 0, 'present': 0, 'late': 0, 'absent': 0})
            
            # Analyse par jour de la semaine
            weekday_stats = defaultdict(lambda: {'total': 0, 'present': 0, 'late': 0, 'absent': 0})
            
            # Analyse des retards
            late_patterns = []
            
            for att in attendances:
                hour = att.marked_at.hour
                weekday = att.marked_at.strftime('%A')
                
                hourly_stats[hour]['total'] += 1
                weekday_stats[weekday]['total'] += 1
                
                if att.status == AttendanceStatus.PRESENT:
                    hourly_stats[hour]['present'] += 1
                    weekday_stats[weekday]['present'] += 1
                elif att.status == AttendanceStatus.LATE:
                    hourly_stats[hour]['late'] += 1
                    weekday_stats[weekday]['late'] += 1
                    
                    # Analyser le retard
                    if att.scheduled_start_time and att.actual_arrival_time:
                        delay_minutes = (att.actual_arrival_time - att.scheduled_start_time).total_seconds() / 60
                        late_patterns.append({
                            'student_id': att.student_id,
                            'date': att.marked_at.date().isoformat(),
                            'delay_minutes': delay_minutes,
                            'hour': hour,
                            'weekday': weekday
                        })
                elif att.status == AttendanceStatus.ABSENT:
                    hourly_stats[hour]['absent'] += 1
                    weekday_stats[weekday]['absent'] += 1
            
            # Calculer les taux
            for stats in [hourly_stats, weekday_stats]:
                for period_data in stats.values():
                    if period_data['total'] > 0:
                        period_data['attendance_rate'] = (period_data['present'] + period_data['late']) / period_data['total']
                        period_data['punctuality_rate'] = period_data['present'] / (period_data['present'] + period_data['late']) if (period_data['present'] + period_data['late']) > 0 else 0
            
            # Analyse des retards
            late_analysis = {}
            if late_patterns:
                delays = [p['delay_minutes'] for p in late_patterns]
                late_analysis = {
                    'total_late_instances': len(late_patterns),
                    'avg_delay_minutes': sum(delays) / len(delays),
                    'max_delay_minutes': max(delays),
                    'min_delay_minutes': min(delays),
                    'most_late_hour': max(set(p['hour'] for p in late_patterns), key=lambda h: sum(1 for p in late_patterns if p['hour'] == h)),
                    'most_late_weekday': max(set(p['weekday'] for p in late_patterns), key=lambda d: sum(1 for p in late_patterns if p['weekday'] == d))
                }
            
            return {
                'course_id': course_id,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'hourly_patterns': dict(hourly_stats),
                'weekday_patterns': dict(weekday_stats),
                'late_analysis': late_analysis,
                'recommendations': self._generate_time_recommendations(hourly_stats, weekday_stats, late_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse temporelle: {e}")
            raise
    
    def _generate_time_recommendations(
        self,
        hourly_stats: Dict,
        weekday_stats: Dict,
        late_analysis: Dict
    ) -> List[str]:
        """Générer des recommandations basées sur l'analyse temporelle"""
        recommendations = []
        
        # Recommandations basées sur les heures
        if hourly_stats:
            best_hour = max(hourly_stats.keys(), key=lambda h: hourly_stats[h].get('attendance_rate', 0))
            worst_hour = min(hourly_stats.keys(), key=lambda h: hourly_stats[h].get('attendance_rate', 0))
            
            if hourly_stats[best_hour]['attendance_rate'] - hourly_stats[worst_hour]['attendance_rate'] > 0.2:
                recommendations.append(f"Considérer programmer plus de cours à {best_hour}h (meilleur taux de présence)")
        
        # Recommandations basées sur les jours
        if weekday_stats:
            best_day = max(weekday_stats.keys(), key=lambda d: weekday_stats[d].get('attendance_rate', 0))
            worst_day = min(weekday_stats.keys(), key=lambda d: weekday_stats[d].get('attendance_rate', 0))
            
            if weekday_stats[best_day]['attendance_rate'] - weekday_stats[worst_day]['attendance_rate'] > 0.15:
                recommendations.append(f"Le {best_day} montre le meilleur taux de présence")
                recommendations.append(f"Attention particulière nécessaire le {worst_day}")
        
        # Recommandations basées sur les retards
        if late_analysis and late_analysis.get('avg_delay_minutes', 0) > 15:
            recommendations.append("Retards fréquents détectés - considérer une période de grâce plus longue")
        
        return recommendations
