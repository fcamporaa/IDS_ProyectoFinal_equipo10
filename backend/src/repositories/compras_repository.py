from decimal import Decimal
from pymysql.err import IntegrityError
from src.db import obtener_conexion, ejecutar_consulta
from src.constants import HTTP_SOLICITUD_INVALIDA, HTTP_CONFLICTO, HTTP_NO_ENCONTRADO
from src.utils import error_de_negocio


def obtener_usuario_para_compra_db(id_usuario: int) -> dict | None:
    filas = ejecutar_consulta(
        "SELECT id_usuario, rol, activo FROM usuarios WHERE id_usuario = %s",
        (id_usuario,),
    )
    return filas[0] if filas else None


def registrar_compra_pagada_db(
    id_usuario: int, datos: dict, codigo_reserva: str, qr_token: str
) -> dict:
    """Una sola transacción y bloqueo por función: evita vender la misma butaca dos veces."""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """SELECT id_funcion, id_sala, precio_entrada
                   FROM funciones
                   WHERE id_funcion = %s AND estado = 'PROGRAMADA' AND inicio > NOW()
                   FOR UPDATE""",
                (datos["id_funcion"],),
            )
            funcion = cursor.fetchone()
            if not funcion:
                error_de_negocio("compras.funcion", "Función no disponible",
                                 "La función no existe o ya comenzó.", HTTP_NO_ENCONTRADO)

            butacas = datos["butacas_ids"]
            marcadores_butacas = ",".join(["%s"] * len(butacas))
            cursor.execute(
                f"""SELECT id_butaca FROM butacas
                    WHERE id_sala = %s AND activa = 1
                      AND id_butaca IN ({marcadores_butacas})
                    FOR UPDATE""",
                (funcion["id_sala"], *butacas),
            )
            if len(cursor.fetchall()) != len(butacas):
                error_de_negocio("compras.butacas", "Butacas inválidas",
                                 "Alguna butaca no pertenece a la sala o está inactiva.", HTTP_SOLICITUD_INVALIDA)
            cursor.execute(
                f"""SELECT id_entrada FROM entradas
                    WHERE id_funcion = %s AND id_butaca IN ({marcadores_butacas})
                      AND estado IN ('RESERVADA', 'OCUPADA')
                    LIMIT 1""",
                (datos["id_funcion"], *butacas),
            )
            if cursor.fetchone():
                error_de_negocio("compras.ocupacion", "Butacas ocupadas",
                                 "Una de las butacas acaba de ser reservada.", HTTP_CONFLICTO)

            servicios = datos["servicios"]
            precios_servicios = {}
            if servicios:
                ids = [item["id_servicio"] for item in servicios]
                marcadores = ",".join(["%s"] * len(ids))
                cursor.execute(
                    f"SELECT id_servicio, precio FROM servicios WHERE activo = 1 AND id_servicio IN ({marcadores})",
                    tuple(ids),
                )
                precios_servicios = {s["id_servicio"]: s["precio"] for s in cursor.fetchall()}
                if len(precios_servicios) != len(servicios):
                    error_de_negocio("compras.servicios", "Servicio no disponible",
                                     "Algún adicional no existe o está inactivo.", HTTP_SOLICITUD_INVALIDA)

            subtotal_entradas = funcion["precio_entrada"] * len(butacas)
            subtotal_servicios = sum((
                precios_servicios[s["id_servicio"]] * s["cantidad"] for s in servicios
            ), Decimal("0.00"))
            cargo_servicio = Decimal("0.00")
            total = subtotal_entradas + subtotal_servicios + cargo_servicio
            cursor.execute(
                """INSERT INTO compras
                (id_usuario, id_funcion, codigo_reserva, email_comprobante,
                 estado, medio_pago, subtotal_entradas, subtotal_servicios,
                 cargo_servicio, total, qr_token, email_estado)
                VALUES (%s, %s, %s, %s, 'PAGADA', %s, %s, %s, %s, %s, %s, 'PENDIENTE')""",
                (id_usuario, datos["id_funcion"], codigo_reserva,
                 datos["email_comprobante"], datos["medio_pago"], subtotal_entradas,
                 subtotal_servicios, cargo_servicio, total, qr_token),
            )
            id_compra = cursor.lastrowid
            cursor.executemany(
                """INSERT INTO entradas
                   (id_compra, id_funcion, id_butaca, precio_unitario, estado)
                   VALUES (%s, %s, %s, %s, 'OCUPADA')""",
                [(id_compra, datos["id_funcion"], id_butaca, funcion["precio_entrada"])
                 for id_butaca in butacas],
            )
            if servicios:
                cursor.executemany(
                    """INSERT INTO compra_servicios
                       (id_compra, id_servicio, cantidad, precio_unitario)
                       VALUES (%s, %s, %s, %s)""",
                    [(id_compra, s["id_servicio"], s["cantidad"],
                      precios_servicios[s["id_servicio"]]) for s in servicios],
                )
        conexion.commit()
        return {
            "id_compra": id_compra,
            "codigo_reserva": codigo_reserva,
            "estado": "PAGADA",
            "total": float(total),
            "email_estado": "PENDIENTE",
            "email_enviado_a": datos["email_comprobante"],
        }
    except IntegrityError as error:
        conexion.rollback()
        error_de_negocio("compras.ocupacion", "No se pudo completar la compra",
                         "Butaca o código ya utilizado. Actualizá la disponibilidad.", HTTP_CONFLICTO)
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def obtener_detalle_compra_db(id_compra: int, id_usuario: int | None = None) -> dict | None:
    parametros = (id_compra,) if id_usuario is None else (id_compra, id_usuario)
    condicion = "" if id_usuario is None else " AND c.id_usuario = %s"
    filas = ejecutar_consulta(
        """SELECT c.id_compra, c.codigo_reserva, c.estado, c.creada_en,
                  c.email_comprobante, c.medio_pago, c.total, c.subtotal_entradas,
                  c.subtotal_servicios, c.cargo_servicio, c.qr_token, c.email_estado,
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
    compra = filas[0]
    compra["inicio"] = compra["inicio"].isoformat(timespec="minutes")
    compra["creada_en"] = compra["creada_en"].isoformat(timespec="seconds")
    for campo in ("total", "subtotal_entradas", "subtotal_servicios", "cargo_servicio"):
        compra[campo] = float(compra[campo])
    entradas = ejecutar_consulta(
        """SELECT e.id_entrada, b.fila, b.numero, e.precio_unitario
           FROM entradas e JOIN butacas b ON b.id_butaca = e.id_butaca
           WHERE e.id_compra = %s ORDER BY b.fila, b.numero""",
        (id_compra,),
    )
    for entrada in entradas:
        entrada["precio_unitario"] = float(entrada["precio_unitario"])
    compra["entradas"] = entradas
    servicios = ejecutar_consulta(
        """SELECT s.nombre AS nombre_servicio, cs.cantidad, cs.precio_unitario
           FROM compra_servicios cs JOIN servicios s ON s.id_servicio = cs.id_servicio
           WHERE cs.id_compra = %s ORDER BY s.nombre""",
        (id_compra,),
    )
    for servicio in servicios:
        servicio["precio_unitario"] = float(servicio["precio_unitario"])
    compra["servicios"] = servicios
    return compra


def listar_compras_usuario_db(id_usuario: int) -> list[dict]:
    filas = ejecutar_consulta(
        """SELECT c.id_compra, c.codigo_reserva, c.estado, c.total,
                  c.creada_en, p.titulo AS pelicula, f.inicio AS fecha_funcion
           FROM compras c JOIN funciones f ON f.id_funcion = c.id_funcion
           JOIN peliculas p ON p.id_pelicula = f.id_pelicula
           WHERE c.id_usuario = %s ORDER BY c.creada_en DESC""",
        (id_usuario,),
    )
    for compra in filas:
        compra["total"] = float(compra["total"])
        compra["creada_en"] = compra["creada_en"].isoformat(timespec="seconds")
        compra["fecha_funcion"] = compra["fecha_funcion"].isoformat(timespec="minutes")
    return filas


def actualizar_estado_email_db(id_compra: int, estado: str) -> None:
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """UPDATE compras SET email_estado = %s, email_intentos = email_intentos + 1,
                   email_enviado_en = CASE WHEN %s = 'ENVIADO' THEN NOW() ELSE email_enviado_en END
                   WHERE id_compra = %s""",
                (estado, estado, id_compra),
            )
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
