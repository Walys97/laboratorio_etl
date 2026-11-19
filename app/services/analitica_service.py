
import pandas as pd

from datetime import date, datetime
from numbers import Number
from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Session
from ..database import get_mongo
from ..models.entidad_sql import Personaje


def obtener_columnas():
    """
    Obtiene los nombres de las columnas de la tabla Personaje.
    """
    return [columna.name for columna in Personaje.__table__.columns]


def obtener_datos_columna(db: Session, nombre_columna: str):
    """
    Obtiene todos los valores de una columna de la tabla Personaje.
    """
    if nombre_columna not in obtener_columnas():
        return None

    columna = getattr(Personaje, nombre_columna)

    resultados = db.query(columna).all()

    # Convierte las tuplas de SQLAlchemy en una lista de valores.
    return [fila[0] for fila in resultados]


def analizar_columna(db: Session, nombre_columna: str):
    """
    Analiza una columna de la tabla Personaje y determina
    automáticamente su tipo de información.
    """

    # 1. Verificar que la columna exista.
    if nombre_columna not in obtener_columnas():
        return None

    # 2. Obtener los valores de la columna.
    valores = obtener_datos_columna(db, nombre_columna)

    # 3. Separar los valores nulos de los valores válidos.
    datos = [valor for valor in valores if valor is not None]
    nulos = len(valores) - len(datos)

    #  Si todos los valores son nulos, identificar el tipo
    # usando la estructura definida en el modelo de SQLAlchemy.
    if not datos:
        columna_sql = Personaje.__table__.columns[nombre_columna]
        tipo_sql = columna_sql.type

        # Las columnas booleanas se revisan antes que las numéricas.
        if isinstance(tipo_sql, Boolean):
            return {
                "columna": nombre_columna,
                "tipo": "booleana",
                "true": 0,
                "false": 0,
                "nulos": nulos
            }

        elif isinstance(tipo_sql, Date):
            return {
                "columna": nombre_columna,
                "tipo": "fecha",
                "min": None,
                "max": None,
                "rango_dias": None,
                "nulos": nulos
            }

        elif isinstance(tipo_sql, Integer):
            return {
                "columna": nombre_columna,
                "tipo": "numerica",
                "min": None,
                "max": None,
                "promedio": None,
                "mediana": None,
                "desviacion_std": None,
                "nulos": nulos
            }

        elif isinstance(tipo_sql, String):
            return {
                "columna": nombre_columna,
                "tipo": "texto",
                "valores_unicos": 0,
                "nulos": nulos
            }



    # 4. Identificar si los datos son fechas.
    if datos and all(isinstance(valor, (date, datetime)) for valor in datos):
        minimo = min(datos)
        maximo = max(datos)

        return {
            "columna": nombre_columna,
            "tipo": "fecha",
            "min": minimo,
            "max": maximo,
            "rango_dias": (maximo - minimo).days,
            "nulos": nulos
        }

    # 5. Identificar si los datos son booleanos.
    # En MySQL, los booleanos también pueden aparecer como 0 y 1.
    son_booleanos = (
        datos
        and all(isinstance(valor, (bool, Number)) for valor in datos)
        and set(datos).issubset({0, 1, False, True})
    )

    if son_booleanos:
        return {
            "columna": nombre_columna,
            "tipo": "booleana",
            "true": sum(valor == 1 for valor in datos),
            "false": sum(valor == 0 for valor in datos),
            "nulos": nulos
        }

    # 6. Identificar variables numéricas.
    son_numericos = (
        datos
        and all(isinstance(valor, Number) and not isinstance(valor, bool)
                for valor in datos)
    )

    if son_numericos:
        serie = pd.Series(datos)

        return {
            "columna": nombre_columna,
            "tipo": "numerica",
            "min": serie.min().item() if hasattr(serie.min(), "item") else serie.min(),
            "max": serie.max().item() if hasattr(serie.max(), "item") else serie.max(),
            "promedio": serie.mean().item() if hasattr(serie.mean(), "item") else serie.mean(),
            "mediana": serie.median().item() if hasattr(serie.median(), "item") else serie.median(),
            "desviacion_std": serie.std().item() if hasattr(serie.std(), "item") else serie.std(),
            "nulos": nulos
        }

    # 7. Identificar variables de texto.
    if datos:
        valores_unicos = len(set(datos))

        # Si todos los valores son diferentes, se considera texto libre.
        if valores_unicos == len(datos):
            return {
                "columna": nombre_columna,
                "tipo": "texto",
                "valores_unicos": valores_unicos,
                "nulos": nulos
            }

    # 8. Si no cumple las condiciones anteriores, se considera categórica.
    distribucion = pd.Series(datos).value_counts().to_dict() if datos else {}

    valor_mas_comun = (
        pd.Series(datos).mode().iloc[0] if datos else None
    )

    return {
        "columna": nombre_columna,
        "tipo": "categorica",
        "valores_unicos": len(set(datos)),
        "distribucion": distribucion,
        "valor_mas_comun": valor_mas_comun,
        "nulos": nulos
    }



def obtener_perfil_dual(db: Session, personaje_id: int):
    """
    Busca un personaje simultaneamente en MongoDB y MySQL.
    """

    # 1. Obtener la coleccion de MongoDB.
    coleccion = get_mongo()

    # 2. Buscar el personaje en MongoDB usando su _id.
    vista_mongo = coleccion.find_one({"_id": personaje_id})

    # 3. Buscar el mismo personaje en MySQL.
    vista_sql = db.query(Personaje).filter(
        Personaje.id_personaje == personaje_id
    ).first()

    # 4. Si no existe en ninguna de las dos bases.
    if vista_mongo is None and vista_sql is None:
        return None

    # 5. Preparar la vista de MongoDB.
    if vista_mongo is not None:
        vista_mongo["_id"] = str(vista_mongo["_id"])

    # 6. Preparar la vista de MySQL.
    if vista_sql is not None:
        vista_sql = {
            columna.name: getattr(vista_sql, columna.name)
            for columna in Personaje.__table__.columns
        }

    # 7. Identificar posibles inconsistencias.
    warning = None

    if vista_mongo is None:
        warning = "El personaje existe en MySQL, pero no en MongoDB."

    elif vista_sql is None:
        warning = "El personaje existe en MongoDB, pero no en MySQL."

    # 8. Construir la respuesta.
    return {
        "id": personaje_id,
        "vista_mongo": vista_mongo,
        "vista_sql": vista_sql,
        "warning": warning
    }
