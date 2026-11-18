"""Servicios HTTP para el ABM de funciones del backoffice."""
from services.api_client import consultar_backend


def listar_funciones_admin(token: str):
    """Obtiene todas las funciones, incluyendo canceladas y finalizadas, para el ABM."""
    return consultar_backend("/funciones/admin", token, metodo="GET")


def listar_peliculas_admin(token: str):
    """Obtiene las películas para el select; la ruta filtra las activas."""
    return consultar_backend("/peliculas/admin", token, metodo="GET")


def listar_locales(token: str):
    """Obtiene los complejos activos para el select."""
    return consultar_backend("/locales", token, metodo="GET")


def listar_salas_por_local(token: str, id_local: int):
    """Obtiene las salas de un complejo para el select."""
    return consultar_backend(f"/locales/{id_local}/salas", token, metodo="GET")


def crear_funcion(token: str, datos: dict):
    """Programa una función nueva."""
    return consultar_backend("/funciones", token, metodo="POST", datos=datos)


def actualizar_funcion(token: str, id_funcion: int, datos: dict):
    """Modifica una función existente."""
    return consultar_backend(
        f"/funciones/{id_funcion}", token, metodo="PUT", datos=datos
    )


def dar_de_baja_funcion(token: str, id_funcion: int):
    """Cancela lógicamente una función."""
    return consultar_backend(f"/funciones/{id_funcion}", token, metodo="DELETE")
