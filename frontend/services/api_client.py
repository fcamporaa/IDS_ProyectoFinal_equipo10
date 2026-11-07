import os
import requests


def consultar_backend(
    ruta: str,
    token: str | None = None,
    params: dict | None = None,
    metodo: str = "GET",
    datos: dict | None = None,
):
    """
    Cliente HTTP transversal y centralizado para consumir la API REST del Backend desde Flask SSR.
    Soporta GET, POST, PUT, DELETE con serialización JSON, headers Bearer y manejo unificado de errores.

    Retorna una tupla: (cuerpo_respuesta, codigo_http)
    """
    base = os.getenv("BACKEND_URL", "http://127.0.0.1:5000").rstrip("/")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        respuesta = requests.request(
            method=metodo.upper(),
            url=f"{base}{ruta}",
            headers=headers,
            params=params,
            json=datos if datos is not None else None,
            timeout=15,
        )

        try:
            cuerpo = respuesta.json()
        except ValueError:
            cuerpo = {"mensaje": respuesta.text}

        if not isinstance(cuerpo, (dict, list)):
            return {"error": "Respuesta inválida del backend."}, 502

        return cuerpo, respuesta.status_code
    except requests.RequestException:
        return {"error": "Backend no disponible o error de comunicación."}, 502
