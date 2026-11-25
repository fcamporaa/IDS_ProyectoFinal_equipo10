from pymysql.err import IntegrityError

from src.db import ejecutar_consulta, ejecutar_mutacion, ejecutar_transaccion


def ejecutar_transaccion_compras_db(operacion):
    return ejecutar_transaccion(operacion)


def ejecutar_registro_compra_db(operacion) -> dict | None:
    try:
        return ejecutar_transaccion_compras_db(operacion)
    except IntegrityError:
        return None


def obtener_compras_por_usuario_db(id_usuario: int) -> list[dict]:
    """Obtiene las compras de un usuario ordenadas por creada_en DESC."""
    query = """
        SELECT c.id_compra, c.codigo_reserva, p.titulo AS pelicula,
               f.inicio AS fecha_funcion,
               (SELECT COUNT(*) FROM entradas e WHERE e.id_compra = c.id_compra) AS cantidad_entradas,
               c.total, c.estado, c.creada_en
        FROM compras c
        JOIN funciones f ON f.id_funcion = c.id_funcion
        JOIN peliculas p ON p.id_pelicula = f.id_pelicula
        WHERE c.id_usuario = %(id_usuario)s
        ORDER BY c.creada_en DESC
    """
    return ejecutar_consulta(query, {"id_usuario": id_usuario})


def obtener_detalle_compra_db(id_compra: int) -> dict | None:
    """Obtiene la cabecera de la compra por id_compra."""
    query = """
        SELECT c.id_compra, c.id_usuario, c.codigo_reserva, c.estado, c.creada_en,
               c.subtotal_entradas, c.subtotal_servicios, c.cargo_servicio,
               c.total, c.qr_token, c.qr_validado_en, c.email_comprobante,
               f.id_funcion, f.id_pelicula, f.id_sala, f.inicio, f.fin,
               f.formato, f.idioma, f.subtitulada, f.precio_entrada,
               f.estado AS estado_funcion, p.titulo AS titulo_pelicula,
               s.numero AS numero_sala, l.nombre AS nombre_local
        FROM compras c
        JOIN funciones f ON f.id_funcion = c.id_funcion
        JOIN peliculas p ON p.id_pelicula = f.id_pelicula
        JOIN salas s ON s.id_sala = f.id_sala
        JOIN locales l ON l.id_local = s.id_local
        WHERE c.id_compra = %(id_compra)s
    """
    resultados = ejecutar_consulta(query, {"id_compra": id_compra})
    return resultados[0] if resultados else None


def obtener_entradas_por_compra_db(id_compra: int) -> list[dict]:
    """Obtiene las entradas y butacas asociadas a una compra."""
    query = """
        SELECT e.id_entrada, b.fila, b.numero, e.precio_unitario
        FROM entradas e
        JOIN butacas b ON b.id_butaca = e.id_butaca
        WHERE e.id_compra = %(id_compra)s
        ORDER BY b.fila, b.numero
    """
    return ejecutar_consulta(query, {"id_compra": id_compra})


def obtener_servicios_por_compra_db(id_compra: int) -> list[dict]:
    """Obtiene los servicios adquiridos en una compra."""
    query = """
        SELECT s.nombre AS nombre_servicio, cs.cantidad, cs.precio_unitario,
               cs.cantidad * cs.precio_unitario AS subtotal
        FROM compra_servicios cs
        JOIN servicios s ON s.id_servicio = cs.id_servicio
        WHERE cs.id_compra = %(id_compra)s
        ORDER BY s.nombre
    """
    return ejecutar_consulta(query, {"id_compra": id_compra})


def bloquear_funcion_para_reserva_db(cursor, id_funcion: int) -> dict | None:
    cursor.execute(
        """SELECT id_sala, estado, inicio FROM funciones
           WHERE id_funcion = %s FOR UPDATE""",
        (id_funcion,),
    )
    return cursor.fetchone()


def obtener_butacas_solicitadas_db(cursor, id_sala: int, ids_butacas: list[int]) -> list[dict]:
    if not ids_butacas:
        return []
    marcadores = ",".join(["%s"] * len(ids_butacas))
    cursor.execute(
        f"""SELECT id_butaca, fila, activa FROM butacas
            WHERE id_sala = %s
              AND id_butaca IN ({marcadores}) FOR UPDATE""",
        (id_sala, *ids_butacas),
    )
    return cursor.fetchall()


