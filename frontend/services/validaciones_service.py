from services.api_client import consultar_backend


def validar_ingreso_qr(token: str, qr_token: str, id_sala: int | None = None):
    """Envía el token QR al backend para validar y registrar el ingreso a sala."""
    payload = {"qr_token": qr_token}
    if id_sala is not None:
        payload["id_sala"] = id_sala
    return consultar_backend("/validaciones-qr", token, metodo="POST", datos=payload)


def listar_validaciones_qr(token: str, filtros: dict | None = None):
    """Obtiene el historial reciente de validaciones QR registradas en puerta."""
    return consultar_backend(
        "/validaciones-qr",
        token,
        params=filtros or None,
        metodo="GET",
    )


def obtener_salas_por_local(token: str, id_local: int):
    """Obtiene las salas de un complejo para el selector opcional de puerta."""
    return consultar_backend(f"/locales/{id_local}/salas", token, metodo="GET")

