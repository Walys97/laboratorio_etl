"""
Configuracion central del proyecto.
Lee las credenciales desde el archivo .env para no dejarlas escritas en el codigo.
"""

import os

from dotenv import load_dotenv

# Carga el contenido del archivo .env en las variables de entorno
load_dotenv()

# ---------- MongoDB (Staging: datos crudos) ----------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "laboratorio_etl_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "raw_data")

# ---------- MySQL (Data Warehouse: datos transformados) ----------
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "laboratorio_etl")

# Cadena de conexion que SQLAlchemy usa para hablar con MySQL
DATABASE_URL = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

# ---------- API publica (fuente de datos) ----------
API_URL = os.getenv("API_URL", "https://rickandmortyapi.com/api/character")
API_NOMBRE = "Rick & Morty API"

# Nombre de la tabla destino en MySQL
TABLA_SQL = "personajes_master"