def obtener_reservas_por_token_db(cursor, token_reserva: str) -> list[dict]:
    cursor.execute(
        """SELECT id_usuario, expira_en FROM reservas_temporales_butacas
           WHERE token_reserva = %s FOR UPDATE""",
        (token_reserva,),
    )
    return cursor.fetchall()


def hay_entrada_ocupada_db(
    cursor, id_funcion: int, ids_butacas: list[int], estados_ocupacion: tuple[str, ...]
) -> bool:
    if not ids_butacas or not estados_ocupacion:
        return False
    marcadores = ",".join(["%s"] * len(ids_butacas))
    marcadores_estados = ",".join(["%s"] * len(estados_ocupacion))
    cursor.execute(
        f"""SELECT id_entrada FROM entradas
            WHERE id_funcion = %s AND id_butaca IN ({marcadores})
              AND estado IN ({marcadores_estados}) LIMIT 1""",
        (id_funcion, *ids_butacas, *estados_ocupacion),
    )
    return cursor.fetchone() is not None


def obtener_butacas_reservadas_por_usuario_db(
    cursor, id_funcion: int, id_usuario: int, token_reserva: str,
    ahora, ids_butacas: list[int],
) -> list[dict]:
    if not ids_butacas:
        return []
    marcadores = ",".join(["%s"] * len(ids_butacas))
    cursor.execute(
        f"""SELECT id_butaca FROM reservas_temporales_butacas
            WHERE id_funcion = %s AND id_usuario = %s AND token_reserva = %s
              AND expira_en > %s AND id_butaca IN ({marcadores}) FOR UPDATE""",
        (id_funcion, id_usuario, token_reserva, ahora, *ids_butacas),
    )
    return cursor.fetchall()


def hay_reserva_temporal_ajena_db(
    cursor, id_funcion: int, ids_butacas: list[int], ahora, token_reserva: str,
) -> bool:
    if not ids_butacas:
        return False
    marcadores = ",".join(["%s"] * len(ids_butacas))
    cursor.execute(
        f"""SELECT id_butaca FROM reservas_temporales_butacas
            WHERE id_funcion = %s AND id_butaca IN ({marcadores})
              AND expira_en > %s AND token_reserva <> %s LIMIT 1""",
        (id_funcion, *ids_butacas, ahora, token_reserva),
    )
    return cursor.fetchone() is not None


def eliminar_reservas_temporales_usuario_db(cursor, id_usuario: int, token_reserva: str) -> None:
    cursor.execute(
        """DELETE FROM reservas_temporales_butacas
           WHERE id_usuario = %s AND token_reserva = %s""",
        (id_usuario, token_reserva),
    )


def eliminar_reservas_temporales_vencidas_db(
    cursor, id_funcion: int, ids_butacas: list[int], ahora,
) -> None:
    if not ids_butacas:
        return
    marcadores = ",".join(["%s"] * len(ids_butacas))
    cursor.execute(
        f"""DELETE FROM reservas_temporales_butacas
            WHERE id_funcion = %s AND id_butaca IN ({marcadores})
              AND expira_en <= %s""",
        (id_funcion, *ids_butacas, ahora),
    )


def insertar_reservas_temporales_db(cursor, reservas: list[tuple]) -> None:
    cursor.executemany(
        """INSERT INTO reservas_temporales_butacas
           (id_funcion, id_butaca, id_usuario, token_reserva, expira_en)
           VALUES (%s, %s, %s, %s, %s)""",
        reservas,
    )


def liberar_reserva_temporal_db(id_usuario: int, token_reserva: str) -> None:
    ejecutar_mutacion(
        "DELETE FROM reservas_temporales_butacas WHERE id_usuario = %s AND token_reserva = %s",
        (id_usuario, token_reserva),
    )


def obtener_compra_para_cancelar_db(cursor, id_compra: int, id_usuario: int) -> dict | None:
    cursor.execute(
        """SELECT c.estado, c.qr_validado_en, f.inicio
           FROM compras c
           JOIN funciones f ON f.id_funcion = c.id_funcion
           WHERE c.id_compra = %s AND c.id_usuario = %s
           FOR UPDATE""",
        (id_compra, id_usuario),
    )
    return cursor.fetchone()


def marcar_compra_cancelada_db(
    cursor, id_compra: int, estado: str, cancelada_en: str
) -> None:
    cursor.execute(
        """UPDATE compras SET estado = %s, cancelada_en = %s
           WHERE id_compra = %s""",
        (estado, cancelada_en, id_compra),
    )


