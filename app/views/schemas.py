"""
Esquemas Pydantic.

Validan el JSON que entra a los endpoints y definen la forma del JSON que sale.
FastAPI los usa ademas para generar la documentacion automatica en /docs.
"""

from pydantic import BaseModel, Field


# ==================== Endpoint A: Extraccion ====================
class ExtraerRequest(BaseModel):
    """Cuerpo de la peticion POST /api/v1/etl/extraer."""

    cantidad: int = Field(
        ...,
        gt=0,
        description="Cuantos registros descargar de la API. Debe ser mayor que 0.",
        examples=[50],
    )


class ExtraerResponse(BaseModel):
    """Respuesta de POST /api/v1/etl/extraer."""

    mensaje: str
    nuevos: int
    ya_existentes: int
    fuente: str
    status: int


# ==================== Endpoint B: Transformacion y carga ====================
class TransformarResponse(BaseModel):
    """Respuesta de POST /api/v1/etl/transformar."""

    mensaje: str
    registros_procesados: int
    tabla_destino: str
    status: int


# ==================== Endpoint C: Reset ====================
class ResetResponse(BaseModel):
    """Respuesta de DELETE /api/v1/etl/reset."""

    mensaje: str
    mongo_docs_eliminados: int
    mysql_rows_eliminadas: int
    status: int