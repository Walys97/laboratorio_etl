"""
Controller del pipeline ETL.
Rutas: extraccion (A), transformacion (B) y reset (C).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/etl", tags=["ETL"])