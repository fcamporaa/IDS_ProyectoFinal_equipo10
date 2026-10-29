from src.repositories.validaciones_repository import (
    buscar_compra_por_qr_token_db,
    marcar_qr_utilizado_db,
    registrar_auditoria_validacion_db,
    obtener_historial_validaciones_db,
)
from src.utils import construir_error_api


def procesar_validacion_qr(datos: dict) -> dict:
    """
    1. Busca compra por qr_token.
    2. Valida que exista, coincida función/fecha, no esté cancelada ni previamente usada.
    3. Registra auditoría en validaciones_qr ('EXITO', 'FALLIDO', 'REUTILIZADO').
    4. Si es válida, marca qr_validado_en con datetime actual.
    """
    pass


def listar_historial_validaciones_qr(filtros: dict) -> list[dict]:
    """Lista las validaciones registradas en puerta."""
    pass
