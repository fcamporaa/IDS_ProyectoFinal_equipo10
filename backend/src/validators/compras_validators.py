from src.utils import construir_error_api


def validar_id_compra(id_compra: int) -> int:
    """Valida que id_compra sea un entero positivo."""
    pass


def validar_datos_compra(datos: dict) -> dict:
    """
    Valida payload para procesar compra:
    - id_funcion: int positivo
    - butacas: list[int] no vacía
    - servicios: list[dict] opcional con id_servicio y cantidad
    - medio_pago: str no vacío
    - email_comprobante: email válido
    """
    pass
