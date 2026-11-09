"""Cliente del backend para el módulo de películas: cartelera, detalle, géneros y reseñas (todos endpoints públicos)."""
from services.api_client import consultar_backend


def obtener_cartelera_vigente(filtros: dict):
    """Obtiene la cartelera vigente. Filtros opcionales: id_genero, titulo y clasificacion."""
    return consultar_backend("/peliculas", params=filtros)


def obtener_detalle_pelicula(id_pelicula: int):
    """Obtiene el detalle de una película junto con sus funciones vigentes."""
    return consultar_backend(f"/peliculas/{id_pelicula}")


def obtener_generos():
    """Obtiene el listado de géneros para armar el filtro de la cartelera."""
    return consultar_backend("/generos")


def obtener_resenas(id_pelicula: int):
    """Obtiene las reseñas y puntuaciones de una película."""
    return consultar_backend(f"/peliculas/{id_pelicula}/resenas")
