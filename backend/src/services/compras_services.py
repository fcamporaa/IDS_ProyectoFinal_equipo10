from datetime import datetime, timedelta
import logging
from datetime import timedelta
from decimal import Decimal
import secrets
import threading

from src.config import pagos_simulados_habilitados
from src.constants import (
    ESTADO_COMPRA_CANCELADA,
    ESTADO_COMPRA_VENDIDA,
    ESTADO_ENTRADA_CANCELADA,
    ESTADO_ENTRADA_OCUPADA,
    ESTADOS_ENTRADA_OCUPACION,
    FORMATO_DATETIME_SQL,
)
from src.repositories.compras_repository import (
    bloquear_funcion_para_reserva_db,
    cancelar_entradas_de_compra_db,
    eliminar_reserva_temporal_compra_db,
    liberar_reserva_temporal_db,
    eliminar_reservas_temporales_usuario_db,
    eliminar_reservas_temporales_vencidas_db,
    ejecutar_registro_compra_db,
    ejecutar_transaccion_compras_db,
    hay_entrada_ocupada_db,
    hay_reserva_temporal_ajena_db,
    insertar_compra_db,
    insertar_entradas_db,
    insertar_reservas_temporales_db,
    insertar_servicios_compra_db,
    marcar_compra_cancelada_db,
    obtener_butacas_solicitadas_db,
    obtener_butacas_reservadas_por_usuario_db,
    obtener_compras_por_usuario_db,
    obtener_compra_para_cancelar_db,
    obtener_detalle_compra_db,
    obtener_detalle_comprobante_db,
    obtener_entradas_por_compra_db,
    obtener_funcion_para_compra_db,
    obtener_reservas_por_token_db,
    obtener_servicios_por_ids_db,
    obtener_servicios_por_compra_db,
)
from src.services.comprobantes_services import enviar_comprobante_compra
from src.services.qr_services import crear_token_qr
from src.utils import ahora_local, formatear_datetime_iso
from src.validators.compras_validators import (
    validar_butacas_disponibles_para_compra,
    validar_butacas_disponibles_para_reserva,
    validar_butacas_solicitadas,
    validar_compra_cancelable,
    validar_compra_para_reenvio,
    validar_compra_propietario,
    validar_compra_registrada,
    validar_funcion_disponible,
    validar_pagos_simulados_habilitados,
    validar_reserva_compra,
    validar_reserva_temporal_ajena_para_compra,
    validar_reservas_temporales_existentes,
    validar_servicios_activos,
)


def _calcular_importes_compra(
    funcion: dict, butacas: list[dict], servicios: list[dict], precios_servicios_db: list[dict]
) -> dict:
    validar_servicios_activos(servicios, precios_servicios_db)
    precios_servicios = {
        servicio["id_servicio"]: Decimal(str(servicio["precio"]))
        for servicio in precios_servicios_db
    }

    precio_base = Decimal(str(funcion["precio_entrada"]))
    precios_butacas = {}
    subtotal_entradas = Decimal("0.00")
    for butaca in butacas:
        precio = (
            round(precio_base * Decimal("1.25"), 2)
            if butaca["fila"] in ("E", "F", "G")
            else precio_base
        )
        precios_butacas[butaca["id_butaca"]] = precio
        subtotal_entradas += precio

    subtotal_servicios = sum(
        (
            precios_servicios[servicio["id_servicio"]] * servicio["cantidad"]
            for servicio in servicios
        ),
        Decimal("0.00"),
    )
    cargo_servicio = Decimal("0.00")
    return {
        "precios_butacas": precios_butacas,
        "precios_servicios": precios_servicios,
        "subtotal_entradas": subtotal_entradas,
        "subtotal_servicios": subtotal_servicios,
        "cargo_servicio": cargo_servicio,
        "total": subtotal_entradas + subtotal_servicios + cargo_servicio,
    }


