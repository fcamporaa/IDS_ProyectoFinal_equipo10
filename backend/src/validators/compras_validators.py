from datetime import datetime, timedelta

from src.constants import (
    DURACION_RESERVA_BUTACAS_SEGUNDOS,
    ESTADO_COMPRA_VENDIDA,
    ESTADO_FUNCION_PROGRAMADA,
    FORMATO_DATETIME_SQL,
    HTTP_CONFLICTO,
    HTTP_NO_ENCONTRADO,
    HTTP_NO_IMPLEMENTADO,
    HTTP_PROHIBIDO,
    HTTP_SOLICITUD_INVALIDA,
    MAX_BUTACAS_COMPRA,
    MAX_ITEMS_SERVICIOS,
    MEDIO_PAGO_DEMO,
)
from src.utils import construir_error_api, es_entero_positivo, es_email_valido, error_de_negocio


def validar_pagos_simulados_habilitados(habilitados: bool) -> None:
    if not habilitados:
        error_de_negocio(
            "compras.pago", "Pago no disponible",
            "Habilitá ALLOW_SIMULATED_PAYMENTS solo en desarrollo.", HTTP_NO_IMPLEMENTADO,
        )


def validar_compra_registrada(compra: dict | None) -> dict:
    if compra is None:
        error_de_negocio(
            "compras.ocupacion", "No se pudo completar la compra",
            "Butaca o código ya utilizado. Actualizá la disponibilidad.", HTTP_CONFLICTO,
        )
    return compra


def validar_funcion_disponible(funcion: dict | None, ahora: datetime) -> None:
    if (
        not funcion
        or funcion["estado"] != ESTADO_FUNCION_PROGRAMADA
        or funcion["inicio"] <= ahora
    ):
        error_de_negocio(
            "compras.funcion", "Función no disponible",
            "La función no existe o ya comenzó.", HTTP_NO_ENCONTRADO,
        )


def validar_butacas_solicitadas(butacas: list[dict], ids_butacas: list[int]) -> None:
    if (
        len(butacas) != len(ids_butacas)
        or any(not butaca["activa"] for butaca in butacas)
    ):
        error_de_negocio(
            "compras.butacas", "Butacas inválidas",
            "Alguna butaca no pertenece a la sala o está inactiva.", HTTP_SOLICITUD_INVALIDA,
        )


def validar_butacas_disponibles_para_compra(hay_entrada_ocupada: bool) -> None:
    if hay_entrada_ocupada:
        error_de_negocio(
            "compras.ocupacion", "Butacas ocupadas",
            "Una de las butacas acaba de ser reservada.", HTTP_CONFLICTO,
        )


def validar_reserva_compra(reservas: list[dict], ids_butacas: list[int]) -> None:
    if len(reservas) != len(ids_butacas):
        error_de_negocio(
            "compras.reserva_expirada", "Reserva no vigente",
            "El apartado de butacas venció o ya no pertenece a esta compra.", HTTP_CONFLICTO,
        )


def validar_reserva_temporal_ajena_para_compra(hay_reserva_ajena: bool) -> None:
    if hay_reserva_ajena:
        error_de_negocio(
            "compras.ocupacion", "Butacas reservadas",
            "Una de las butacas está siendo reservada por otro usuario.", HTTP_CONFLICTO,
        )


def validar_butacas_disponibles_para_reserva(
    hay_entrada_ocupada: bool, hay_reserva_ajena: bool
) -> None:
    if hay_entrada_ocupada:
        error_de_negocio(
            "compras.ocupacion", "Butacas ocupadas",
            "Una de las butacas ya fue comprada o reservada.", HTTP_CONFLICTO,
        )
    if hay_reserva_ajena:
        error_de_negocio(
            "compras.ocupacion", "Butacas reservadas",
            "Una de las butacas está siendo reservada por otro usuario.", HTTP_CONFLICTO,
        )


