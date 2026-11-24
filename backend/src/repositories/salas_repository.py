from src.db import ejecutar_consulta, ejecutar_mutacion, ejecutar_transaccion

# Consulta base para obtener salas con su capacidad total calculada a partir de butacas activas
SELECT_SALA_CON_CAPACIDAD = """
    SELECT s.id_sala, s.id_local, s.numero, s.activa,
           COUNT(b.id_butaca) AS capacidad
    FROM salas s
    LEFT JOIN butacas b ON s.id_sala = b.id_sala AND b.activa = 1
"""

SQL_INSERTAR_SALA = """
    INSERT INTO salas (id_local, numero, activa)
    VALUES (%s, %s, %s)
"""

SQL_INSERTAR_BUTACA = """
    INSERT INTO butacas (id_sala, fila, numero, activa)
    VALUES (%s, %s, %s, 1)
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


def obtener_salas_admin_db() -> list[dict]:
    """Lista todas las salas (activas e inactivas) con el nombre del complejo."""
    query = """
        SELECT s.id_sala, s.id_local, l.nombre AS nombre_local, s.numero, s.activa,
               COUNT(b.id_butaca) AS capacidad
        FROM salas s
        INNER JOIN locales l ON l.id_local = s.id_local
        LEFT JOIN butacas b ON s.id_sala = b.id_sala AND b.activa = 1
        GROUP BY s.id_sala, s.id_local, l.nombre, s.numero, s.activa
        ORDER BY l.nombre ASC, s.numero ASC
    """
    return ejecutar_consulta(query)


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


def buscar_sala_por_local_y_numero_db(id_local: int, numero: int) -> dict | None:
    """Busca si ya existe una sala con ese número dentro del complejo."""
    query = """
        SELECT id_sala, id_local, numero, activa
        FROM salas
        WHERE id_local = %s AND numero = %s
    """
    filas = ejecutar_consulta(query, (id_local, numero))
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


def contar_butacas_sala_db(id_sala: int) -> int:
    """Cuenta todas las butacas (activas e inactivas) de una sala."""
    query = "SELECT COUNT(*) AS total FROM butacas WHERE id_sala = %s"
    filas = ejecutar_consulta(query, (id_sala,))
    return int(filas[0]["total"]) if filas else 0


def existe_butaca_en_sala_db(id_sala: int, fila: str, numero: int) -> bool:
    """Indica si ya hay una butaca con esa fila y número en la sala."""
    query = """
        SELECT id_butaca
        FROM butacas
        WHERE id_sala = %s AND fila = %s AND numero = %s
        LIMIT 1
    """
    filas = ejecutar_consulta(query, (id_sala, fila, numero))
    return bool(filas)


def insertar_sala_con_butacas_db(
    id_local: int, numero: int, activa: bool, butacas: list[tuple[str, int]]
) -> int:
    """
    Crea la sala y su grilla de butacas en una sola transacción.
    `butacas` es una lista de (fila, numero). Devuelve el id_sala generado.
    """

    def operacion(cursor):
        cursor.execute(
            SQL_INSERTAR_SALA, (id_local, numero, 1 if activa else 0)
        )
        id_sala = cursor.lastrowid
        if butacas:
            cursor.executemany(
                SQL_INSERTAR_BUTACA,
                [(id_sala, fila, asiento) for fila, asiento in butacas],
            )
        return id_sala

    return ejecutar_transaccion(operacion)


def insertar_butacas_lote_db(id_sala: int, butacas: list[tuple[str, int]]) -> int:
    """Inserta un lote de butacas activas para una sala en una transacción."""

    def operacion(cursor):
        cursor.executemany(
            SQL_INSERTAR_BUTACA,
            [(id_sala, fila, asiento) for fila, asiento in butacas],
        )
        return cursor.rowcount

    return ejecutar_transaccion(operacion)


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
