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
    pelicula = buscar_pelicula_por_id_db(pelicula_id)
    if pelicula is None:
        raise error_validacion("La película indicada no existe.")
    
    reseñas = buscar_reseñas_por_pelicula_db(pelicula_id)
    return [_formatear_reseña(r) for r in reseñas]


def crear_resena_pelicula(id_pelicula: int, id_usuario: int, datos: dict) -> dict:
    pelicula_id = datos.get("pelicula_id")
    usuario_id = datos.get("usuario_id")
    puntuacion = datos.get("puntuacion")
    comentario = datos.get("comentario", "")

    pelicula = buscar_pelicula_por_id_db(pelicula_id)
    if pelicula is None:
        raise error_validacion("La película indicada no existe.")

    if puntuacion is None or not (1 <= int(puntuacion) <= 5):
        raise error_validacion("La puntuación es obligatoria y debe ser un valor entero entre 1 y 5.")

    asistio = verificar_asistencia_usuario_db(usuario_id, pelicula_id)
    if not asistio:
        raise error_validacion("Acceso denegado. Solo los usuarios con asistencia validada (QR escaneado) pueden dejar reseñas[cite: 3, 10].")

    id_reseña = insertar_reseña_db({
        "pelicula_id": pelicula_id,
        "usuario_id": usuario_id,
        "puntuacion": int(puntuacion),
        "comentario": comentario,
        "fecha": datetime.now()
    })

    return _formatear_reseña(buscar_reseña_por_id_db(id_reseña))

