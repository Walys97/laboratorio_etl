"""
Modelo de la tabla destino en MySQL (Data Warehouse).

La Primary Key es el mismo id que trae la API y que se usa como _id en MongoDB.
Eso permite cruzar un mismo registro entre las dos bases (endpoint de Perfil Dual).
"""

from sqlalchemy import Boolean, Column, Date, Integer, String

from ..config import TABLA_SQL
from ..database import Base


class Personaje(Base):
    """Un personaje de Rick & Morty, ya limpio y aplanado."""

    __tablename__ = TABLA_SQL

    # ---- Primary Key explicita ----
    # autoincrement=False: NO la genera MySQL, viene de la API.
    id_personaje = Column(Integer, primary_key=True, autoincrement=False)

    # ---- Columnas de texto (vienen directo del JSON) ----
    nombre = Column(String(150), nullable=False)
    estado = Column(String(50))
    especie = Column(String(50))
    genero = Column(String(50))
    tipo = Column(String(100))

    # ---- Columnas aplanadas desde objetos anidados ----
    origen_nombre = Column(String(150))        # viene de origin["name"]
    ubicacion_nombre = Column(String(150))     # viene de location["name"]

    # ---- Columnas derivadas (calculadas en la transformacion) ----
    total_episodios = Column(Integer)          # cuantos episodios tiene el arreglo episode
    esta_vivo = Column(Boolean)                # True si estado == "Alive"

    # ---- Fecha ----
    fecha_creacion = Column(Date)              # viene de created

    def __repr__(self):
        return f"<Personaje {self.id_personaje} - {self.nombre}>"