def _registrar_compra_pagada(
    id_usuario: int, datos: dict, codigo_reserva: str, qr_token: str
) -> dict:
    ahora = ahora_local()

    def operacion(cursor):
        funcion = obtener_funcion_para_compra_db(cursor, datos["id_funcion"])
        validar_funcion_disponible(funcion, ahora)

        butacas = obtener_butacas_solicitadas_db(
            cursor, funcion["id_sala"], datos["butacas_ids"]
        )
        validar_butacas_solicitadas(butacas, datos["butacas_ids"])
        validar_butacas_disponibles_para_compra(
            hay_entrada_ocupada_db(
                cursor, datos["id_funcion"], datos["butacas_ids"], ESTADOS_ENTRADA_OCUPACION
            )
        )

        reservas = obtener_butacas_reservadas_por_usuario_db(
            cursor,
            datos["id_funcion"],
            id_usuario,
            datos["token_reserva"],
            ahora,
            datos["butacas_ids"],
        )
        validar_reserva_compra(reservas, datos["butacas_ids"])
        validar_reserva_temporal_ajena_para_compra(
            hay_reserva_temporal_ajena_db(
                cursor, datos["id_funcion"], datos["butacas_ids"], ahora,
                datos["token_reserva"],
            )
        )

        precios_servicios_db = obtener_servicios_por_ids_db(
            cursor, [servicio["id_servicio"] for servicio in datos["servicios"]]
        )
        importes = _calcular_importes_compra(
            funcion, butacas, datos["servicios"], precios_servicios_db
        )
        compra = {
            "id_usuario": id_usuario,
            "id_funcion": datos["id_funcion"],
            "codigo_reserva": codigo_reserva,
            "email_comprobante": datos["email_comprobante"],
            "estado": ESTADO_COMPRA_VENDIDA,
            "medio_pago": datos["medio_pago"],
            "qr_token": qr_token,
            **importes,
        }
        id_compra = insertar_compra_db(cursor, compra)
        insertar_entradas_db(
            cursor,
            [
                {
                    "id_compra": id_compra,
                    "id_funcion": datos["id_funcion"],
                    "id_butaca": butaca["id_butaca"],
                    "precio_unitario": importes["precios_butacas"][butaca["id_butaca"]],
                    "estado": ESTADO_ENTRADA_OCUPADA,
                }
                for butaca in butacas
            ],
        )
        eliminar_reserva_temporal_compra_db(
            cursor, id_usuario, datos["token_reserva"]
        )
        insertar_servicios_compra_db(
            cursor,
            [
                {
                    "id_compra": id_compra,
                    "id_servicio": servicio["id_servicio"],
                    "cantidad": servicio["cantidad"],
                    "precio_unitario": importes["precios_servicios"][servicio["id_servicio"]],
                }
                for servicio in datos["servicios"]
            ],
        )
        return {
            "id_compra": id_compra,
            "codigo_reserva": codigo_reserva,
            "estado": "PAGADA",
            "total": float(importes["total"]),
            "email_estado": "PENDIENTE",
            "email_enviado_a": datos["email_comprobante"],
        }

    return validar_compra_registrada(ejecutar_registro_compra_db(operacion))


def procesar_compra(id_usuario: int, datos: dict) -> dict:
    """Registra la compra demostrativa, genera el QR y envía el correo tras COMMIT."""
    validar_pagos_simulados_habilitados(pagos_simulados_habilitados())
    codigo_reserva = "CP-" + secrets.token_hex(8).upper()
    qr_token = crear_token_qr()
    compra = _registrar_compra_pagada(id_usuario, datos, codigo_reserva, qr_token)
    
    # Enviar comprobante por correo en segundo plano para no demorar la respuesta HTTP
    def _enviar_correo_background(id_compra_target):
        try:
            enviar_comprobante_compra(id_compra_target)
        except Exception:
            logging.exception("Fallo el envio en background del comprobante %s", id_compra_target)

    hilo = threading.Thread(target=_enviar_correo_background, args=(compra["id_compra"],), daemon=True)
    hilo.start()
    compra["email_estado"] = "EN_COLA"
    return compra


def reservar_butacas_temporalmente(id_usuario: int, datos: dict) -> dict:
    """Aparta las butacas por el tiempo restante del checkout."""
    ahora = ahora_local()
    expira_en = ahora + timedelta(seconds=datos["duracion_segundos"])

    def operacion(cursor):
        funcion = bloquear_funcion_para_reserva_db(cursor, datos["id_funcion"])
        validar_funcion_disponible(funcion, ahora)

        butacas = obtener_butacas_solicitadas_db(
            cursor, funcion["id_sala"], datos["butacas_ids"]
        )
        validar_butacas_solicitadas(butacas, datos["butacas_ids"])

        reservas_existentes = obtener_reservas_por_token_db(
            cursor, datos["token_reserva"]
        )
        vencimiento_final = validar_reservas_temporales_existentes(
            reservas_existentes, id_usuario, ahora, expira_en
        )
        validar_butacas_disponibles_para_reserva(
            hay_entrada_ocupada_db(
                cursor, datos["id_funcion"], datos["butacas_ids"], ESTADOS_ENTRADA_OCUPACION
            ),
            hay_reserva_temporal_ajena_db(
                cursor, datos["id_funcion"], datos["butacas_ids"], ahora,
                datos["token_reserva"],
            ),
        )

        eliminar_reservas_temporales_usuario_db(
            cursor, id_usuario, datos["token_reserva"]
        )
        eliminar_reservas_temporales_vencidas_db(
            cursor, datos["id_funcion"], datos["butacas_ids"], ahora
        )
        insertar_reservas_temporales_db(
            cursor,
            [
                (
                    datos["id_funcion"], id_butaca, id_usuario,
                    datos["token_reserva"], vencimiento_final,
                )
                for id_butaca in datos["butacas_ids"]
            ],
        )
        return {"token_reserva": datos["token_reserva"], "estado": "RESERVADA"}

    return ejecutar_transaccion_compras_db(operacion)


