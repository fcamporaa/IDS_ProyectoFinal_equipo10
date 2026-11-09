from src.db import ejecutar_consulta, ejecutar_mutacion

# Consulta base para obtener salas con su capacidad total calculada a partir de butacas activas
SELECT_SALA_CON_CAPACIDAD = """
    SELECT s.id_sala, s.id_local, s.numero, s.activa,
           COUNT(b.id_butaca) AS capacidad
    FROM salas s
    LEFT JOIN butacas b ON s.id_sala = b.id_sala AND b.activa = 1
"""


def obtener_locales_db() -> list[dict]:
    """Obtiene los locales activos de la tabla locales."""
    query = """
        SELECT id_local, nombre, direccion, activo
        FROM locales
        WHERE activo = 1
        ORDER BY id_local ASC
    """
    return ejecutar_consulta(query)


def buscar_local_por_id_db(id_local: int) -> dict | None:
    """Busca un local por su ID."""
    query = """
        SELECT id_local, nombre, direccion, activo
        FROM locales
        WHERE id_local = %s
    """
    filas = ejecutar_consulta(query, (id_local,))
    return filas[0] if filas else None


def obtener_salas_por_local_db(id_local: int) -> list[dict]:
    """Obtiene las salas pertenecientes a un local y cuenta sus butacas activas."""
    query = (
        SELECT_SALA_CON_CAPACIDAD
        + """
        WHERE s.id_local = %s
        GROUP BY s.id_sala, s.id_local, s.numero, s.activa
        ORDER BY s.numero ASC
        """
    )
    return ejecutar_consulta(query, (id_local,))


def buscar_sala_por_id_db(id_sala: int) -> dict | None:
    """Busca una sala por su id_sala."""
    query = (
        SELECT_SALA_CON_CAPACIDAD
        + """
        WHERE s.id_sala = %s
        GROUP BY s.id_sala, s.id_local, s.numero, s.activa
        """
    )
    filas = ejecutar_consulta(query, (id_sala,))
    return filas[0] if filas else None


def obtener_butacas_por_sala_db(id_sala: int) -> list[dict]:
    """Obtiene las butacas de una sala ordenadas por fila y numero."""
    query = """
        SELECT id_butaca, id_sala, fila, numero, activa
        FROM butacas
        WHERE id_sala = %s
        ORDER BY fila ASC, numero ASC
    """
    return ejecutar_consulta(query, (id_sala,))


def actualizar_sala_db(id_sala: int, datos: dict) -> int:
    """Actualiza una sala en la tabla salas."""
    campos = []
    valores = []

    if "numero" in datos:
        campos.append("numero = %s")
        valores.append(datos["numero"])

    if "activa" in datos:
        campos.append("activa = %s")
        valores.append(1 if datos["activa"] else 0)

    if not campos:
        return 0

    valores.append(id_sala)
    query = f"UPDATE salas SET {', '.join(campos)} WHERE id_sala = %s"
    return ejecutar_mutacion(query, tuple(valores))
