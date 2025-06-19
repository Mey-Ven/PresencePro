"""
Routes API pour le service utilisateur
"""
from .students import router as students_router
from .teachers import router as teachers_router
from .parents import router as parents_router

__all__ = ["students_router", "teachers_router", "parents_router"]
