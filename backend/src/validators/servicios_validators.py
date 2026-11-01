from src.utils import construir_error_api


def validar_id_servicio(id_servicio: int) -> int:
    """Valida que id_servicio sea un entero positivo."""
    pass


def validar_crear_servicio(datos: dict) -> dict:
    """
    Valida campos para crear servicio:
    - nombre: str no vacío
    - tipo: COMIDA o BEBIDA
    - precio: decimal positivo
    """
    pass


def validar_actualizar_servicio(datos: dict) -> dict:
    """Valida campos para actualizar servicio."""
    pass
