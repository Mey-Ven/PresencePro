"""
Service de calcul des statistiques
"""
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
import pandas as pd
import numpy as np
from scipy import stats

from app.core.database import (
    get_database, get_cache_key, get_from_cache, set_cache, 
    clear_cache_pattern, SessionLocal
)
from app.models.statistics import (
    AttendanceRecord, StatisticsCache, StudentStatistics, ClassStatistics,
    StatisticType, AggregationPeriod
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service de calcul des statistiques"""
    
    def __init__(self):
        self.cache_enabled = settings.cache_enabled
        self.cache_ttl = settings.cache_ttl
    
    async def get_student_statistics(
        self,
        student_id: str,
        start_date: date,
        end_date: date,
        statistics: List[StatisticType] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Calculer les statistiques pour un étudiant"""
        try:
            # Vérifier le cache
            cache_key = get_cache_key(
                "student_stats",
                student_id=student_id,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                stats=",".join(statistics or [])
            )
            
            if use_cache and self.cache_enabled:
                cached_data = get_from_cache(cache_key)
                if cached_data:
                    logger.info(f"Cache hit pour statistiques étudiant {student_id}")
                    return json.loads(cached_data)
            
            db = SessionLocal()
            
            # Récupérer les données de présence
            attendance_data = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.student_id == student_id,
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date
                )
            ).all()
            
            if not attendance_data:
                return self._empty_student_stats(student_id, start_date, end_date)
            
            # Calculer les statistiques de base
            stats_result = self._calculate_basic_student_stats(attendance_data)
            
            # Ajouter les statistiques spécifiques demandées
            if statistics:
                for stat_type in statistics:
                    if stat_type == StatisticType.WEEKLY_TRENDS:
                        stats_result["weekly_trends"] = self._calculate_weekly_trends(
                            attendance_data, start_date, end_date
                        )
                    elif stat_type == StatisticType.COURSE_COMPARISON:
                        stats_result["course_breakdown"] = self._calculate_course_breakdown(
                            attendance_data
                        )
                    elif stat_type == StatisticType.STUDENT_RANKING:
                        stats_result["class_ranking"] = await self._calculate_student_ranking(
                            student_id, start_date, end_date, db
                        )
            
            # Ajouter les métadonnées
            stats_result.update({
                "student_id": student_id,
                "period_start": start_date,
                "period_end": end_date,
                "generated_at": datetime.now(),
                "cache_hit": False
            })
            
            # Mettre en cache
            if self.cache_enabled:
                set_cache(cache_key, json.dumps(stats_result, default=str), self.cache_ttl)
            
            db.close()
            return stats_result
            
        except Exception as e:
            logger.error(f"Erreur calcul statistiques étudiant {student_id}: {e}")
            raise
    
    async def get_class_statistics(
        self,
        class_id: str,
        start_date: date,
        end_date: date,
        statistics: List[StatisticType] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Calculer les statistiques pour une classe"""
        try:
            # Vérifier le cache
            cache_key = get_cache_key(
                "class_stats",
                class_id=class_id,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                stats=",".join(statistics or [])
            )
            
            if use_cache and self.cache_enabled:
                cached_data = get_from_cache(cache_key)
                if cached_data:
                    logger.info(f"Cache hit pour statistiques classe {class_id}")
                    return json.loads(cached_data)
            
            db = SessionLocal()
            
            # Récupérer les données de présence pour la classe
            attendance_data = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.class_id == class_id,
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date
                )
            ).all()
            
            if not attendance_data:
                return self._empty_class_stats(class_id, start_date, end_date)
            
            # Calculer les statistiques de base
            stats_result = self._calculate_basic_class_stats(attendance_data)
            
            # Ajouter les statistiques spécifiques
            if statistics:
                for stat_type in statistics:
                    if stat_type == StatisticType.STUDENT_RANKING:
                        stats_result["student_rankings"] = self._calculate_class_student_rankings(
                            attendance_data
                        )
                    elif stat_type == StatisticType.WEEKLY_TRENDS:
                        stats_result["weekly_trends"] = self._calculate_class_weekly_trends(
                            attendance_data, start_date, end_date
                        )
                    elif stat_type == StatisticType.COURSE_COMPARISON:
                        stats_result["course_comparison"] = self._calculate_class_course_comparison(
                            attendance_data
                        )
            
            # Ajouter les métadonnées
            stats_result.update({
                "class_id": class_id,
                "period_start": start_date,
                "period_end": end_date,
                "generated_at": datetime.now(),
                "cache_hit": False
            })
            
            # Mettre en cache
            if self.cache_enabled:
                set_cache(cache_key, json.dumps(stats_result, default=str), self.cache_ttl)
            
            db.close()
            return stats_result
            
        except Exception as e:
            logger.error(f"Erreur calcul statistiques classe {class_id}: {e}")
            raise
    
    async def get_global_statistics(
        self,
        start_date: date,
        end_date: date,
        statistics: List[StatisticType] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Calculer les statistiques globales"""
        try:
            # Vérifier le cache
            cache_key = get_cache_key(
                "global_stats",
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                stats=",".join(statistics or [])
            )
            
            if use_cache and self.cache_enabled:
                cached_data = get_from_cache(cache_key)
                if cached_data:
                    logger.info("Cache hit pour statistiques globales")
                    return json.loads(cached_data)
            
            db = SessionLocal()
            
            # Récupérer toutes les données de présence
            attendance_data = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date
                )
            ).all()
            
            if not attendance_data:
                return self._empty_global_stats(start_date, end_date)
            
            # Calculer les statistiques de base
            stats_result = self._calculate_basic_global_stats(attendance_data)
            
            # Ajouter les statistiques spécifiques
            if statistics:
                for stat_type in statistics:
                    if stat_type == StatisticType.MONTHLY_TRENDS:
                        stats_result["monthly_trends"] = self._calculate_monthly_trends(
                            attendance_data, start_date, end_date
                        )
                    elif stat_type == StatisticType.CLASS_AVERAGE:
                        stats_result["class_rankings"] = self._calculate_global_class_rankings(
                            attendance_data
                        )
                    elif stat_type == StatisticType.STUDENT_RANKING:
                        stats_result["top_performers"] = self._calculate_top_performers(
                            attendance_data
                        )
            
            # Ajouter les métadonnées
            stats_result.update({
                "period_start": start_date,
                "period_end": end_date,
                "generated_at": datetime.now(),
                "cache_hit": False
            })
            
            # Mettre en cache
            if self.cache_enabled:
                set_cache(cache_key, json.dumps(stats_result, default=str), self.cache_ttl)
            
            db.close()
            return stats_result
            
        except Exception as e:
            logger.error(f"Erreur calcul statistiques globales: {e}")
            raise
    
    def _calculate_basic_student_stats(self, attendance_data: List[AttendanceRecord]) -> Dict[str, Any]:
        """Calculer les statistiques de base pour un étudiant"""
        total_courses = len(attendance_data)
        present_count = sum(1 for record in attendance_data if record.status == "present")
        absent_count = sum(1 for record in attendance_data if record.status == "absent")
        late_count = sum(1 for record in attendance_data if record.status == "late")
        excused_count = sum(1 for record in attendance_data if record.is_justified)
        
        attendance_rate = (present_count / total_courses * 100) if total_courses > 0 else 0
        absence_rate = (absent_count / total_courses * 100) if total_courses > 0 else 0
        tardiness_rate = (late_count / total_courses * 100) if total_courses > 0 else 0
        justification_rate = (excused_count / absent_count * 100) if absent_count > 0 else 0
        
        return {
            "total_courses": total_courses,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "justified_absences": excused_count,
            "unjustified_absences": absent_count - excused_count,
            "attendance_rate": round(attendance_rate, 2),
            "absence_rate": round(absence_rate, 2),
            "tardiness_rate": round(tardiness_rate, 2),
            "justification_rate": round(justification_rate, 2)
        }
    
    def _calculate_basic_class_stats(self, attendance_data: List[AttendanceRecord]) -> Dict[str, Any]:
        """Calculer les statistiques de base pour une classe"""
        df = pd.DataFrame([{
            "student_id": record.student_id,
            "status": record.status,
            "is_justified": record.is_justified
        } for record in attendance_data])
        
        total_students = df["student_id"].nunique()
        total_records = len(df)
        
        # Calculer les taux par étudiant
        student_stats = df.groupby("student_id").agg({
            "status": lambda x: (x == "present").sum() / len(x) * 100
        }).rename(columns={"status": "attendance_rate"})
        
        return {
            "total_students": total_students,
            "total_records": total_records,
            "average_attendance_rate": round(student_stats["attendance_rate"].mean(), 2),
            "median_attendance_rate": round(student_stats["attendance_rate"].median(), 2),
            "std_attendance_rate": round(student_stats["attendance_rate"].std(), 2),
            "best_attendance_rate": round(student_stats["attendance_rate"].max(), 2),
            "worst_attendance_rate": round(student_stats["attendance_rate"].min(), 2),
            "present_count": len(df[df["status"] == "present"]),
            "absent_count": len(df[df["status"] == "absent"]),
            "late_count": len(df[df["status"] == "late"])
        }
    
    def _calculate_basic_global_stats(self, attendance_data: List[AttendanceRecord]) -> Dict[str, Any]:
        """Calculer les statistiques de base globales"""
        df = pd.DataFrame([{
            "student_id": record.student_id,
            "class_id": record.class_id,
            "course_id": record.course_id,
            "status": record.status,
            "is_justified": record.is_justified
        } for record in attendance_data])
        
        total_students = df["student_id"].nunique()
        total_classes = df["class_id"].nunique()
        total_courses = df["course_id"].nunique()
        total_records = len(df)
        
        present_count = len(df[df["status"] == "present"])
        absent_count = len(df[df["status"] == "absent"])
        late_count = len(df[df["status"] == "late"])
        
        global_attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        
        return {
            "total_students": total_students,
            "total_classes": total_classes,
            "total_courses": total_courses,
            "total_records": total_records,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "global_attendance_rate": round(global_attendance_rate, 2)
        }
    
    def _calculate_weekly_trends(
        self,
        attendance_data: List[AttendanceRecord],
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Calculer les tendances hebdomadaires"""
        df = pd.DataFrame([{
            "date": record.date,
            "status": record.status
        } for record in attendance_data])

        df["week"] = pd.to_datetime(df["date"]).dt.isocalendar().week
        df["year"] = pd.to_datetime(df["date"]).dt.year

        weekly_stats = df.groupby(["year", "week"]).agg({
            "status": [
                lambda x: (x == "present").sum(),
                lambda x: (x == "absent").sum(),
                lambda x: len(x)
            ]
        }).reset_index()

        weekly_stats.columns = ["year", "week", "present", "absent", "total"]
        weekly_stats["attendance_rate"] = (weekly_stats["present"] / weekly_stats["total"] * 100).round(2)

        return weekly_stats.to_dict("records")

    def _calculate_course_breakdown(self, attendance_data: List[AttendanceRecord]) -> List[Dict[str, Any]]:
        """Calculer la répartition par cours"""
        df = pd.DataFrame([{
            "course_id": record.course_id,
            "status": record.status
        } for record in attendance_data])

        course_stats = df.groupby("course_id").agg({
            "status": [
                lambda x: len(x),
                lambda x: (x == "present").sum(),
                lambda x: (x == "absent").sum()
            ]
        }).reset_index()

        course_stats.columns = ["course_id", "total", "present", "absent"]
        course_stats["attendance_rate"] = (course_stats["present"] / course_stats["total"] * 100).round(2)

        return course_stats.to_dict("records")

    async def _calculate_student_ranking(
        self,
        student_id: str,
        start_date: date,
        end_date: date,
        db: Session
    ) -> Dict[str, Any]:
        """Calculer le classement de l'étudiant dans sa classe"""
        # Récupérer la classe de l'étudiant
        student_class = db.query(AttendanceRecord.class_id).filter(
            AttendanceRecord.student_id == student_id
        ).first()

        if not student_class:
            return {"rank": None, "percentile": None, "total_students": 0}

        # Calculer les taux de présence de tous les étudiants de la classe
        class_data = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.class_id == student_class.class_id,
                AttendanceRecord.date >= start_date,
                AttendanceRecord.date <= end_date
            )
        ).all()

        df = pd.DataFrame([{
            "student_id": record.student_id,
            "status": record.status
        } for record in class_data])

        student_rates = df.groupby("student_id").agg({
            "status": lambda x: (x == "present").sum() / len(x) * 100
        }).reset_index()
        student_rates.columns = ["student_id", "attendance_rate"]

        # Calculer le rang
        student_rates = student_rates.sort_values("attendance_rate", ascending=False)
        student_rates["rank"] = range(1, len(student_rates) + 1)

        student_rank = student_rates[student_rates["student_id"] == student_id]

        if student_rank.empty:
            return {"rank": None, "percentile": None, "total_students": len(student_rates)}

        rank = student_rank.iloc[0]["rank"]
        percentile = (len(student_rates) - rank + 1) / len(student_rates) * 100

        return {
            "rank": int(rank),
            "percentile": round(percentile, 2),
            "total_students": len(student_rates)
        }
    
    def _empty_student_stats(self, student_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Retourner des statistiques vides pour un étudiant"""
        return {
            "student_id": student_id,
            "period_start": start_date,
            "period_end": end_date,
            "total_courses": 0,
            "present_count": 0,
            "absent_count": 0,
            "late_count": 0,
            "attendance_rate": 0.0,
            "generated_at": datetime.now(),
            "cache_hit": False
        }
    
    def _empty_class_stats(self, class_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Retourner des statistiques vides pour une classe"""
        return {
            "class_id": class_id,
            "period_start": start_date,
            "period_end": end_date,
            "total_students": 0,
            "total_records": 0,
            "average_attendance_rate": 0.0,
            "generated_at": datetime.now(),
            "cache_hit": False
        }
    
    def _empty_global_stats(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Retourner des statistiques globales vides"""
        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_students": 0,
            "total_classes": 0,
            "total_records": 0,
            "global_attendance_rate": 0.0,
            "generated_at": datetime.now(),
            "cache_hit": False
        }
    
    def _calculate_class_student_rankings(self, attendance_data: List[AttendanceRecord]) -> List[Dict[str, Any]]:
        """Calculer le classement des étudiants dans une classe"""
        df = pd.DataFrame([{
            "student_id": record.student_id,
            "status": record.status
        } for record in attendance_data])

        student_rates = df.groupby("student_id").agg({
            "status": lambda x: (x == "present").sum() / len(x) * 100
        }).reset_index()
        student_rates.columns = ["student_id", "attendance_rate"]

        # Trier par taux de présence
        student_rates = student_rates.sort_values("attendance_rate", ascending=False)
        student_rates["rank"] = range(1, len(student_rates) + 1)

        return student_rates.to_dict("records")

    def _calculate_class_weekly_trends(
        self,
        attendance_data: List[AttendanceRecord],
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Calculer les tendances hebdomadaires pour une classe"""
        return self._calculate_weekly_trends(attendance_data, start_date, end_date)

    def _calculate_class_course_comparison(self, attendance_data: List[AttendanceRecord]) -> List[Dict[str, Any]]:
        """Calculer la comparaison par cours pour une classe"""
        return self._calculate_course_breakdown(attendance_data)

    def _calculate_monthly_trends(
        self,
        attendance_data: List[AttendanceRecord],
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Calculer les tendances mensuelles"""
        df = pd.DataFrame([{
            "date": record.date,
            "status": record.status
        } for record in attendance_data])

        df["month"] = pd.to_datetime(df["date"]).dt.month
        df["year"] = pd.to_datetime(df["date"]).dt.year

        monthly_stats = df.groupby(["year", "month"]).agg({
            "status": [
                lambda x: (x == "present").sum(),
                lambda x: (x == "absent").sum(),
                lambda x: len(x)
            ]
        }).reset_index()

        monthly_stats.columns = ["year", "month", "present", "absent", "total"]
        monthly_stats["attendance_rate"] = (monthly_stats["present"] / monthly_stats["total"] * 100).round(2)

        return monthly_stats.to_dict("records")

    def _calculate_global_class_rankings(self, attendance_data: List[AttendanceRecord]) -> List[Dict[str, Any]]:
        """Calculer le classement des classes"""
        df = pd.DataFrame([{
            "class_id": record.class_id,
            "status": record.status
        } for record in attendance_data])

        class_rates = df.groupby("class_id").agg({
            "status": lambda x: (x == "present").sum() / len(x) * 100
        }).reset_index()
        class_rates.columns = ["class_id", "attendance_rate"]

        # Trier par taux de présence
        class_rates = class_rates.sort_values("attendance_rate", ascending=False)
        class_rates["rank"] = range(1, len(class_rates) + 1)

        return class_rates.to_dict("records")

    def _calculate_top_performers(self, attendance_data: List[AttendanceRecord]) -> List[Dict[str, Any]]:
        """Calculer les meilleurs étudiants"""
        df = pd.DataFrame([{
            "student_id": record.student_id,
            "status": record.status
        } for record in attendance_data])

        student_rates = df.groupby("student_id").agg({
            "status": lambda x: (x == "present").sum() / len(x) * 100
        }).reset_index()
        student_rates.columns = ["student_id", "attendance_rate"]

        # Prendre les 10 meilleurs
        top_performers = student_rates.sort_values("attendance_rate", ascending=False).head(10)

        return top_performers.to_dict("records")

    async def invalidate_cache(self, pattern: str = None):
        """Invalider le cache"""
        if not self.cache_enabled:
            return 0

        pattern = pattern or "*_stats:*"
        return clear_cache_pattern(pattern)


# Instance globale du service
statistics_service = StatisticsService()
