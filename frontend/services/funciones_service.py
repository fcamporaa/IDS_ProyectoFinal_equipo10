from services.api_client import consultar_backend


def obtener_mapa_butacas_del_backend(id_funcion: int):
    """
    Consume GET /funciones/<id>/butacas del Backend.
    Retorna (datos_butacas, status_code).
    """
    return consultar_backend(f"/funciones/{id_funcion}/butacas", metodo="GET")


def obtener_funciones_del_backend(filtros: dict | None = None):
    """
    Consume GET /funciones del Backend con filtros opcionales.
    Retorna (lista_funciones, status_code).
    """
    return consultar_backend("/funciones", metodo="GET", params=filtros)


def obtener_detalle_funcion_del_backend(id_funcion: int):
    """
    Obtiene los datos de una función específica buscando por id_funcion en la lista de funciones vigentes.
    Retorna (datos_funcion, status_code).
    """
    funciones, status = obtener_funciones_del_backend()
    if status == 200 and isinstance(funciones, list):
        for f in funciones:
            if f.get("id_funcion") == id_funcion:
                return f, 200
        return {"error": "Función no encontrada o ya finalizada."}, 404
    return funciones, status

