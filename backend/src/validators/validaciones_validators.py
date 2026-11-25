import re

from src.constants import RESULTADOS_VALIDACION_QR
from src.utils import construir_error_api


def validar_payload_validacion_qr(datos: dict) -> dict:
    """Valida el QR escaneado y la sala opcional; el administrador proviene del JWT."""
    if not isinstance(datos, dict):
        return construir_error_api(
            "error.validacion.cuerpo", "Cuerpo inválido",
            "No se pudo leer el código QR.",
        )
    if set(datos) - {"qr_token", "id_sala"}:
        return construir_error_api(
            "error.validacion.campos", "Datos no válidos",
            "Los datos enviados no son válidos.",
        )
    token = datos.get("qr_token")
    if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_-]{8,160}", token):
        return construir_error_api(
            "error.validacion.qr_token", "QR inválido",
            "El código QR no tiene un formato válido.",
        )
    id_sala = datos.get("id_sala")
    if id_sala is not None and (type(id_sala) is not int or id_sala <= 0):
        return construir_error_api(
            "error.validacion.id_sala", "Sala inválida",
            "Seleccioná una sala válida.",
        )
    return {"qr_token": token, "id_sala": id_sala}


def validar_filtros_validaciones_qr(args) -> dict:
    """Valida los filtros id_compra y resultado del historial de puerta."""
    if set(args) - {"id_compra", "resultado"}:
        return construir_error_api(
            "error.validacion.filtros", "Filtros inválidos",
            "Los filtros utilizados no son válidos.",
        )
    filtros = {}
    id_compra = args.get("id_compra")
    if id_compra is not None:
        if not re.fullmatch(r"[1-9][0-9]*", str(id_compra)) or int(id_compra) > 2147483647:
            return construir_error_api(
                "error.validacion.id_compra", "Compra inválida",
                "Ingresá un número de compra válido.",
            )
        filtros["id_compra"] = int(id_compra)
    resultado = args.get("resultado")
    if resultado is not None:
        if resultado not in RESULTADOS_VALIDACION_QR:
            return construir_error_api(
                "error.validacion.resultado", "Resultado inválido",
                "Seleccioná un resultado válido.",
            )
        filtros["resultado"] = resultado
    return filtros
