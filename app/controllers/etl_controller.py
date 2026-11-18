"""
Controller del pipeline ETL.
Rutas: extraccion (A), transformacion (B) y reset (C).
"""

import requests
from fastapi import APIRouter, HTTPException, status

from ..services import etl_service
from ..views.schemas import ExtraerRequest, ExtraerResponse

router = APIRouter(prefix="/api/v1/etl", tags=["ETL"])


@router.post(
    "/extraer",
    response_model=ExtraerResponse,
    status_code=status.HTTP_201_CREATED,
)
def extraer(payload: ExtraerRequest):
    """
    Endpoint A - Extraccion (Staging).

    Descarga personajes de la API publica y los guarda crudos en MongoDB.
    Es idempotente: ejecutarlo varias veces no genera duplicados.
    """
    try:
        return etl_service.extraer(payload.cantidad)
    except requests.RequestException as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo consultar la API publica: {error}",
        )