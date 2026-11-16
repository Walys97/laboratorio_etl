"""
Controller de analitica.
Rutas: analisis por columna (D) y perfil dual Mongo/MySQL (E).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analitica", tags=["Analitica"])