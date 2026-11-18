"""
Logica del pipeline ETL.

Endpoint A (Extract): descarga personajes de la API publica
y los guarda crudos en MongoDB, sin transformar.
"""

import requests

from ..config import API_NOMBRE, API_URL
from ..database import get_mongo


def descargar_personajes(cantidad: int) -> list[dict]:
    """
    Pide personajes a la API publica recorriendo las paginas
    necesarias hasta juntar la cantidad solicitada.
    """
    personajes = []
    pagina = 1

    while len(personajes) < cantidad:
        respuesta = requests.get(API_URL, params={"page": pagina}, timeout=30)
        respuesta.raise_for_status()   # corta si la API responde con error
        datos = respuesta.json()

        personajes.extend(datos["results"])

        # Si la API ya no tiene mas paginas, paramos aunque falten registros
        if datos["info"]["next"] is None:
            break
        pagina += 1

    # Devolvemos exactamente la cantidad pedida, ni una mas
    return personajes[:cantidad]


def guardar_crudos(personajes: list[dict]) -> tuple[int, int]:
    """
    Guarda cada personaje TAL CUAL llega de la API en MongoDB.

    Usa el id de la API como _id del documento por dos razones:
      1. Idempotencia: si el documento ya existe se reemplaza, no se duplica.
      2. Permite cruzar el registro con MySQL en el endpoint de Perfil Dual.

    Devuelve una tupla (nuevos, ya_existentes).
    """
    coleccion = get_mongo()
    nuevos = 0
    ya_existentes = 0

    for personaje in personajes:
        documento = dict(personaje)            # copia del JSON crudo
        documento["_id"] = personaje["id"]     # el id de la API es la llave

        resultado = coleccion.replace_one(
            {"_id": documento["_id"]},
            documento,
            upsert=True,
        )

        # upserted_id solo tiene valor cuando se inserto un documento nuevo
        if resultado.upserted_id is not None:
            nuevos += 1
        else:
            ya_existentes += 1

    return nuevos, ya_existentes


def extraer(cantidad: int) -> dict:
    """
    Orquesta la extraccion completa: descarga de la API y carga cruda en Mongo.
    """
    personajes = descargar_personajes(cantidad)
    nuevos, ya_existentes = guardar_crudos(personajes)

    return {
        "mensaje": "Datos extraidos exitosamente",
        "nuevos": nuevos,
        "ya_existentes": ya_existentes,
        "fuente": API_NOMBRE,
        "status": 201,
    }