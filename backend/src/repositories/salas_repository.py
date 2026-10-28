from src.db import ejecutar_consulta, ejecutar_mutacion


def obtener_locales_db() -> list[dict]:
    """Obtiene los locales activos de la tabla locales."""
    pass


def obtener_salas_por_local_db(id_local: int) -> list[dict]:
    """Obtiene las salas pertenecientes a un local y cuenta sus butacas."""
    pass


def buscar_sala_por_id_db(id_sala: int) -> dict | None:
    """Busca una sala por su id_sala."""
    pass


def obtener_butacas_por_sala_db(id_sala: int) -> list[dict]:
    """Obtiene las butacas de una sala ordenadas por fila y número."""
    pass


def actualizar_sala_db(id_sala: int, datos: dict) -> int:
    """Actualiza una sala en la tabla salas."""
    pass
