from services.api_client import consultar_backend


def listar_peliculas_admin(token: str):
    """Obtiene todas las películas, activas e inactivas, para el ABM."""
    return consultar_backend("/peliculas/admin", token, metodo="GET")


def obtener_pelicula(token: str, id_pelicula: int):
    """Obtiene el detalle de una película para precargar el formulario de edición."""
    return consultar_backend(f"/peliculas/{id_pelicula}", token, metodo="GET")


def buscar_peliculas_externas(token: str, titulo: str):
    """Busca películas por título en OMDb."""
    return consultar_backend(
        "/peliculas/externas/buscar",
        token,
        params={"query": titulo},
        metodo="GET",
    )


def obtener_pelicula_externa(token: str, id_api: str):
    """Obtiene el detalle de una película de OMDb para precargar la ficha."""
    return consultar_backend(f"/peliculas/externas/{id_api}", token, metodo="GET")


def crear_pelicula(token: str, datos: dict):
    """Registra una película nueva en el backend."""
    return consultar_backend("/peliculas", token, metodo="POST", datos=datos)


def actualizar_pelicula(token: str, id_pelicula: int, datos: dict):
    """Actualiza los campos editables de una película existente."""
    return consultar_backend(
        f"/peliculas/{id_pelicula}",
        token,
        metodo="PUT",
        datos=datos,
    )


def dar_de_baja_pelicula(token: str, id_pelicula: int):
    """Da de baja lógica una película."""
    return consultar_backend(f"/peliculas/{id_pelicula}", token, metodo="DELETE")


def reactivar_pelicula(token: str, id_pelicula: int):
    """Reactiva una película dada de baja reutilizando el PUT de actualización."""
    return actualizar_pelicula(token, id_pelicula, {"activa": True})
