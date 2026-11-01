import re
from src.constants import RESULTADOS_VALIDACION_QR
from src.utils import construir_error_api


def validar_payload_validacion_qr(datos: dict) -> dict:
    """Valida el contenido escaneado. El administrador se obtiene del JWT."""
    if not isinstance(datos, dict):
        return construir_error_api("error.validacion.cuerpo", "Cuerpo inválido",
                                  "Se esperaba un objeto JSON.")
    if set(datos) - {"qr_token", "id_sala"}:
        return construir_error_api("error.validacion.campos", "Campos no permitidos",
                                  "Solo se aceptan qr_token e id_sala.")
    token = datos.get("qr_token")
    if (not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_\-]{8,160}", token)):
        return construir_error_api("error.validacion.qr_token", "QR inválido",
                                  "qr_token debe contener entre 8 y 160 caracteres ASCII de token.")
    sala = datos.get("id_sala")
    if sala is not None and (type(sala) is not int or sala <= 0):
        return construir_error_api("error.validacion.id_sala", "Sala inválida",
                                  "id_sala debe ser un entero positivo.")
    return {"qr_token": token, "id_sala": sala}


def validar_filtros_validaciones_qr(args) -> dict:
    """Admite exactamente los filtros especificados por OpenAPI."""
    if set(args) - {"id_compra", "resultado"}:
        return construir_error_api("error.validacion.filtros", "Filtros inválidos",
                                  "Solo se aceptan id_compra y resultado.")
    filtros = {}
    id_compra = args.get("id_compra")
    if id_compra is not None:
        if not re.fullmatch(r"[1-9][0-9]*", str(id_compra)):
            return construir_error_api("error.validacion.id_compra", "Compra inválida",
                                      "id_compra debe ser un entero positivo.")
        filtros["id_compra"] = int(id_compra)
    resultado = args.get("resultado")
    if resultado is not None:
        if resultado not in RESULTADOS_VALIDACION_QR:
            return construir_error_api("error.validacion.resultado", "Resultado inválido",
                                      "resultado debe ser EXITO, FALLIDO o REUTILIZADO.")
        filtros["resultado"] = resultado
    return filtros
