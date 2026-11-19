
"""
Controller de analitica.
Rutas: analisis por columna (D) y perfil dual Mongo/MySQL (E).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import analitica_service

router = APIRouter(prefix="/api/v1/analitica", tags=["Analitica"])


@router.get("/columna/{nombre}")
def analizar_columna(
    nombre: str,
    db: Session = Depends(get_db)
):
    """
    Analiza una columna de la tabla Personaje.
    """

    resultado = analitica_service.analizar_columna(db, nombre)

    if resultado is None:
        columnas = analitica_service.obtener_columnas()

        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": f"La columna '{nombre}' no existe.",
                "columnas_validas": columnas
            }
        )

    return resultado
