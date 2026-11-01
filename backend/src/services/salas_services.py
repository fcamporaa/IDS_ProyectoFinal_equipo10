from src.repositories.salas_repository import (
    obtener_locales_db,
    obtener_salas_por_local_db,
    buscar_sala_por_id_db,
    obtener_butacas_por_sala_db,
    actualizar_sala_db,
)
from src.utils import construir_error_api


def listar_locales() -> list[dict]:
    """Lista los locales de cine disponibles."""
    pass


def listar_salas_por_local(id_local: int) -> list[dict]:
    """Lista las salas de un complejo y su capacidad total."""
    pass


def obtener_detalle_sala(id_sala: int) -> dict:
    """Obtiene la sala y la grilla o distribución física de sus butacas."""
    pass


def actualizar_configuracion_sala(id_sala: int, datos: dict) -> None:
    """Actualiza configuración de la sala (activa / inactiva)."""
    pass
