import secrets
from src.repositories.compras_repository import (
    registrar_compra_pagada_db,
    obtener_detalle_compra_db,
    listar_compras_usuario_db,
)
from src.services.qr_services import crear_token_qr
from src.services.comprobantes_services import enviar_comprobante_compra
from src.constants import HTTP_NO_IMPLEMENTADO
from src.config import pagos_simulados_habilitados
from src.utils import error_de_negocio


def procesar_compra(id_usuario: int, datos: dict) -> dict:
    """Integración US-08/09. Solo demo: no procesa dinero ni tarjetas bancarias."""
    if not pagos_simulados_habilitados():
        error_de_negocio("compras.pago", "Pago no disponible",
                         "Habilitá ALLOW_SIMULATED_PAYMENTS solo en desarrollo.", HTTP_NO_IMPLEMENTADO)
    codigo_reserva = "CP-" + secrets.token_hex(8).upper()
    qr_token = crear_token_qr()
    compra = registrar_compra_pagada_db(id_usuario, datos, codigo_reserva, qr_token)
    try:
        compra["email_estado"] = enviar_comprobante_compra(compra["id_compra"])
    except Exception:
        # La compra pagada ya fue confirmada; nunca se deshace por fallos SMTP.
        compra["email_estado"] = "ERROR"
    return compra


def obtener_detalle_compra(id_compra: int, id_usuario: int) -> dict | None:
    compra = obtener_detalle_compra_db(id_compra, id_usuario)
    if compra:
        compra.pop("qr_token", None)
    return compra


def listar_mis_compras(id_usuario: int) -> list[dict]:
    return listar_compras_usuario_db(id_usuario)


def reenviar_comprobante(id_compra: int, id_usuario: int) -> str | None:
    compra = obtener_detalle_compra_db(id_compra, id_usuario)
    if not compra:
        return None
    if compra["estado"] != "PAGADA":
        raise ValueError("Compra aún no pagada")
    return enviar_comprobante_compra(id_compra)


def cancelar_compra(id_compra: int, id_usuario: int) -> None:
    """US-10 permanece pendiente: no se confirma cancelación sin implementar reglas."""
    raise NotImplementedError("US-10 no está implementada")
