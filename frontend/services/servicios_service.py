from services.api_client import consultar_backend


def obtener_servicios_del_backend():
    """
    Consulta GET /servicios al backend.
    Devuelve los servicios disponibles y el código HTTP.
    """
    return consultar_backend("/servicios", metodo="GET")