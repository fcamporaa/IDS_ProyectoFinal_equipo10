from src.constants import (
    ESTADO_COMPRA_CANCELADA,
    ESTADO_COMPRA_VENDIDA,
    ESTADO_FUNCION_CANCELADA,
    ESTADOS_COMPRA_DASHBOARD,
    ESTADOS_ENTRADA_OCUPACION,
    ESTADOS_ENTRADA_VENDIDA,
)
from src.db import ejecutar_consulta


def _marcadores(valores: tuple) -> str:
    """Genera los placeholders parametrizados para una cláusula IN."""
    return ", ".join(["%s"] * len(valores))


def _agregar_filtro_fechas(
    condiciones: list[str], parametros: list, filtros: dict, columna: str
) -> None:
    """Agrega el rango inclusivo de fechas sobre una columna DATETIME."""
    if filtros.get("desde"):
        condiciones.append(f"{columna} >= %s")
        parametros.append(filtros["desde"])
    if filtros.get("hasta"):
        condiciones.append(f"{columna} < DATE_ADD(%s, INTERVAL 1 DAY)")
        parametros.append(filtros["hasta"])


def obtener_porcentaje_ocupacion_db(filtros: dict = None) -> list[dict]:
    """Consulta de ocupación por función cruzando entradas vendidas vs capacidad de sala."""
    filtros = filtros or {}
    condiciones = ["f.estado <> %s"]
    # El filtro de entradas vive en el LEFT JOIN, por eso sus placeholders van primero.
    parametros = list(ESTADOS_ENTRADA_OCUPACION) + [ESTADO_FUNCION_CANCELADA]

    _agregar_filtro_fechas(condiciones, parametros, filtros, "f.inicio")
    if filtros.get("id_local"):
        condiciones.append("s.id_local = %s")
        parametros.append(filtros["id_local"])

    query = f"""
        SELECT f.id_funcion, p.titulo AS pelicula, s.numero AS sala,
               l.nombre AS local,
               (SELECT COUNT(*)
                FROM butacas b
                WHERE b.id_sala = f.id_sala AND b.activa = 1) AS capacidad_total,
               COUNT(DISTINCT e.id_entrada) AS entradas_vendidas
        FROM funciones f
        JOIN peliculas p ON p.id_pelicula = f.id_pelicula
        JOIN salas s ON s.id_sala = f.id_sala
        JOIN locales l ON l.id_local = s.id_local
        LEFT JOIN entradas e
               ON e.id_funcion = f.id_funcion
              AND e.estado IN ({_marcadores(ESTADOS_ENTRADA_OCUPACION)})
        WHERE {" AND ".join(condiciones)}
        GROUP BY f.id_funcion, f.id_sala, p.titulo, s.numero, l.nombre
        ORDER BY f.inicio DESC, p.titulo ASC
    """
    return ejecutar_consulta(query, tuple(parametros))


def obtener_ventas_por_genero_db(filtros: dict = None) -> list[dict]:
    """Consulta de ventas agrupada por género cinematográfico."""
    filtros = filtros or {}
    condiciones = [
        "e.estado IN (%s)",
        "c.estado = %s",
        "f.estado <> %s",
    ]
    parametros = list(ESTADOS_ENTRADA_VENDIDA) + [
        ESTADO_COMPRA_VENDIDA,
        ESTADO_FUNCION_CANCELADA,
    ]

    _agregar_filtro_fechas(condiciones, parametros, filtros, "f.inicio")
    if filtros.get("id_local"):
        condiciones.append("s.id_local = %s")
        parametros.append(filtros["id_local"])

    query = f"""
        SELECT g.nombre AS genero,
               COUNT(DISTINCT e.id_entrada) AS entradas_vendidas,
               COALESCE(SUM(e.precio_unitario), 0) AS total_recaudado
        FROM entradas e
        JOIN compras c ON c.id_compra = e.id_compra
        JOIN funciones f ON f.id_funcion = e.id_funcion
        JOIN peliculas p ON p.id_pelicula = f.id_pelicula
        JOIN pelicula_generos pg ON pg.id_pelicula = p.id_pelicula
        JOIN generos g ON g.id_genero = pg.id_genero
        JOIN salas s ON s.id_sala = f.id_sala
        WHERE {" AND ".join(condiciones)}
        GROUP BY g.id_genero, g.nombre
        ORDER BY total_recaudado DESC, entradas_vendidas DESC
    """
    return ejecutar_consulta(query, tuple(parametros))


def obtener_ventas_por_franja_horaria_db(filtros: dict = None) -> list[dict]:
    """Consulta de ventas agrupada por hora de inicio de función."""
    filtros = filtros or {}
    condiciones = [
        "e.estado IN (%s)",
        "c.estado = %s",
        "f.estado <> %s",
    ]
    parametros = list(ESTADOS_ENTRADA_VENDIDA) + [
        ESTADO_COMPRA_VENDIDA,
        ESTADO_FUNCION_CANCELADA,
    ]

    _agregar_filtro_fechas(condiciones, parametros, filtros, "f.inicio")
    if filtros.get("id_local"):
        condiciones.append("s.id_local = %s")
        parametros.append(filtros["id_local"])

    query = f"""
        SELECT HOUR(f.inicio) AS hora,
               COUNT(DISTINCT e.id_entrada) AS entradas_vendidas,
               COALESCE(SUM(e.precio_unitario), 0) AS total_recaudado
        FROM entradas e
        JOIN compras c ON c.id_compra = e.id_compra
        JOIN funciones f ON f.id_funcion = e.id_funcion
        JOIN salas s ON s.id_sala = f.id_sala
        WHERE {" AND ".join(condiciones)}
        GROUP BY HOUR(f.inicio)
        ORDER BY HOUR(f.inicio) ASC
    """
    return ejecutar_consulta(query, tuple(parametros))


def obtener_metricas_cancelaciones_db(filtros: dict = None) -> dict:
    """Consulta de total de compras vs compras canceladas."""
    filtros = filtros or {}
    condiciones = ["c.estado IN (%s, %s)"]
    parametros = list(ESTADOS_COMPRA_DASHBOARD)

    _agregar_filtro_fechas(condiciones, parametros, filtros, "c.creada_en")
    if filtros.get("id_local"):
        condiciones.append("s.id_local = %s")
        parametros.append(filtros["id_local"])

    query = f"""
        SELECT COUNT(*) AS total_compras,
               COALESCE(SUM(CASE WHEN c.estado = %s THEN 1 ELSE 0 END), 0)
                   AS total_canceladas,
               COALESCE(SUM(CASE WHEN c.estado = %s THEN c.total ELSE 0 END), 0)
                   AS monto_devuelto
        FROM compras c
        JOIN funciones f ON f.id_funcion = c.id_funcion
        JOIN salas s ON s.id_sala = f.id_sala
        WHERE {" AND ".join(condiciones)}
    """
    parametros_consulta = [
        ESTADO_COMPRA_CANCELADA,
        ESTADO_COMPRA_CANCELADA,
    ] + parametros
    resultados = ejecutar_consulta(query, tuple(parametros_consulta))
    return resultados[0] if resultados else {}


def obtener_consolidado_ventas_db(filtros: dict = None) -> list[dict]:
    """Consulta de ranking de películas con más recaudación y espectadores."""
    pass
