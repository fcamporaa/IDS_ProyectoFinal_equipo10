from src.utils import construir_error_api


def validar_id_funcion(id_funcion: int) -> int:
    """Valida que id_funcion sea un entero positivo."""
    pass


def validar_filtros_funciones(args) -> dict:
    """Valida filtros para consultar funciones (por película, sala, fecha)."""
    pass


def validar_crear_funcion(datos: dict) -> dict:
    """
    Valida campos obligatorios para programar función:
    - id_pelicula: int positivo
    - id_sala: int positivo
    - inicio: datetime formato único ISO
    - fin: datetime formato único ISO posterior a inicio
    - formato: 2D, 3D, o 4D
    - precio_entrada: decimal positivo
    """
    pass


def validar_actualizar_funcion(datos: dict) -> dict:
    """Valida modificaciones de horario, precio o estado de función."""
    pass
