from datetime import datetime, timedelta

from src.repositories.validaciones_repository import (
    validar_y_registrar_qr_db,
    obtener_historial_validaciones_db,
)
from src.services.auth_services import obtener_perfil_usuario
from src.utils import construir_error_api
from src.validators.auth_validators import validar_autorizacion


def autenticar_administrador_validacion(encabezado: str | None) -> tuple:
    """Reutiliza el JWT de US-02 y comprueba el rol y estado de la cuenta."""
    autorizacion = validar_autorizacion(encabezado)
    if "errors" in autorizacion:
        return None, autorizacion, 401
    perfil = obtener_perfil_usuario(autorizacion["usuario_id"])
    if "errors" in perfil or not perfil.get("activo"):
        return None, construir_error_api(
            "error.auth.inactivo", "No autorizado",
            "La cuenta ya no existe o está inactiva.",
        ), 401
    if perfil["rol"] != "ADMINISTRADOR":
        return None, construir_error_api(
            "error.auth.prohibido", "Acceso denegado",
            "Solo un administrador puede validar códigos QR.",
        ), 403
    return perfil["id_usuario"], None, 200


def evaluar_ingreso_qr(compra: dict, ahora: datetime, id_sala: int | None,
                       entradas_vigentes: int) -> tuple[str, str]:
    """Evalúa las reglas de acceso sobre una compra bloqueada en la transacción."""
    if compra["qr_validado_en"] is not None:
        return "REUTILIZADO", "El código QR ya fue utilizado."
    if compra["estado"] != "PAGADA" or compra["cancelada_en"] is not None:
        return "FALLIDO", "La compra no está pagada o fue cancelada."
    if compra["estado_funcion"] not in ("PROGRAMADA", "EN_CURSO"):
        return "FALLIDO", "La función no está habilitada para ingresar."
    if id_sala is not None and compra["id_sala"] != id_sala:
        return "FALLIDO", "El QR no corresponde a esta sala."
    if not compra["inicio"] - timedelta(minutes=30) <= ahora <= compra["fin"]:
        return "FALLIDO", "El ingreso no está habilitado para la fecha y hora de la función."
    if entradas_vigentes <= 0:
        return "FALLIDO", "La compra no tiene entradas vigentes."
    return "EXITO", "Ingreso autorizado. Compra validada con éxito."


def procesar_validacion_qr(datos: dict, id_administrador: int) -> dict:
    """Coordina la decisión de negocio y la operación SQL atómica."""
    return validar_y_registrar_qr_db(
        datos["qr_token"], id_administrador, datos["id_sala"], evaluar_ingreso_qr,
    )


def listar_historial_validaciones_qr(filtros: dict) -> list[dict]:
    historial = obtener_historial_validaciones_db(filtros)
    for item in historial:
        fecha = item.get("fecha_validacion")
        if isinstance(fecha, datetime):
            item["fecha_validacion"] = fecha.isoformat(timespec="seconds")
    return historial
