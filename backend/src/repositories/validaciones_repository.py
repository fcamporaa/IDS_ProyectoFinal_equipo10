from src.db import ejecutar_consulta, ejecutar_mutacion


def buscar_compra_por_qr_token_db(qr_token: str) -> dict | None:
    """Busca compra y datos de la función por qr_token."""
    pass


def marcar_qr_utilizado_db(id_compra: int, fecha_validacion: str) -> int:
    """Actualiza qr_validado_en en la tabla compras."""
    pass


def registrar_auditoria_validacion_db(id_compra: int, id_admin: int, fecha: str, resultado: str) -> int:
    """Inserta registro en la tabla validaciones_qr."""
    pass


def obtener_historial_validaciones_db(filtros: dict = None) -> list[dict]:
    """Obtiene el historial de validaciones con datos de la compra y del administrador."""
    pass
