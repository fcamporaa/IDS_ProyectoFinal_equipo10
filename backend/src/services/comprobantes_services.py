import logging

from src.constants import ESTADO_COMPRA_PENDIENTE, ESTADO_COMPRA_VENDIDA
from src.repositories.compras_repository import (
    obtener_detalle_comprobante_db,
    obtener_entradas_por_compra_db,
    obtener_servicios_por_compra_db,
)
from src.services.qr_services import crear_imagen_qr
from src.utils import enviar_correo_html
from src.config import obtener_config_email


def _preparar_contexto_comprobante(compra: dict) -> dict:
    contexto = compra.copy()
    contexto["inicio"] = contexto["inicio"].isoformat(timespec="minutes")
    contexto["creada_en"] = contexto["creada_en"].isoformat(timespec="seconds")
    for campo in ("total", "subtotal_entradas", "subtotal_servicios", "cargo_servicio"):
        contexto[campo] = float(contexto[campo])

    entradas = obtener_entradas_por_compra_db(contexto["id_compra"])
    for entrada in entradas:
        entrada["precio_unitario"] = float(entrada["precio_unitario"])
    contexto["entradas"] = entradas

    contexto["servicios"] = [
        {
            "nombre_servicio": servicio["nombre_servicio"],
            "cantidad": servicio["cantidad"],
            "precio_unitario": float(servicio["precio_unitario"]),
        }
        for servicio in obtener_servicios_por_compra_db(contexto["id_compra"])
    ]
    return contexto


def enviar_comprobante_compra(id_compra: int, plantilla: str = "compra_confirmada") -> str:
    """Reutilizable por US-19: plantilla 'comprobante_provisorio' sin QR."""
    compra = obtener_detalle_comprobante_db(id_compra)
    if not compra:
        raise ValueError("Compra inexistente")
    if plantilla == "compra_confirmada" and compra["estado"] != ESTADO_COMPRA_VENDIDA:
        raise ValueError("El QR solo se envía para compras pagadas")
    if plantilla == "comprobante_provisorio" and compra["estado"] != ESTADO_COMPRA_PENDIENTE:
        raise ValueError("El comprobante provisorio requiere una reserva pendiente")

    compra = _preparar_contexto_comprobante(compra)
    try:
        imagenes = {}
        if plantilla == "compra_confirmada" and obtener_config_email()["modo"] == "smtp":
            imagenes["entrada-qr"] = crear_imagen_qr(compra["qr_token"])
        estado = enviar_correo_html(
            destinatario=compra["email_comprobante"],
            asunto=("Tu entrada de Cine Paradiso" if plantilla == "compra_confirmada"
                    else "Reserva pendiente de pago — Cine Paradiso"),
            plantilla=plantilla,
            contexto=compra,
            imagenes_inline=imagenes,
        )
    except Exception:
        logging.exception("Falló el envío del comprobante de la compra %s", id_compra)
        raise
    return estado
