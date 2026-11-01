from datetime import datetime, timedelta

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
    """
    1. Verifica que las butacas sigan libres para esa función.
    2. Calcula subtotales de entradas, servicios y total.
    3. Registra compra, entradas y servicios asociados.
    4. Genera QR token único.
    5. Envía factura/comprobante con QR por email (stub/mock).
    """
    pass


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
    if inicio <= datetime.now() + timedelta(hours=24):
        return construir_error_api(
            "error.compras.plazo_cancelacion_vencido",
            "Plazo de cancelación vencido",
            "La compra solo puede cancelarse hasta 24 horas antes del inicio de la función.",
        )

    cancelada_en = datetime.now().strftime(FORMATO_DATETIME_SQL)
    if not cancelar_compra_atomica_db(id_compra, id_usuario, cancelada_en):
        return construir_error_api(
            "error.compras.no_cancelable",
            "Compra no cancelable",
            "La compra ya fue cancelada, utilizada o superó el plazo de cancelación.",
        )
    return None
