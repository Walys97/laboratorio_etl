"""
Punto de entrada de la aplicacion.

Inicializa FastAPI, crea la tabla de MySQL si no existe
y registra las rutas de los controllers.
"""

from fastapi import FastAPI

from .controllers import analitica_controller, etl_controller
from .database import Base, engine
from .models import entidad_sql  # noqa: F401  importarlo registra la tabla en Base

# Crea la tabla en MySQL si todavia no existe.
# Si ya existe no la toca, asi que no se pierden datos.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Laboratorio Final - Pipeline ETL",
    description=(
        "Pipeline ETL que extrae datos de la API de Rick & Morty, "
        "los guarda crudos en MongoDB, los transforma con Pandas "
        "y los carga en MySQL. Incluye endpoints de analitica."
    ),
    version="1.0.0",
)

# Registro de las rutas de cada controller
app.include_router(etl_controller.router)
app.include_router(analitica_controller.router)


@app.get("/", tags=["Salud"])
def raiz():
    """Endpoint de salud: confirma que la aplicacion esta arriba."""
    return {
        "mensaje": "Pipeline ETL en funcionamiento",
        "documentacion": "/docs",
    }