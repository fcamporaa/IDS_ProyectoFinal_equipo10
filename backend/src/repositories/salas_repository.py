from src.db import ejecutar_consulta, ejecutar_mutacion


def obtener_locales_db() -> list[dict]:
    """Obtiene los locales activos de la tabla locales."""
    sql = "SELECT id_local, nombre, direccion, activo FROM locales WHERE activo = 1 ORDER BY id_local ASC"
    return ejecutar_consulta(sql)


def buscar_local_por_id_db(id_local: int) -> dict | None:
    """Busca un local por su ID."""
    sql = "SELECT id_local, nombre, direccion, activo FROM locales WHERE id_local = %(id_local)s"
    filas = ejecutar_consulta(sql, {"id_local": id_local})
    return filas[0] if filas else None


def obtener_salas_por_local_db(id_local: int) -> list[dict]:
    """Obtiene las salas pertenecientes a un local y cuenta sus butacas activas."""
    sql = (
        "SELECT s.id_sala, s.id_local, s.numero, s.activa, COUNT(b.id_butaca) AS capacidad "
        "FROM salas s "
        "LEFT JOIN butacas b ON s.id_sala = b.id_sala AND b.activa = 1 "
        "WHERE s.id_local = %(id_local)s "
        "GROUP BY s.id_sala, s.id_local, s.numero, s.activa "
        "ORDER BY s.numero ASC"
    )
    return ejecutar_consulta(sql, {"id_local": id_local})


def buscar_sala_por_id_db(id_sala: int) -> dict | None:
    """Busca una sala por su id_sala."""
    sql = (
        "SELECT s.id_sala, s.id_local, s.numero, s.activa, COUNT(b.id_butaca) AS capacidad "
        "FROM salas s "
        "LEFT JOIN butacas b ON s.id_sala = b.id_sala AND b.activa = 1 "
        "WHERE s.id_sala = %(id_sala)s "
        "GROUP BY s.id_sala, s.id_local, s.numero, s.activa"
    )
    filas = ejecutar_consulta(sql, {"id_sala": id_sala})
    return filas[0] if filas else None


def obtener_butacas_por_sala_db(id_sala: int) -> list[dict]:
    """Obtiene las butacas de una sala ordenadas por fila y numero."""
    sql = "SELECT id_butaca, id_sala, fila, numero, activa FROM butacas WHERE id_sala = %(id_sala)s ORDER BY fila ASC, numero ASC"
    return ejecutar_consulta(sql, {"id_sala": id_sala})


def actualizar_sala_db(id_sala: int, datos: dict) -> int:
    """Actualiza una sala en la tabla salas."""
    campos = []
    params = {"id_sala": id_sala}

    if "numero" in datos:
        campos.append("numero = %(numero)s")
        params["numero"] = datos["numero"]

    if "activa" in datos:
        campos.append("activa = %(activa)s")
        params["activa"] = 1 if datos["activa"] else 0

    if not campos:
        return 0

    sql = f"UPDATE salas SET {', '.join(campos)} WHERE id_sala = %(id_sala)s"
    return ejecutar_mutacion(sql, params)
