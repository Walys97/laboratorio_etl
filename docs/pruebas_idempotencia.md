# Prueba de idempotencia del Endpoint B

1. `DELETE /api/v1/etl/reset` → Mongo y MySQL vacíos.
2. `POST /api/v1/etl/extraer` con `{"cantidad": 50}` → 50 documentos nuevos.
3. `POST /api/v1/etl/transformar` → 50 registros procesados.
4. `POST /api/v1/etl/transformar` otra vez → 50 registros procesados.

Verificación en DBeaver:
- `SELECT COUNT(*) FROM personajes_master;` → 50
- Duplicados por PK → 0