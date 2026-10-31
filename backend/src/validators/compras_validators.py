from src.constants import (
    MAX_BUTACAS_COMPRA, MAX_ITEMS_SERVICIOS, MEDIO_PAGO_DEMO,
    HTTP_SOLICITUD_INVALIDA, HTTP_NO_IMPLEMENTADO,
)
from src.utils import es_entero_positivo, es_email_valido, error_de_negocio


def validar_id_compra(id_compra: int) -> int:
    if not es_entero_positivo(id_compra):
        error_de_negocio("compras.id", "ID inválido", "Debe ser positivo.", HTTP_SOLICITUD_INVALIDA)
    return id_compra


def validar_datos_compra(datos: dict) -> dict:
    if not isinstance(datos, dict):
        error_de_negocio("compras.json", "JSON inválido", "Se esperaba un objeto.", HTTP_SOLICITUD_INVALIDA)
    funcion = datos.get("id_funcion")
    butacas = datos.get("butacas_ids")
    servicios = datos.get("servicios", [])
    email = datos.get("email_comprobante", "")
    medio_pago = datos.get("medio_pago")

    if not es_entero_positivo(funcion):
        error_de_negocio("compras.funcion", "Función inválida", "ID positivo obligatorio.", HTTP_SOLICITUD_INVALIDA)
    if (not isinstance(butacas, list) or not 1 <= len(butacas) <= MAX_BUTACAS_COMPRA
            or any(not es_entero_positivo(i) for i in butacas)
            or len(set(butacas)) != len(butacas)):
        error_de_negocio("compras.butacas", "Butacas inválidas", "1 a 20 IDs positivos sin repeticiones.", HTTP_SOLICITUD_INVALIDA)
    if not isinstance(servicios, list) or len(servicios) > MAX_ITEMS_SERVICIOS:
        error_de_negocio("compras.servicios", "Servicios inválidos", "Se esperaba una lista corta.", HTTP_SOLICITUD_INVALIDA)
    ids = []
    for servicio in servicios:
        if (not isinstance(servicio, dict)
                or not es_entero_positivo(servicio.get("id_servicio"))
                or not es_entero_positivo(servicio.get("cantidad"))
                or servicio["cantidad"] > 99):
            error_de_negocio("compras.servicios", "Servicio inválido", "ID y cantidad positivos.", HTTP_SOLICITUD_INVALIDA)
        ids.append(servicio["id_servicio"])
    if len(set(ids)) != len(ids):
        error_de_negocio("compras.servicios", "Servicios repetidos", "Agrupá las cantidades.", HTTP_SOLICITUD_INVALIDA)
    if not es_email_valido(email):
        error_de_negocio("compras.email", "Email inválido", "Ingresá un correo válido.", HTTP_SOLICITUD_INVALIDA)
    if medio_pago != MEDIO_PAGO_DEMO:
        error_de_negocio("compras.pago", "Medio de pago no implementado", "No hay procesador bancario integrado.", HTTP_NO_IMPLEMENTADO)
    return {
        "id_funcion": funcion,
        "butacas_ids": butacas,
        "servicios": servicios,
        "medio_pago": medio_pago,
        "email_comprobante": email.strip(),
    }
