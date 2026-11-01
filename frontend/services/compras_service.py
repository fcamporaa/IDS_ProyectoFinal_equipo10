import os
import requests


def _consultar_backend(metodo: str, ruta: str, token: str, datos: dict | None = None):
    base = os.getenv("BACKEND_URL", "http://127.0.0.1:5000").rstrip("/")
    try:
        if metodo == "POST":
            respuesta = requests.post(
                f"{base}{ruta}", json=datos,
                headers={"Authorization": f"Bearer {token}"}, timeout=15,
            )
        else:
            respuesta = requests.get(
                f"{base}{ruta}", headers={"Authorization": f"Bearer {token}"}, timeout=15,
            )
        cuerpo = respuesta.json()
        if not isinstance(cuerpo, (dict, list)):
            return {"error": "Respuesta inválida."}, 502
        return cuerpo, respuesta.status_code
    except (requests.RequestException, ValueError):
        return {"error": "Backend no disponible o respuesta inválida."}, 502


def enviar_compra_al_backend(datos: dict, token: str):
    return _consultar_backend("POST", "/compras", token, datos)


def obtener_compra_del_backend(id_compra: int, token: str):
    return _consultar_backend("GET", f"/compras/{id_compra}", token)


def reenviar_comprobante_al_backend(id_compra: int, token: str):
    return _consultar_backend("POST", f"/compras/{id_compra}/reenviar-comprobante", token)
