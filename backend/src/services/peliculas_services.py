from src.repositories.peliculas_repository import (
    obtener_cartelera_vigente_db,
    buscar_pelicula_por_id_db,
    insertar_pelicula_db,
    actualizar_pelicula_db,
    dar_de_baja_pelicula_db,
    obtener_generos_db,
    asociar_genero_a_pelicula_db,
    obtener_resenas_por_pelicula_db,
    insertar_resena_db,
    usuario_tiene_asistencia_confirmada_db,
)
from src.utils import construir_error_api


def listar_cartelera(filtros: dict) -> list[dict]:
    """Lista las películas actualmente en cartelera con sus géneros."""
    pass


def obtener_detalle_pelicula(id_pelicula: int) -> dict:
    """Obtiene el detalle completo de una película y sus funciones vigentes."""
    pass


def crear_pelicula(datos: dict) -> dict:
    """Crea una nueva película y asocia sus géneros en BD."""
    pass


def actualizar_pelicula(id_pelicula: int, datos: dict) -> None:
    """Actualiza datos de la película."""
    pass


def eliminar_pelicula(id_pelicula: int) -> None:
    """Da de baja lógica una película de la cartelera."""
    pass


def buscar_peliculas_externas(filtros: dict) -> list[dict]:
    """Consulta la API externa (OMDb / TMDb) para buscar películas clásicas."""
    pass


def listar_generos() -> list[dict]:
    """Devuelve el listado de todos los géneros disponibles."""
    pass


def listar_resenas_pelicula(id_pelicula: int) -> list[dict]:
    """Lista las reseñas y puntuaciones de una película."""
    pass


def crear_resena_pelicula(id_pelicula: int, id_usuario: int, datos: dict) -> dict:
    """
    Registra una reseña validando que el usuario tenga una compra
    con QR validado efectivamente en puerta.
    """
    pass
