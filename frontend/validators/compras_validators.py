import json
import re


def validar_servicios_seleccionados(servicios) -> list[dict]:
    if isinstance(servicios, str):
        try:
            servicios = json.loads(servicios)
        except json.JSONDecodeError as error:
            raise ValueError("La selección de servicios no es válida.") from error

    if not isinstance(servicios, list) or len(servicios) > 20:
        raise ValueError("La selección de servicios no es válida.")

    resultado = []
    ids_servicios = set()
    for item in servicios:
        if not isinstance(item, dict):
            raise ValueError("Cada servicio debe incluir un ID y una cantidad.")
        id_servicio = item.get("id_servicio")
        cantidad = item.get("cantidad")
        if (
            type(id_servicio) is not int
            or id_servicio <= 0
            or type(cantidad) is not int
            or cantidad < 0
            or cantidad > 99
        ):
            raise ValueError(
                "Los IDs deben ser positivos y la cantidad debe estar entre 0 y 99."
            )
        if id_servicio in ids_servicios:
            raise ValueError("Un servicio no puede aparecer más de una vez.")
        ids_servicios.add(id_servicio)
        if cantidad > 0:
            resultado.append({"id_servicio": id_servicio, "cantidad": cantidad})

    return resultado


def validar_formulario_compra(formulario, servicios_seleccionados=None) -> dict:
    try:
        id_funcion = int(formulario.get("id_funcion", ""))
        butacas = [int(b) for b in formulario.getlist("butacas_ids") if b.strip()]
    except (ValueError, TypeError) as error:
        raise ValueError("La función y las butacas deben ser enteros positivos.") from error
    if id_funcion <= 0 or not butacas or any(b <= 0 for b in butacas):
        raise ValueError("Seleccioná una función y al menos una butaca.")
    if len(set(butacas)) != len(butacas):
        raise ValueError("Hay butacas seleccionadas más de una vez.")
    email = formulario.get("email_comprobante", "").strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 255:
        raise ValueError("El correo no es válido.")
    if formulario.get("medio_pago") != "TARJETA_SIMULADA":
        raise ValueError("Solo existe el pago simulado de desarrollo.")
    servicios = validar_servicios_seleccionados(servicios_seleccionados or [])
    return {
        "id_funcion": id_funcion,
        "butacas_ids": butacas,
        "medio_pago": "TARJETA_SIMULADA",
        "email_comprobante": email,
        "servicios": servicios,
    }