def validar_reservas_temporales_existentes(
    reservas: list[dict], id_usuario: int, ahora: datetime, expira_en: datetime
) -> datetime:
    if any(reserva["id_usuario"] != id_usuario for reserva in reservas):
        error_de_negocio(
            "compras.reserva", "Reserva inválida",
            "El token de reserva pertenece a otro usuario.", HTTP_CONFLICTO,
        )
    if not reservas:
        return expira_en

    vencimiento_previo = min(reserva["expira_en"] for reserva in reservas)
    if vencimiento_previo <= ahora:
        error_de_negocio(
            "compras.reserva_expirada", "Reserva vencida",
            "El apartado de butacas ya venció.", HTTP_CONFLICTO,
        )
    return min(expira_en, vencimiento_previo)


def validar_servicios_activos(servicios: list[dict], precios_db: list[dict]) -> None:
    precios_por_id = {servicio["id_servicio"]: servicio for servicio in precios_db}
    if len(precios_por_id) != len(servicios) or any(
        not servicio["activo"] for servicio in precios_db
    ):
        error_de_negocio(
            "compras.servicios", "Servicio no disponible",
            "Algún adicional no existe o está inactivo.", HTTP_SOLICITUD_INVALIDA,
        )


def validar_compra_propietario(
    compra: dict | None, id_usuario: int, accion: str = "consultar"
) -> None:
    if compra is None:
        error_de_negocio(
            "error.compras.no_encontrada", "Compra no encontrada",
            "No existe una compra con el identificador indicado.", HTTP_NO_ENCONTRADO,
        )
    if compra["id_usuario"] != id_usuario:
        descripcion = (
            "No posee autorización para cancelar esta compra."
            if accion == "cancelar"
            else "No posee autorización para consultar esta compra."
        )
        error_de_negocio(
            "error.auth.prohibido", "Acceso denegado",
            descripcion, HTTP_PROHIBIDO,
        )


def _inicio_dentro_plazo_cancelacion(inicio, ahora: datetime) -> bool:
    if isinstance(inicio, str):
        inicio = datetime.strptime(inicio, FORMATO_DATETIME_SQL)
    return inicio > ahora + timedelta(hours=24)


def validar_compra_cancelable(
    compra: dict | None, id_usuario: int, ahora: datetime, revalidando: bool = False
) -> None:
    no_cancelable = (
        not compra
        or compra["estado"] != ESTADO_COMPRA_VENDIDA
        or compra["qr_validado_en"] is not None
    )
    if revalidando:
        if no_cancelable or not _inicio_dentro_plazo_cancelacion(compra["inicio"], ahora):
            error_de_negocio(
                "error.compras.no_cancelable", "Compra no cancelable",
                "La compra ya fue cancelada, utilizada o superó el plazo de cancelación.",
                HTTP_SOLICITUD_INVALIDA,
            )
        return

    validar_compra_propietario(compra, id_usuario, "cancelar")
    if no_cancelable:
        error_de_negocio(
            "error.compras.no_cancelable", "Compra no cancelable",
            "Solo se pueden cancelar compras pagadas cuyo QR no haya sido utilizado.",
            HTTP_SOLICITUD_INVALIDA,
        )
    if not _inicio_dentro_plazo_cancelacion(compra["inicio"], ahora):
        error_de_negocio(
            "error.compras.plazo_cancelacion_vencido", "Plazo de cancelación vencido",
            "La compra solo puede cancelarse hasta 24 horas antes del inicio de la función.",
            HTTP_SOLICITUD_INVALIDA,
        )


def validar_compra_para_reenvio(compra: dict | None) -> None:
    if compra is None:
        error_de_negocio(
            "error.compras.no_encontrada", "Compra no encontrada",
            "No existe esa compra.", HTTP_NO_ENCONTRADO,
        )
    if compra["estado"] != ESTADO_COMPRA_VENDIDA or compra.get("qr_validado_en") is not None:
        error_de_negocio(
            "compras.estado", "Comprobante no disponible",
            "La compra no está pagada o su QR ya fue usado.", HTTP_CONFLICTO,
        )


def validar_id_compra(id_compra: int) -> int:
    """Valida que id_compra sea un entero positivo."""
    try:
        id_validado = int(id_compra)
    except (TypeError, ValueError):
        id_validado = 0
    if id_validado <= 0:
        return construir_error_api(
            "error.validacion.id_compra",
            "Compra inválida",
            "No pudimos identificar la compra seleccionada.",
        )
    return id_validado


