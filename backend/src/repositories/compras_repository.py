from datetime import datetime, timedelta

from src.db import ejecutar_consulta, ejecutar_mutacion, obtener_conexion


def verificar_butacas_disponibles_db(id_funcion: int, ids_butacas: list[int]) -> bool:
    """Verifica que ninguna de las butacas solicitadas esté ocupada/reservada en la función."""
    pass


def insertar_compra_db(datos: dict) -> int:
    """Inserta registro en la tabla compras y retorna id_compra."""
    pass


def insertar_entradas_db(entradas: list[dict]) -> None:
    """Inserta las entradas individuales para cada butaca de la compra."""
    pass


def insertar_servicios_compra_db(servicios: list[dict]) -> None:
    """Inserta los ítems en la tabla compra_servicios."""
    pass


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
               c.total, c.qr_token, c.qr_validado_en,
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


def actualizar_estado_compra_db(id_compra: int, estado: str, cancelada_en: str = None) -> int:
    """Actualiza el estado de la compra."""
    query = """
        UPDATE compras
        SET estado = %(estado)s, cancelada_en = %(cancelada_en)s
        WHERE id_compra = %(id_compra)s
    """
    return ejecutar_mutacion(
        query,
        {"id_compra": id_compra, "estado": estado, "cancelada_en": cancelada_en},
    )


def liberar_butacas_compra_db(id_compra: int) -> int:
    """Actualiza el estado de las entradas a CANCELADA para liberar butacas."""
    query = """
        UPDATE entradas
        SET estado = 'CANCELADA'
        WHERE id_compra = %(id_compra)s AND estado IN ('RESERVADA', 'OCUPADA')
    """
    return ejecutar_mutacion(query, {"id_compra": id_compra})


def cancelar_compra_atomica_db(id_compra: int, id_usuario: int, cancelada_en: str) -> bool:
    """Cancela compra y entradas en una transacción con bloqueo y revalidación."""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.estado, c.qr_validado_en, f.inicio
                FROM compras c
                JOIN funciones f ON f.id_funcion = c.id_funcion
                WHERE c.id_compra = %(id_compra)s AND c.id_usuario = %(id_usuario)s
                FOR UPDATE
                """,
                {"id_compra": id_compra, "id_usuario": id_usuario},
            )
            compra = cursor.fetchone()
            if (
                not compra
                or compra["estado"] != "PAGADA"
                or compra["qr_validado_en"] is not None
                or compra["inicio"] <= datetime.now() + timedelta(hours=24)
            ):
                conexion.rollback()
                return False

            cursor.execute(
                "UPDATE compras SET estado = 'CANCELADA', cancelada_en = %(fecha)s WHERE id_compra = %(id_compra)s",
                {"fecha": cancelada_en, "id_compra": id_compra},
            )
            cursor.execute(
                "UPDATE entradas SET estado = 'CANCELADA' WHERE id_compra = %(id_compra)s AND estado IN ('RESERVADA', 'OCUPADA')",
                {"id_compra": id_compra},
            )
        conexion.commit()
        return True
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
