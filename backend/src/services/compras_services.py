from datetime import datetime, timedelta
import secrets

from src.config import pagos_simulados_habilitados
from src.services.qr_services import crear_token_qr
from src.services.comprobantes_services import enviar_comprobante_compra
from src.repositories.compras_repository import registrar_compra_pagada_db, obtener_detalle_comprobante_db
from src.constants import HTTP_NO_IMPLEMENTADO, HTTP_CONFLICTO
from src.utils import ahora_local, error_de_negocio

from src.constants import FORMATO_DATETIME_SQL
from src.repositories.compras_repository import (
    verificar_butacas_disponibles_db,
    insertar_compra_db,
    insertar_entradas_db,
    insertar_servicios_compra_db,
    obtener_compras_por_usuario_db,
    obtener_detalle_compra_db,
    obtener_entradas_por_compra_db,
    obtener_servicios_por_compra_db,
    actualizar_estado_compra_db,
    liberar_butacas_compra_db,
    cancelar_compra_atomica_db,
)
from src.utils import construir_error_api


def procesar_compra(id_usuario: int, datos: dict) -> dict:
    """Registra la compra demostrativa, genera el QR y envía el correo tras COMMIT."""
    if not pagos_simulados_habilitados():
        error_de_negocio(
            "compras.pago", "Pago no disponible",
            "Habilitá ALLOW_SIMULATED_PAYMENTS solo en desarrollo.", HTTP_NO_IMPLEMENTADO,
        )
    codigo_reserva = "CP-" + secrets.token_hex(8).upper()
    qr_token = crear_token_qr()
    compra = registrar_compra_pagada_db(id_usuario, datos, codigo_reserva, qr_token)
    try:
        compra["email_estado"] = enviar_comprobante_compra(compra["id_compra"])
    except Exception:
        # El commit de la compra ya ocurrió: un fallo de SMTP no debe liberar las entradas.
        compra["email_estado"] = "ERROR"
    return compra


def listar_mis_compras(id_usuario: int) -> list[dict]:
    """Devuelve el historial de compras del cliente logueado."""
    return obtener_compras_por_usuario_db(id_usuario)


def obtener_detalle_compra(id_compra: int, id_usuario: int) -> dict:
    """Obtiene el detalle completo de una compra con sus entradas, servicios y QR."""
    compra = obtener_detalle_compra_db(id_compra)
    if compra is None:
        return construir_error_api(
            "error.compras.no_encontrada",
            "Compra no encontrada",
            "No existe una compra con el identificador indicado.",
        )
    if compra["id_usuario"] != id_usuario:
        return construir_error_api(
            "error.auth.prohibido",
            "Acceso denegado",
            "No posee autorización para consultar esta compra.",
        )

    compra["funcion"] = {
        "id_funcion": compra.pop("id_funcion"),
        "id_pelicula": compra.pop("id_pelicula"),
        "titulo_pelicula": compra.pop("titulo_pelicula"),
        "id_sala": compra.pop("id_sala"),
        "numero_sala": compra.pop("numero_sala"),
        "nombre_local": compra.pop("nombre_local"),
        "inicio": compra.pop("inicio"),
        "fin": compra.pop("fin"),
        "formato": compra.pop("formato"),
        "idioma": compra.pop("idioma"),
        "subtitulada": bool(compra.pop("subtitulada")),
        "precio_entrada": compra.pop("precio_entrada"),
        "estado": compra.pop("estado_funcion"),
    }
    compra.pop("id_usuario")
    compra["entradas"] = obtener_entradas_por_compra_db(id_compra)
    compra["servicios"] = obtener_servicios_por_compra_db(id_compra)
    return compra


def cancelar_compra(id_compra: int, id_usuario: int) -> dict | None:
    """
    Valida estar dentro del tiempo límite antes del inicio de la función.
    Libera las butacas y marca la compra como CANCELADA.
    """
    compra = obtener_detalle_compra_db(id_compra)
    if compra is None:
        return construir_error_api(
            "error.compras.no_encontrada",
            "Compra no encontrada",
            "No existe una compra con el identificador indicado.",
        )
    if compra["id_usuario"] != id_usuario:
        return construir_error_api(
            "error.auth.prohibido",
            "Acceso denegado",
            "No posee autorización para cancelar esta compra.",
        )
    if compra["estado"] != "PAGADA" or compra["qr_validado_en"] is not None:
        return construir_error_api(
            "error.compras.no_cancelable",
            "Compra no cancelable",
            "Solo se pueden cancelar compras pagadas cuyo QR no haya sido utilizado.",
        )

    inicio = compra["inicio"]
    if isinstance(inicio, str):
        inicio = datetime.strptime(inicio, FORMATO_DATETIME_SQL)
    if inicio <= ahora_local() + timedelta(hours=24):
        return construir_error_api(
            "error.compras.plazo_cancelacion_vencido",
            "Plazo de cancelación vencido",
            "La compra solo puede cancelarse hasta 24 horas antes del inicio de la función.",
        )

    cancelada_en = ahora_local().strftime(FORMATO_DATETIME_SQL)
    if not cancelar_compra_atomica_db(id_compra, id_usuario, cancelada_en):
        return construir_error_api(
            "error.compras.no_cancelable",
            "Compra no cancelable",
            "La compra ya fue cancelada, utilizada o superó el plazo de cancelación.",
        )
    return None


def reenviar_comprobante(id_compra: int, id_usuario: int) -> str | None:
    """Solo el dueño puede reenviar un QR, y exclusivamente para compras pagadas."""
    compra = obtener_detalle_comprobante_db(id_compra, id_usuario)
    if compra is None:
        return None
    if compra["estado"] != "PAGADA" or compra.get("qr_validado_en") is not None:
        error_de_negocio(
            "compras.estado", "Comprobante no disponible",
            "La compra no está pagada o su QR ya fue usado.", HTTP_CONFLICTO,
        )
    return enviar_comprobante_compra(id_compra)
