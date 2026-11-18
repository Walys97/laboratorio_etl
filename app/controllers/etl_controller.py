"""
Controller del pipeline ETL.
Rutas: extraccion (A), transformacion (B) y reset (C).
"""

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import etl_service
from ..views.schemas import (
    ExtraerRequest,
    ExtraerResponse,
    ResetResponse,
    TransformarResponse,
)
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


@router.delete("/reset", response_model=ResetResponse)
def reset(db: Session = Depends(get_db)):
    """
    Endpoint C - Limpieza total.

    Borra los documentos de MongoDB y vacia la tabla de MySQL con TRUNCATE.
    """
    return etl_service.resetear(db)


@router.post("/transformar", response_model=TransformarResponse)
def transformar(db: Session = Depends(get_db)):
    """
    Endpoint B - Transformacion y carga (ETL).

    Lee los documentos crudos de MongoDB, los aplana y limpia con Pandas
    y los inserta en MySQL. Es idempotente: no duplica filas al reejecutar.
    """
    try:
        return etl_service.transformar(db)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )