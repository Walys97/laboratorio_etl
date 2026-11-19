-- Total de filas y duplicados (debe ser 0)
SELECT COUNT(*) AS total FROM personajes_master;
SELECT COUNT(*) - COUNT(DISTINCT id_personaje) AS duplicados FROM personajes_master;

-- Tipos de datos y PK
DESCRIBE personajes_master;

-- Nulos: texto rellenado con N/A y numericos/fechas en NULL
SELECT COUNT(*) AS tipo_na FROM personajes_master WHERE tipo = 'N/A';
SELECT COUNT(*) AS episodios_nulos FROM personajes_master WHERE total_episodios IS NULL;
SELECT COUNT(*) AS fechas_nulas FROM personajes_master WHERE fecha_creacion IS NULL;

-- Verificar un registro (comparar con Mongo Compass y /analitica/perfil/{id})
SELECT * FROM personajes_master WHERE id_personaje = 1;
