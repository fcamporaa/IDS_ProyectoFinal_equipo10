from services.api_client import consultar_backend


def listar_servicios_admin(token: str):
    """Obtiene todos los servicios, activos e inactivos, para el ABM."""
    return consultar_backend("/servicios/admin", token, metodo="GET")


def crear_servicio(token: str, datos: dict):
    """Crea un nuevo servicio adicional."""
    return consultar_backend("/servicios", token, metodo="POST", datos=datos)


def actualizar_servicio(token: str, id_servicio: int, datos: dict):
    """Modifica un servicio existente."""
    return consultar_backend(
        f"/servicios/{id_servicio}",
        token,
        metodo="PUT",
        datos=datos,
    )


def dar_de_baja_servicio(token: str, id_servicio: int):
    """Da de baja lógica un servicio."""
    return consultar_backend(f"/servicios/{id_servicio}", token, metodo="DELETE")


def reactivar_servicio(token: str, id_servicio: int):
    """Reactiva un servicio inactivo reutilizando el PUT de actualización."""
    return actualizar_servicio(token, id_servicio, {"activo": True})
