from src.repositories.compras_repository import (
    verificar_butacas_disponibles_db,
    insertar_compra_db,
    insertar_entradas_db,
    insertar_servicios_compra_db,
    obtener_compras_por_usuario_db,
    obtener_detalle_compra_db,
    obtener_entradas_por_compra_db,
    obtener_servicios_por_compra_db,
    actualizar_estado_compra_db,
    liberar_butacas_compra_db,
)
from src.utils import construir_error_api


def procesar_compra(id_usuario: int, datos: dict) -> dict:
    """
    1. Verifica que las butacas sigan libres para esa función.
    2. Calcula subtotales de entradas, servicios y total.
    3. Registra compra, entradas y servicios asociados.
    4. Genera QR token único.
    5. Envía factura/comprobante con QR por email (stub/mock).
    """
    pass


def listar_mis_compras(id_usuario: int) -> list[dict]:
    """Devuelve el historial de compras del cliente logueado."""
    pass


def obtener_detalle_compra(id_compra: int) -> dict:
    """Obtiene el detalle completo de una compra con sus entradas, servicios y QR."""
    pass


def cancelar_compra(id_compra: int, id_usuario: int) -> None:
    """
    Valida estar dentro del tiempo límite antes del inicio de la función.
    Libera las butacas y marca la compra como CANCELADA.
    """
    pass