def cancelar_entradas_de_compra_db(
    cursor, id_compra: int, estado: str, estados_actuales: tuple[str, ...]
) -> None:
    if not estados_actuales:
        return
    marcadores_estados = ",".join(["%s"] * len(estados_actuales))
    cursor.execute(
        f"""UPDATE entradas SET estado = %s
            WHERE id_compra = %s AND estado IN ({marcadores_estados})""",
        (estado, id_compra, *estados_actuales),
    )

def obtener_funcion_para_compra_db(cursor, id_funcion: int) -> dict | None:
    cursor.execute(
          """SELECT id_funcion, id_sala, precio_entrada, estado, inicio
           FROM funciones
              WHERE id_funcion = %s FOR UPDATE""",
          (id_funcion,),
    )
    return cursor.fetchone()


def obtener_servicios_por_ids_db(cursor, ids_servicios: list[int]) -> list[dict]:
    if not ids_servicios:
        return []
    marcadores = ",".join(["%s"] * len(ids_servicios))
    cursor.execute(
        f"""SELECT id_servicio, precio, activo FROM servicios
            WHERE id_servicio IN ({marcadores})""",
        tuple(ids_servicios),
    )
    return cursor.fetchall()


def insertar_compra_db(cursor, datos: dict) -> int:
    cursor.execute(
        """INSERT INTO compras
           (id_usuario, id_funcion, codigo_reserva, email_comprobante,
            estado, medio_pago, subtotal_entradas, subtotal_servicios,
            cargo_servicio, total, qr_token)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            datos["id_usuario"], datos["id_funcion"], datos["codigo_reserva"],
            datos["email_comprobante"], datos["estado"], datos["medio_pago"],
            datos["subtotal_entradas"], datos["subtotal_servicios"],
            datos["cargo_servicio"], datos["total"], datos["qr_token"],
        ),
    )
    return cursor.lastrowid


def insertar_entradas_db(cursor, entradas: list[dict]) -> None:
    cursor.executemany(
        """INSERT INTO entradas
           (id_compra, id_funcion, id_butaca, precio_unitario, estado)
           VALUES (%s, %s, %s, %s, %s)""",
        [
            (
                entrada["id_compra"], entrada["id_funcion"],
                entrada["id_butaca"], entrada["precio_unitario"], entrada["estado"],
            )
            for entrada in entradas
        ],
    )


def eliminar_reserva_temporal_compra_db(cursor, id_usuario: int, token_reserva: str) -> None:
    cursor.execute(
        "DELETE FROM reservas_temporales_butacas WHERE id_usuario = %s AND token_reserva = %s",
        (id_usuario, token_reserva),
    )


def insertar_servicios_compra_db(cursor, servicios: list[dict]) -> None:
    if not servicios:
        return
    cursor.executemany(
        """INSERT INTO compra_servicios
           (id_compra, id_servicio, cantidad, precio_unitario)
           VALUES (%s, %s, %s, %s)""",
        [
            (
                servicio["id_compra"], servicio["id_servicio"],
                servicio["cantidad"], servicio["precio_unitario"],
            )
            for servicio in servicios
        ],
    )

def obtener_detalle_comprobante_db(id_compra: int, id_usuario: int | None = None) -> dict | None:
    parametros = (id_compra,) if id_usuario is None else (id_compra, id_usuario)
    condicion = "" if id_usuario is None else " AND c.id_usuario = %s"
    filas = ejecutar_consulta(
        """SELECT c.id_compra, c.codigo_reserva, c.estado, c.creada_en,
                  c.email_comprobante, c.medio_pago, c.total, c.subtotal_entradas,
                  c.subtotal_servicios, c.cargo_servicio, c.qr_token, c.qr_validado_en,
                  p.titulo AS pelicula, f.inicio, s.numero AS sala,
                  l.nombre AS local, l.direccion
           FROM compras c
           JOIN funciones f ON f.id_funcion = c.id_funcion
           JOIN peliculas p ON p.id_pelicula = f.id_pelicula
           JOIN salas s ON s.id_sala = f.id_sala
           JOIN locales l ON l.id_local = s.id_local
           WHERE c.id_compra = %s""" + condicion,
        parametros,
    )
    if not filas:
        return None
    return filas[0]
