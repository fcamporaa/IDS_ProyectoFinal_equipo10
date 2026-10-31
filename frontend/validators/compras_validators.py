import re


def validar_formulario_compra(formulario) -> dict:
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
    return {
        "id_funcion": id_funcion,
        "butacas_ids": butacas,
        "medio_pago": "TARJETA_SIMULADA",
        "email_comprobante": email,
        "servicios": [],
    }
