from src.utils import construir_error_api


def validar_id_pelicula(id_pelicula: int) -> int:
    """Valida que el id_pelicula sea un entero positivo."""
    pass


def validar_filtros_cartelera(args) -> dict:
    """Valida los filtros de búsqueda para la cartelera pública (género, fecha, etc.)."""
    pass


def validar_crear_pelicula(datos: dict) -> dict:
    """
    Valida campos obligatorios al crear película:
    - titulo: str no vacío
    - origen_api: OMDB, TMDB, o CUSTOM
    - duracion_min: int positivo
    - generos: list[int]
    """
    pass


def validar_actualizar_pelicula(datos: dict) -> dict:
    """Valida campos permitidos para modificación de película."""
    pass


def validar_busqueda_externa(args) -> dict:
    """Valida parámetro 'query' o 'titulo' para la búsqueda en API externa."""
    pass


def validar_crear_resena(datos: dict) -> dict:
    """
    Valida puntuación (1 a 5) y comentario opcional para reseña.
    """
    pass
