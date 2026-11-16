"""
Conexiones a las dos bases de datos del pipeline ETL.

- MongoDB: guarda el JSON crudo tal como llega de la API (Staging).
- MySQL: guarda los datos ya limpios y estructurados (Data Warehouse).
"""

from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL, MONGO_COLLECTION, MONGO_DB, MONGO_URI

# ==================== MongoDB (NoSQL) ====================
cliente_mongo = MongoClient(MONGO_URI)
base_mongo = cliente_mongo[MONGO_DB]
coleccion_raw = base_mongo[MONGO_COLLECTION]


def get_mongo():
    """Devuelve la coleccion de MongoDB donde viven los documentos crudos."""
    return coleccion_raw


# ==================== MySQL (SQL) ====================
# El engine es el motor de conexion.
# pool_pre_ping=True revisa que la conexion siga viva antes de usarla.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Fabrica de sesiones: cada peticion HTTP abre y cierra la suya.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredan los modelos (las tablas de MySQL).
Base = declarative_base()


def get_db():
    """
    Dependencia de FastAPI: entrega una sesion de MySQL al endpoint
    y la cierra al terminar, aunque la peticion falle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()