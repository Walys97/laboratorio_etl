
import pandas as pd

from datetime import date, datetime
from numbers import Number
from sqlalchemy.orm import Session

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
