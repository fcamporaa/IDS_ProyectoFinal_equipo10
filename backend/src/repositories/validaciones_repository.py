from src.db import obtener_conexion, ejecutar_consulta
from src.utils import ahora_local


def validar_y_registrar_qr_db(qr_token: str, id_administrador: int,
                             id_sala: int | None, evaluar_ingreso) -> dict:
    """Bloquea la compra y registra la decisión y la auditoría en una transacción."""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.id_compra, c.estado, c.qr_validado_en, c.cancelada_en,
                       f.inicio, f.fin, f.estado AS estado_funcion, f.id_sala,
                       p.titulo AS pelicula
                FROM compras c
                JOIN funciones f ON f.id_funcion = c.id_funcion
                JOIN peliculas p ON p.id_pelicula = f.id_pelicula
                WHERE c.qr_token = %s
                FOR UPDATE
                """,
                (qr_token,),
            )
            compra = cursor.fetchone()
            if compra is None:
                # El esquema existente exige validaciones_qr.id_compra NOT NULL.
                conexion.rollback()
                return {
                    "autorizado": False, "resultado": "FALLIDO",
                    "mensaje": "El código QR no existe.", "id_compra": None,
                }

            ahora = ahora_local()
            cursor.execute(
                """
                SELECT COUNT(*) AS cantidad
                FROM entradas
                WHERE id_compra = %s AND estado = 'OCUPADA'
                """,
                (compra["id_compra"],),
            )
            entradas_vigentes = cursor.fetchone()["cantidad"]
            resultado, mensaje = evaluar_ingreso(
                compra, ahora, id_sala, entradas_vigentes,
            )
            if resultado == "EXITO":
                cursor.execute(
                    """
                    UPDATE compras SET qr_validado_en = %s
                    WHERE id_compra = %s AND qr_validado_en IS NULL
                      AND estado = 'PAGADA' AND cancelada_en IS NULL
                    """,
                    (ahora, compra["id_compra"]),
                )
                if cursor.rowcount != 1:
                    resultado, mensaje = "REUTILIZADO", "El código QR ya fue utilizado."

            cursor.execute(
                """
                INSERT INTO validaciones_qr
                    (id_compra, id_administrador, fecha_validacion, resultado)
                VALUES (%s, %s, %s, %s)
                """,
                (compra["id_compra"], id_administrador, ahora, resultado),
            )
        conexion.commit()
        return {
            "autorizado": resultado == "EXITO",
            "resultado": resultado,
            "mensaje": mensaje,
            "id_compra": compra["id_compra"],
            "pelicula": compra["pelicula"] if resultado == "EXITO" else None,
            "entradas_validadas": entradas_vigentes if resultado == "EXITO" else 0,
            "fecha_validacion": ahora.isoformat(timespec="seconds"),
        }
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def obtener_historial_validaciones_db(filtros: dict) -> list[dict]:
    """Devuelve el historial de puerta con filtros parametrizados y límite fijo."""
    condiciones = []
    parametros = []
    if "id_compra" in filtros:
        condiciones.append("v.id_compra = %s")
        parametros.append(filtros["id_compra"])
    if "resultado" in filtros:
        condiciones.append("v.resultado = %s")
        parametros.append(filtros["resultado"])
    where = "WHERE " + " AND ".join(condiciones) if condiciones else ""
    consulta = f"""
        SELECT v.id_validacion, v.id_compra, v.id_administrador,
               u.nombre AS nombre_administrador,
               v.fecha_validacion, v.resultado
        FROM validaciones_qr v
        JOIN usuarios u ON u.id_usuario = v.id_administrador
        {where}
        ORDER BY v.fecha_validacion DESC, v.id_validacion DESC
        LIMIT 200
    """
    return ejecutar_consulta(consulta, tuple(parametros))