def liberar_reserva_temporal(id_usuario: int, token_reserva: str) -> None:
    liberar_reserva_temporal_db(id_usuario, token_reserva)


def listar_mis_compras(id_usuario: int) -> list[dict]:
    """Devuelve el historial de compras del cliente logueado."""
    compras = obtener_compras_por_usuario_db(id_usuario)
    return [
        {
            **c,
            "fecha_funcion": (
                formatear_datetime_iso(c["fecha_funcion"])
                if c.get("fecha_funcion")
                else None
            ),
            "creada_en": (
                formatear_datetime_iso(c["creada_en"])
                if c.get("creada_en")
                else None
            ),
        }
        for c in compras
    ]


def obtener_detalle_compra(id_compra: int, id_usuario: int) -> dict:
    """Obtiene el detalle completo de una compra con sus entradas, servicios y QR."""
    compra = obtener_detalle_compra_db(id_compra)
    validar_compra_propietario(compra, id_usuario)

    inicio_dt = compra.pop("inicio")
    fin_dt = compra.pop("fin")
    compra["funcion"] = {
        "id_funcion": compra.pop("id_funcion"),
        "id_pelicula": compra.pop("id_pelicula"),
        "titulo_pelicula": compra.pop("titulo_pelicula"),
        "id_sala": compra.pop("id_sala"),
        "numero_sala": compra.pop("numero_sala"),
        "nombre_local": compra.pop("nombre_local"),
        "inicio": formatear_datetime_iso(inicio_dt) if inicio_dt else None,
        "fin": formatear_datetime_iso(fin_dt) if fin_dt else None,
        "formato": compra.pop("formato"),
        "idioma": compra.pop("idioma"),
        "subtitulada": bool(compra.pop("subtitulada")),
        "precio_entrada": compra.pop("precio_entrada"),
        "estado": compra.pop("estado_funcion"),
    }
    compra.pop("id_usuario")
    compra["creada_en"] = (
        formatear_datetime_iso(compra["creada_en"])
        if compra.get("creada_en")
        else None
    )
    if compra.get("qr_validado_en"):
        compra["qr_validado_en"] = formatear_datetime_iso(compra["qr_validado_en"])
    compra["entradas"] = obtener_entradas_por_compra_db(id_compra)
    compra["servicios"] = obtener_servicios_por_compra_db(id_compra)
    return compra


def cancelar_compra(id_compra: int, id_usuario: int) -> dict | None:
    """
    Valida estar dentro del tiempo límite antes del inicio de la función.
    Libera las butacas y marca la compra como CANCELADA.
    """
    compra = obtener_detalle_compra_db(id_compra)
    validar_compra_cancelable(compra, id_usuario, ahora_local())

    cancelada_en = ahora_local().strftime(FORMATO_DATETIME_SQL)

    def operacion(cursor):
        compra_actual = obtener_compra_para_cancelar_db(
            cursor, id_compra, id_usuario
        )
        validar_compra_cancelable(
            compra_actual, id_usuario, ahora_local(), revalidando=True
        )
        marcar_compra_cancelada_db(
            cursor, id_compra, ESTADO_COMPRA_CANCELADA, cancelada_en
        )
        cancelar_entradas_de_compra_db(
            cursor, id_compra, ESTADO_ENTRADA_CANCELADA, ESTADOS_ENTRADA_OCUPACION
        )
        return True

    ejecutar_transaccion_compras_db(operacion)
    return None


def reenviar_comprobante(id_compra: int, id_usuario: int) -> str | None:
    """Solo el dueño puede reenviar un QR, y exclusivamente para compras pagadas."""
    compra = obtener_detalle_comprobante_db(id_compra, id_usuario)
    validar_compra_para_reenvio(compra)
    return enviar_comprobante_compra(id_compra)
