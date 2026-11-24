from services.api_client import consultar_backend


def listar_locales(token: str):
    """Obtiene los complejos activos para el select del formulario."""
    return consultar_backend("/locales", token, metodo="GET")


def listar_salas_admin(token: str):
    """Obtiene todas las salas (activas e inactivas) para el ABM."""
    return consultar_backend("/salas/admin", token, metodo="GET")


def crear_sala(token: str, id_local: int, datos: dict):
    """Crea una sala con su grilla de butacas en el complejo indicado."""
    return consultar_backend(
        f"/locales/{id_local}/salas",
        token,
        metodo="POST",
        datos=datos,
    )


def generar_butacas(token: str, id_sala: int, datos: dict):
    """Genera butacas para una sala que aún no tiene grilla."""
    return consultar_backend(
        f"/salas/{id_sala}/butacas",
        token,
        metodo="POST",
        datos=datos,
    )


def actualizar_sala(token: str, id_sala: int, datos: dict):
    """Actualiza número o estado activo de una sala."""
    return consultar_backend(
        f"/salas/{id_sala}",
        token,
        metodo="PUT",
        datos=datos,
    )


def dar_de_baja_sala(token: str, id_sala: int):
    """Da de baja lógica una sala."""
    return actualizar_sala(token, id_sala, {"activa": False})


def reactivar_sala(token: str, id_sala: int):
    """Reactiva una sala inactiva."""
    return actualizar_sala(token, id_sala, {"activa": True})
