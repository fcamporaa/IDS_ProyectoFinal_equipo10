from src.utils import construir_error_api, es_entero_positivo, es_email_valido
from src.constants import MAX_BUTACAS_COMPRA, MAX_ITEMS_SERVICIOS, MEDIO_PAGO_DEMO
from src.constants import DURACION_RESERVA_BUTACAS_SEGUNDOS


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
