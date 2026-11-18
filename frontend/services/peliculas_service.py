"""Cliente del backend para el módulo de películas: cartelera, detalle, géneros y reseñas."""
from services.api_client import consultar_backend


def obtener_cartelera_vigente(filtros: dict):
    """Obtiene la cartelera vigente. Filtros opcionales: id_genero, titulo y clasificacion."""
    return consultar_backend("/peliculas", params=filtros)


def obtener_detalle_pelicula(id_pelicula: int):
    """Obtiene el detalle de una película junto con sus funciones vigentes."""
    return consultar_backend(f"/peliculas/{id_pelicula}")


def obtener_resenas_pelicula(id_pelicula: int, token: str | None = None):
    """Obtiene las reseñas y puntuaciones de una película. Con token, permite identificar la reseña propia."""
    return consultar_backend(
        f"/peliculas/{id_pelicula}/resenas", token=token, metodo="GET"
    )


def crear_resena_pelicula(id_pelicula: int, token: str, datos: dict):
    """Envía una reseña de compra al backend para validar asistencia y guardarla."""
    return consultar_backend(
        f"/peliculas/{id_pelicula}/resenas",
        token=token,
        metodo="POST",
        datos=datos,
    )


def obtener_generos():
    """Consume GET /generos y devuelve (datos, código HTTP) para que la ruta decida."""
    return consultar_backend("/generos", metodo="GET")