from src.db import ejecutar_consulta, ejecutar_mutacion


def obtener_cartelera_vigente_db(filtros: dict = None) -> list[dict]:
    """Consulta las películas activas que tienen funciones vigentes."""
    pass


def buscar_pelicula_por_id_db(id_pelicula: int) -> dict | None:
    """Obtiene datos de una película por su id_pelicula."""
    pass


def insertar_pelicula_db(datos: dict) -> int:
    """Inserta una película y devuelve su id autoincremental."""
    pass


def actualizar_pelicula_db(id_pelicula: int, datos: dict) -> int:
    """Actualiza una película en la BD."""
    pass


def dar_de_baja_pelicula_db(id_pelicula: int) -> int:
    """Marca la película como inactiva (activa = 0)."""
    pass


def obtener_generos_db() -> list[dict]:
    """Obtiene todos los registros de la tabla generos."""
    pass


def asociar_genero_a_pelicula_db(id_pelicula: int, id_genero: int) -> int:
    """Inserta en la tabla intermedia pelicula_generos."""
    pass


def obtener_resenas_por_pelicula_db(id_pelicula: int) -> list[dict]:
    """Consulta las reseñas aprobadas de una película."""
    pass


def usuario_tiene_asistencia_confirmada_db(id_usuario: int, id_pelicula: int) -> int | None:
    """
    Verifica si el usuario tiene una compra con QR validado para esa película.
    Retorna id_compra si existe o None.
    """
    pass


def insertar_resena_db(datos: dict) -> int:
    """Inserta una reseña en la tabla resenas."""
    pass
