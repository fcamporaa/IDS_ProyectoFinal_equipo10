import logging

from src.repositories.compras_repository import (
    obtener_detalle_comprobante_db,
)
from src.services.qr_services import crear_imagen_qr
from src.utils import enviar_correo_html
from src.config import obtener_config_email


def enviar_comprobante_compra(id_compra: int, plantilla: str = "compra_confirmada") -> str:
    """Reutilizable por US-19: plantilla 'comprobante_provisorio' sin QR."""
    compra = obtener_detalle_comprobante_db(id_compra)
    if not compra:
        raise ValueError("Compra inexistente")
    if plantilla == "compra_confirmada" and compra["estado"] != "PAGADA":
        raise ValueError("El QR solo se envía para compras pagadas")
    if plantilla == "comprobante_provisorio" and compra["estado"] != "PENDIENTE":
        raise ValueError("El comprobante provisorio requiere una reserva pendiente")

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
