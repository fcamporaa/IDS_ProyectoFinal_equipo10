from datetime import datetime, timedelta
from src.db import obtener_conexion, ejecutar_consulta


def validar_y_registrar_qr_db(qr_token: str, id_administrador: int,
                             id_sala: int | None) -> dict:
    """Bloquea la compra, decide acceso y registra auditoría en una sola transacción."""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT c.id_compra, c.estado, c.qr_validado_en, c.cancelada_en,
                       f.inicio, f.fin, f.estado AS estado_funcion, f.id_sala,
                       p.titulo AS pelicula
                FROM compras c
                JOIN funciones f ON f.id_funcion = c.id_funcion
                JOIN peliculas p ON p.id_pelicula = f.id_pelicula
                WHERE c.qr_token = %s
                FOR UPDATE
            """, (qr_token,))
            compra = cursor.fetchone()
            if compra is None:
                # La migración 002 permite auditar tokens desconocidos con id_compra NULL.
                cursor.execute("""
                    INSERT INTO validaciones_qr
                        (id_compra, id_administrador, fecha_validacion, resultado)
                    VALUES (NULL, %s, %s, 'FALLIDO')
                """, (id_administrador, datetime.now()))
                conexion.commit()
                return {"autorizado": False, "resultado": "FALLIDO",
                        "mensaje": "QR inválido o inexistente.", "id_compra": None}

            ahora = datetime.now()
            estado = "EXITO"
            mensaje = "Ingreso autorizado. Compra validada con éxito."
            if compra["qr_validado_en"] is not None:
                estado, mensaje = "REUTILIZADO", "El QR ya fue utilizado."
            elif compra["estado"] != "PAGADA" or compra["cancelada_en"] is not None:
                estado, mensaje = "FALLIDO", "La compra no está pagada o fue cancelada."
            elif compra["estado_funcion"] not in ("PROGRAMADA", "EN_CURSO"):
                estado, mensaje = "FALLIDO", "La función no está habilitada para ingreso."
            elif id_sala is not None and compra["id_sala"] != id_sala:
                estado, mensaje = "FALLIDO", "El QR no corresponde a esta sala."
            elif not (compra["inicio"] - timedelta(minutes=30) <= ahora <= compra["fin"]):
                estado, mensaje = "FALLIDO", "El QR no corresponde al horario de esta función."
            else:
                cursor.execute("""
                    SELECT COUNT(*) AS cantidad FROM entradas
                    WHERE id_compra = %s AND estado = 'OCUPADA'
                """, (compra["id_compra"],))
                if cursor.fetchone()["cantidad"] <= 0:
                    estado, mensaje = "FALLIDO", "La compra no tiene entradas vigentes."

            if estado == "EXITO":
                cursor.execute("""
                    UPDATE compras SET qr_validado_en = %s
                    WHERE id_compra = %s AND qr_validado_en IS NULL
                      AND estado = 'PAGADA' AND cancelada_en IS NULL
                """, (ahora, compra["id_compra"]))
                if cursor.rowcount != 1:
                    estado, mensaje = "REUTILIZADO", "El QR ya fue utilizado."

            cursor.execute("""
                INSERT INTO validaciones_qr
                    (id_compra, id_administrador, fecha_validacion, resultado)
                VALUES (%s, %s, %s, %s)
            """, (compra["id_compra"], id_administrador, ahora, estado))
            conexion.commit()
            return {"autorizado": estado == "EXITO", "resultado": estado,
                    "mensaje": mensaje, "id_compra": compra["id_compra"],
                    "pelicula": compra["pelicula"] if estado == "EXITO" else None,
                    "fecha_validacion": ahora.isoformat(timespec="seconds")}
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def obtener_historial_validaciones_db(filtros: dict) -> list[dict]:
    """Consulta limitada para impedir respuestas ilimitadas en el backoffice."""
    condiciones = []
    parametros = []
    if "id_compra" in filtros:
        condiciones.append("v.id_compra = %s")
        parametros.append(filtros["id_compra"])
    if "resultado" in filtros:
        condiciones.append("v.resultado = %s")
        parametros.append(filtros["resultado"])
    where = "WHERE " + " AND ".join(condiciones) if condiciones else ""
    query = f"""
        SELECT v.id_validacion, v.id_compra, v.id_administrador,
               u.nombre AS nombre_administrador,
               v.fecha_validacion, v.resultado
        FROM validaciones_qr v
        JOIN usuarios u ON u.id_usuario = v.id_administrador
        {where}
        ORDER BY v.fecha_validacion DESC, v.id_validacion DESC
        LIMIT 200
    """
    return ejecutar_consulta(query, tuple(parametros))
