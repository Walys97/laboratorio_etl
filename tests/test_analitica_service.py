
from app.services import analitica_service


def test_analizar_columna_numerica_con_nulos(monkeypatch):
    """Comprueba las estadísticas numéricas cuando existen valores nulos."""

    monkeypatch.setattr(
        analitica_service,
        "obtener_columnas",
        lambda: ["edad"]
    )

    monkeypatch.setattr(
        analitica_service,
        "obtener_datos_columna",
        lambda db, nombre: [10, None, 20, 30]
    )

    resultado = analitica_service.analizar_columna(
        db=None,
        nombre_columna="edad"
    )

    assert resultado["tipo"] == "numerica"
    assert resultado["min"] == 10
    assert resultado["max"] == 30
    assert resultado["promedio"] == 20
    assert resultado["mediana"] == 20
    assert resultado["desviacion_std"] == 10
    assert resultado["nulos"] == 1


def test_analizar_columna_categorica_con_nulos(monkeypatch):
    """Comprueba la distribución de categorías cuando existen valores nulos."""

    monkeypatch.setattr(
        analitica_service,
        "obtener_columnas",
        lambda: ["especie"]
    )

    monkeypatch.setattr(
        analitica_service,
        "obtener_datos_columna",
        lambda db, nombre: ["humano", "alien", "humano", None]
    )

    resultado = analitica_service.analizar_columna(
        db=None,
        nombre_columna="especie"
    )

    assert resultado["tipo"] == "categorica"
    assert resultado["valores_unicos"] == 2
    assert resultado["distribucion"] == {
        "humano": 2,
        "alien": 1
    }
    assert resultado["valor_mas_comun"] == "humano"
    assert resultado["nulos"] == 1



def test_columna_booleana_todos_nulos(monkeypatch):
    """Comprueba una columna booleana cuyos valores son todos nulos."""

    monkeypatch.setattr(
        analitica_service,
        "obtener_columnas",
        lambda: ["esta_vivo"]
    )

    monkeypatch.setattr(
        analitica_service,
        "obtener_datos_columna",
        lambda db, nombre: [None, None, None]
    )

    resultado = analitica_service.analizar_columna(None, "esta_vivo")

    assert resultado["tipo"] == "booleana"
    assert resultado["true"] == 0
    assert resultado["false"] == 0
    assert resultado["nulos"] == 3


def test_columna_fecha_todos_nulos(monkeypatch):
    """Comprueba una columna de fecha cuyos valores son todos nulos."""

    monkeypatch.setattr(
        analitica_service,
        "obtener_columnas",
        lambda: ["fecha_creacion"]
    )

    monkeypatch.setattr(
        analitica_service,
        "obtener_datos_columna",
        lambda db, nombre: [None, None]
    )

    resultado = analitica_service.analizar_columna(None, "fecha_creacion")

    assert resultado["tipo"] == "fecha"
    assert resultado["min"] is None
    assert resultado["max"] is None
    assert resultado["rango_dias"] is None
    assert resultado["nulos"] == 2


def test_columna_numerica_todos_nulos(monkeypatch):
    """Comprueba una columna numérica cuyos valores son todos nulos."""

    monkeypatch.setattr(
        analitica_service,
        "obtener_columnas",
        lambda: ["total_episodios"]
    )

    monkeypatch.setattr(
        analitica_service,
        "obtener_datos_columna",
        lambda db, nombre: [None, None, None]
    )

    resultado = analitica_service.analizar_columna(None, "total_episodios")

    assert resultado["tipo"] == "numerica"
    assert resultado["min"] is None
    assert resultado["max"] is None
    assert resultado["promedio"] is None
    assert resultado["mediana"] is None
    assert resultado["desviacion_std"] is None
    assert resultado["nulos"] == 3


def test_columna_texto_todos_nulos(monkeypatch):
    """Comprueba una columna de texto cuyos valores son todos nulos."""

    monkeypatch.setattr(
        analitica_service,
        "obtener_columnas",
        lambda: ["estado"]
    )

    monkeypatch.setattr(
        analitica_service,
        "obtener_datos_columna",
        lambda db, nombre: [None, None]
    )

    resultado = analitica_service.analizar_columna(None, "estado")

    assert resultado["tipo"] == "texto"
    assert resultado["valores_unicos"] == 0
    assert resultado["nulos"] == 2