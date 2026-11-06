import os

import requests


def consultar_backend(
    ruta: str,
    token: str | None = None,
    params: dict | None = None,
    metodo: str = "GET",
):
    """Ejecuta una petición HTTP al backend y normaliza errores de red o formato."""
    base = os.getenv("BACKEND_URL", "http://127.0.0.1:5000").rstrip("/")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        respuesta = requests.request(
            metodo,
            f"{base}{ruta}",
            headers=headers,
            params=params,
            timeout=15,
        )
        cuerpo = respuesta.json()
        if not isinstance(cuerpo, (dict, list)):
            return {"error": "Respuesta inválida del backend."}, 502
        return cuerpo, respuesta.status_code
    except (requests.RequestException, ValueError):
        return {"error": "Backend no disponible o respuesta inválida."}, 502
