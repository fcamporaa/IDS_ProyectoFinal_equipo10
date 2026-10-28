from src.repositories.servicios_repository import (
    obtener_servicios_activos_db,
    buscar_servicio_por_id_db,
    insertar_servicio_db,
    actualizar_servicio_db,
    dar_de_baja_servicio_db,
)
from src.utils import construir_error_api


def listar_servicios() -> list[dict]:
    """Lista todos los servicios adicionales activos."""
    pass


def crear_servicio(datos: dict) -> dict:
    """Crea un nuevo servicio adicional."""
    pass


def actualizar_servicio(id_servicio: int, datos: dict) -> None:
    """Modifica datos o precio de un servicio."""
    pass


def eliminar_servicio(id_servicio: int) -> None:
    """Da de baja lógica un servicio adicional."""
    pass