def validar_datos_compra(datos: dict, email_usuario: str = "") -> dict:
    """Valida los IDs, servicios, correo y medio de pago del checkout."""
    def error(codigo, texto):
        return construir_error_api(codigo, "Compra inválida", texto)

    if not isinstance(datos, dict):
        return error("error.compras.json", "Los datos de la compra no pudieron procesarse.")
    funcion = datos.get("id_funcion")
    butacas = datos.get("butacas_ids")
    token_reserva = datos.get("token_reserva")
    if not es_entero_positivo(funcion):
        return error("error.compras.funcion", "Seleccioná una función válida.")
    if (not isinstance(butacas, list) or not 1 <= len(butacas) <= MAX_BUTACAS_COMPRA
            or any(not es_entero_positivo(b) for b in butacas)
            or len(set(butacas)) != len(butacas)):
        return error("error.compras.butacas", "Seleccioná butacas disponibles sin repetirlas.")
    if not isinstance(token_reserva, str) or not 32 <= len(token_reserva) <= 64:
        return error("error.compras.reserva", "La reserva temporal venció. Volvé a seleccionar tus butacas.")
    servicios = datos.get("servicios", [])
    if not isinstance(servicios, list) or len(servicios) > MAX_ITEMS_SERVICIOS:
        return error("error.compras.servicios", "La selección de servicios no es válida.")
    ids_servicios = []
    for item in servicios:
        if (not isinstance(item, dict) or not es_entero_positivo(item.get("id_servicio"))
                or not es_entero_positivo(item.get("cantidad")) or item["cantidad"] > 99):
            return error("error.compras.servicios", "Seleccioná una cantidad válida para cada servicio.")
        ids_servicios.append(item["id_servicio"])
    if len(ids_servicios) != len(set(ids_servicios)):
        return error("error.compras.servicios", "Solo podés seleccionar cada servicio una vez.")
    email = datos.get("email_comprobante") or email_usuario
    if not es_email_valido(email):
        return error("error.compras.email", "Ingresá un correo electrónico válido.")
    if datos.get("medio_pago") != MEDIO_PAGO_DEMO:
        return error("error.compras.medio_pago", "Este medio de pago no está disponible actualmente.")
    return {
        "id_funcion": funcion,
        "butacas_ids": butacas,
        "token_reserva": token_reserva,
        "servicios": servicios,
        "medio_pago": MEDIO_PAGO_DEMO,
        "email_comprobante": email.strip(),
    }


def validar_datos_reserva_temporal(datos: dict) -> dict:
    """Valida los datos mínimos para apartar butacas temporalmente."""
    if not isinstance(datos, dict):
        return construir_error_api(
            "error.compras.reserva", "Reserva inválida", "Los datos de reserva no son válidos."
        )
    funcion = datos.get("id_funcion")
    butacas = datos.get("butacas_ids")
    token = datos.get("token_reserva")
    duracion = datos.get("duracion_segundos")
    if not es_entero_positivo(funcion):
        return construir_error_api(
            "error.compras.funcion", "Función inválida", "Seleccioná una función válida."
        )
    if (not isinstance(butacas, list) or not 1 <= len(butacas) <= MAX_BUTACAS_COMPRA
            or any(not es_entero_positivo(butaca) for butaca in butacas)
            or len(set(butacas)) != len(butacas)):
        return construir_error_api(
            "error.compras.butacas", "Butacas inválidas", "Seleccioná butacas válidas sin repetirlas."
        )
    if not isinstance(token, str) or not 32 <= len(token) <= 64:
        return construir_error_api(
            "error.compras.token_reserva", "Reserva inválida", "El identificador de reserva no es válido."
        )
    if type(duracion) is not int or not 1 <= duracion <= DURACION_RESERVA_BUTACAS_SEGUNDOS:
        return construir_error_api(
            "error.compras.duracion", "Duración inválida", "El tiempo de reserva no es válido."
        )
    return {
        "id_funcion": funcion,
        "butacas_ids": butacas,
        "token_reserva": token,
        "duracion_segundos": duracion,
    }
