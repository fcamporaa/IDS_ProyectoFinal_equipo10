from src.repositories.funciones_repository import (
    obtener_funciones_db,
    buscar_funcion_por_id_db,
    hay_solapamiento_horario_db,
    insertar_funcion_db,
    actualizar_funcion_db,
    tiene_entradas_activas_db,
    cancelar_funcion_db,
    obtener_estado_butacas_funcion_db,
)
from src.utils import construir_error_api


def listar_funciones(filtros: dict) -> list[dict]:
    """Lista las funciones programadas filtradas."""
    pass


def crear_funcion(datos: dict) -> dict:
    """
    Programa una nueva función validando que la sala esté libre en esa franja horaria.
    """
    pass


def actualizar_funcion(id_funcion: int, datos: dict) -> None:
    """Modifica horario, precio o estado de la función."""
    pass


def eliminar_funcion(id_funcion: int) -> None:
    """Cancela o da de baja una función programada sin entradas activas."""
    pass


def obtener_mapa_butacas_funcion(id_funcion: int) -> dict:
    """Devuelve el mapa de butacas de la sala indicando libres y ocupadas."""
    pass
