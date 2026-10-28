from src.db import ejecutar_consulta, ejecutar_mutacion


def obtener_servicios_activos_db() -> list[dict]:
    """Obtiene todos los servicios donde activo = 1."""
    pass


def buscar_servicio_por_id_db(id_servicio: int) -> dict | None:
    """Busca un servicio por su id_servicio."""
    pass


def insertar_servicio_db(datos: dict) -> int:
    """Inserta un nuevo servicio en la tabla servicios."""
    pass


def actualizar_servicio_db(id_servicio: int, datos: dict) -> int:
    """Actualiza un servicio existente."""
    pass


def dar_de_baja_servicio_db(id_servicio: int) -> int:
    """Marca el servicio como inactivo (activo = 0)."""
    pass
