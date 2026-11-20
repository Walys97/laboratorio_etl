
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.controllers import analitica_controller
from app.database import get_db


# Creamos una aplicación independiente para las pruebas.
app = FastAPI()

# Registramos las rutas del controlador de analítica.
app.include_router(analitica_controller.router)


# Evitamos abrir una conexión real con la base de datos.
def override_get_db():
    yield object()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_analizar_columna_valida(monkeypatch):
    """Comprueba que se pueda analizar una columna existente."""

    def analisis_simulado(db, nombre):
        return {
            "columna": nombre,
            "tipo": "categorica"
        }

    monkeypatch.setattr(
        analitica_controller.analitica_service,
        "analizar_columna",
        analisis_simulado
    )

    respuesta = client.get("/api/v1/analitica/columna/genero")

    assert respuesta.status_code == 200
    assert respuesta.json()["columna"] == "genero"


def test_normalizar_nombre_columna(monkeypatch):
    """Comprueba que se eliminen espacios y se conviertan mayúsculas."""

    def analisis_simulado(db, nombre):
        return {
            "columna": nombre,
            "tipo": "categorica"
        }

    monkeypatch.setattr(
        analitica_controller.analitica_service,
        "analizar_columna",
        analisis_simulado
    )

    respuesta = client.get("/api/v1/analitica/columna/%20GENERO%20")

    assert respuesta.status_code == 200
    assert respuesta.json()["columna"] == "genero"


def test_columna_inexistente(monkeypatch):
    """Comprueba que una columna inexistente genere error 400."""

    monkeypatch.setattr(
        analitica_controller.analitica_service,
        "analizar_columna",
        lambda db, nombre: None
    )

    monkeypatch.setattr(
        analitica_controller.analitica_service,
        "obtener_columnas",
        lambda: ["genero", "nombre", "estado"]
    )

    respuesta = client.get("/api/v1/analitica/columna/columna_falsa")

    assert respuesta.status_code == 400
    assert "columnas_validas" in respuesta.json()["detail"]

def test_perfil_en_ambas_bases(monkeypatch):
    """Comprueba que el perfil exista en MongoDB y MySQL."""

    def perfil_simulado(db, id):
        return {
            "id": id,
            "vista_mongo": {"nombre": "Rick"},
            "vista_sql": {"nombre": "Rick"},
            "warning": None
        }

    monkeypatch.setattr(
        analitica_controller.analitica_service,
        "obtener_perfil_dual",
        perfil_simulado
    )

    respuesta = client.get("/api/v1/analitica/perfil/1")

    assert respuesta.status_code == 200
    assert respuesta.json()["vista_mongo"]["nombre"] == "Rick"
    assert respuesta.json()["vista_sql"]["nombre"] == "Rick"
    assert respuesta.json()["warning"] is None


def test_perfil_no_existe(monkeypatch):
    """Comprueba que un perfil inexistente genere error 404."""

    monkeypatch.setattr(
        analitica_controller.analitica_service,
        "obtener_perfil_dual",
        lambda db, id: None
    )

    respuesta = client.get("/api/v1/analitica/perfil/999999")

    assert respuesta.status_code == 404


def test_perfil_solo_en_mongo(monkeypatch):
    """Comprueba que se informe cuando el perfil solo está en MongoDB."""

    def perfil_simulado(db, id):
        return {
            "id": id,
            "vista_mongo": {"nombre": "Morty"},
            "vista_sql": None,
            "warning": "El personaje no existe en MySQL."
        }

    monkeypatch.setattr(
        analitica_controller.analitica_service,
        "obtener_perfil_dual",
        perfil_simulado
    )

    respuesta = client.get("/api/v1/analitica/perfil/2")

    assert respuesta.status_code == 200
    assert respuesta.json()["vista_mongo"]["nombre"] == "Morty"
    assert respuesta.json()["vista_sql"] is None
    assert respuesta.json()["warning"] is not None


def test_perfil_solo_en_mysql(monkeypatch):
    """Comprueba que se informe cuando el perfil solo está en MySQL."""

    def perfil_simulado(db, id):
        return {
            "id": id,
            "vista_mongo": None,
            "vista_sql": {"nombre": "Summer"},
            "warning": "El personaje no existe en MongoDB."
        }

    monkeypatch.setattr(
        analitica_controller.analitica_service,
        "obtener_perfil_dual",
        perfil_simulado
    )

    respuesta = client.get("/api/v1/analitica/perfil/3")

    assert respuesta.status_code == 200
    assert respuesta.json()["vista_mongo"] is None
    assert respuesta.json()["vista_sql"]["nombre"] == "Summer"
    assert respuesta.json()["warning"] is not None
