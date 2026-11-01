from datetime import datetime
from src.repositories.validaciones_repository import (
    validar_y_registrar_qr_db, obtener_historial_validaciones_db,
)


def procesar_validacion_qr(datos: dict, id_administrador: int) -> dict:
    """El repositorio aplica la verificación y el marcado de forma atómica."""
    return validar_y_registrar_qr_db(
        datos["qr_token"], id_administrador, datos["id_sala"]
    )


def listar_historial_validaciones_qr(filtros: dict) -> list[dict]:
    historial = obtener_historial_validaciones_db(filtros)
    for item in historial:
        fecha = item.get("fecha_validacion")
        if isinstance(fecha, datetime):
            item["fecha_validacion"] = fecha.isoformat(timespec="seconds")
    return historial
