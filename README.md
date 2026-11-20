# Laboratorio Final (2) — Pipeline ETL con FastAPI

Aplicación backend que orquesta un proceso **ETL completo** y expone capacidades
analíticas sobre los datos cargados.

**Curso:** Bases de Datos para Ciencia de Datos — Universidad de Antioquia
**Docente:** Miguel Ramos García
**Equipo 6**

## Flujo de datos

```
API pública (Rick & Morty)  →  MongoDB (crudo)  →  Pandas  →  MySQL (limpio)
        Fuente                    Staging         Transform     Data Warehouse
```

- **Fuente:** [Rick & Morty API](https://rickandmortyapi.com/api/character) — pública, sin autenticación.
- **Staging (NoSQL):** MongoDB guarda el JSON completo tal como llega.
- **Data Warehouse (SQL):** MySQL guarda los datos aplanados y tipados.

## Integrantes y responsabilidades

| Integrante | Responsabilidad |
|---|---|
| **Walys Vera Herrera** | Base del proyecto (estructura MVC, `config.py`, `database.py`, modelo SQLAlchemy, esquemas Pydantic, `main.py`) · **Endpoint A: Extracción** · **Endpoint C: Reset** |
| **Esteban Ramírez** | **Endpoint B: Transformación y carga** (lectura desde Mongo, aplanamiento con Pandas, manejo de nulos, carga idempotente en MySQL) |
| **Luis Fernando Grajales** | **Endpoint D: Análisis por columna** (detección dinámica de tipos) · **Endpoint E: Perfil dual Mongo/MySQL** |

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/etl/extraer` | Descarga de la API y guarda crudo en MongoDB |
| `POST` | `/api/v1/etl/transformar` | Lee Mongo, limpia con Pandas y carga en MySQL |
| `DELETE` | `/api/v1/etl/reset` | Borra Mongo y hace TRUNCATE en MySQL |
| `GET` | `/api/v1/analitica/columna/{nombre}` | Análisis estadístico según el tipo de columna |
| `GET` | `/api/v1/analitica/perfil/{id}` | Mismo registro visto desde Mongo y desde MySQL |

### Ejemplos

**Extracción** — `POST /api/v1/etl/extraer`

```json
// Request
{ "cantidad": 50 }

// Response 201
{
  "mensaje": "Datos extraidos exitosamente",
  "nuevos": 50,
  "ya_existentes": 0,
  "fuente": "Rick & Morty API",
  "status": 201
}
```

**Reset** — `DELETE /api/v1/etl/reset`

```json
// Response 200
{
  "mensaje": "Sistema reseteado correctamente",
  "mongo_docs_eliminados": 50,
  "mysql_rows_eliminadas": 50,
  "status": 200
}
```

## Tabla destino en MySQL

Tabla `personajes_master`, 11 columnas:

| Columna | Tipo | Origen |
|---|---|---|
| `id_personaje` | INT (PK) | `id` de la API — **misma PK que el `_id` de Mongo** |
| `nombre` | VARCHAR(150) | `name` |
| `estado` | VARCHAR(50) | `status` |
| `especie` | VARCHAR(50) | `species` |
| `genero` | VARCHAR(50) | `gender` |
| `tipo` | VARCHAR(100) | `type` |
| `origen_nombre` | VARCHAR(150) | aplanado de `origin.name` |
| `ubicacion_nombre` | VARCHAR(150) | aplanado de `location.name` |
| `total_episodios` | INT | derivada: tamaño del arreglo `episode` |
| `esta_vivo` | BOOLEAN | derivada: `status == "Alive"` |
| `fecha_creacion` | DATE | `created` |

La Primary Key **no es autoincremental**: es el `id` que viene de la API. Eso garantiza
que un mismo registro tenga el mismo identificador en MongoDB y en MySQL, que es lo que
permite cruzarlos desde el endpoint de Perfil Dual.

## Estructura del proyecto

```
laboratorio_etl/
├── .env                      credenciales (NO se sube al repositorio)
├── .gitignore
├── requirements.txt
└── app/
    ├── main.py               inicializa FastAPI y registra routers
    ├── config.py             lee las variables del .env
    ├── database.py           conexiones a MongoDB y MySQL
    ├── controllers/
    │   ├── etl_controller.py         rutas del pipeline ETL
    │   └── analitica_controller.py   rutas de analítica
    ├── models/
    │   └── entidad_sql.py    tabla de MySQL con SQLAlchemy
    ├── services/
    │   ├── etl_service.py            lógica del ETL
    │   └── analitica_service.py      lógica de la analítica
    └── views/
        └── schemas.py        esquemas Pydantic
```

## Requisitos previos

- Python 3.10 o superior
- MongoDB Community Server (local) + MongoDB Compass
- MySQL Server (local) + DBeaver

## Cómo ejecutarlo

**1. Clonar el repositorio**

```bash
git clone https://github.com/Walys97/laboratorio_etl.git
cd laboratorio_etl
```

**2. Crear y activar el entorno virtual**

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac / Linux
source venv/bin/activate
```

**3. Instalar las dependencias**

```bash
pip install -r requirements.txt
```

**4. Crear la base de datos en MySQL**

```sql
CREATE DATABASE laboratorio_etl;
GRANT ALL PRIVILEGES ON laboratorio_etl.* TO 'tu_usuario'@'localhost';
FLUSH PRIVILEGES;
```

**5. Crear el archivo `.env`** en la raíz del proyecto

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=laboratorio_etl_db
MONGO_COLLECTION=raw_data

MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_contrasena
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=laboratorio_etl

API_URL=https://rickandmortyapi.com/api/character
```

**6. Levantar el servidor**

```bash
uvicorn app.main:app --reload
```

La documentación interactiva queda en **http://localhost:8000/docs**

## Cómo probar el pipeline completo

1. `DELETE /api/v1/etl/reset` — deja el sistema limpio
2. `POST /api/v1/etl/extraer` con `{"cantidad": 50}` — debe responder `nuevos: 50`
3. `POST /api/v1/etl/extraer` otra vez — debe responder `nuevos: 0` (**idempotencia**)
4. `POST /api/v1/etl/transformar` — carga los datos limpios en MySQL
5. `POST /api/v1/etl/transformar` otra vez — no debe duplicar filas
6. `GET /api/v1/analitica/columna/especie` — análisis de una columna categórica
7. `GET /api/v1/analitica/perfil/1` — el mismo registro en las dos bases

## Decisiones técnicas

- **MongoDB para el staging** porque el JSON de la API trae objetos anidados
  (`origin`, `location`) y arreglos (`episode`). Una base relacional exigiría
  descomponerlos en varias tablas antes de poder guardarlos; Mongo permite
  almacenar el documento completo y decidir después qué extraer.
- **`replace_one` con `upsert=True`** en vez de `insert_one`: si el documento ya
  existe lo reemplaza, de modo que ejecutar la extracción varias veces nunca duplica.
- **`TRUNCATE` y no `DROP`** en el reset: vacía la tabla pero conserva su estructura
  y su Primary Key, lista para el siguiente pipeline.
- **`autoincrement=False`** en la Primary Key: el identificador lo define la API,
  no MySQL, para que las dos bases usen la misma llave.
- **Credenciales en `.env`**, excluido del repositorio por `.gitignore`.
- **Nulos distintos según el tipo de columna**: el texto categórico se rellena con
  `"N/A"`; los numéricos y las fechas quedan en `NULL`. Rellenar con 0 distorsionaría
  el promedio y la mediana del análisis por columna, y `"N/A"` no es una fecha válida.
- **`INSERT ... ON DUPLICATE KEY UPDATE` en lotes** para cargar en MySQL, en vez de
  `df.to_sql(if_exists="replace")`: el upsert evita duplicados al reejecutar
  `/transformar` y conserva la tabla y su Primary Key, que `replace` destruiría.
- **`Base.metadata.create_all` al inicio de `/transformar`**: si la tabla no existe se
  crea con el modelo de SQLAlchemy (con su PK), así el pipeline no depende de que
  alguien la haya creado a mano.