
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
