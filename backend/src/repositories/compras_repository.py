from src.db import ejecutar_consulta, ejecutar_mutacion


def verificar_butacas_disponibles_db(id_funcion: int, ids_butacas: list[int]) -> bool:
    """Verifica que ninguna de las butacas solicitadas esté ocupada/reservada en la función."""
    pass


def insertar_compra_db(datos: dict) -> int:
    """Inserta registro en la tabla compras y retorna id_compra."""
    pass


def insertar_entradas_db(entradas: list[dict]) -> None:
    """Inserta las entradas individuales para cada butaca de la compra."""
    pass


def insertar_servicios_compra_db(servicios: list[dict]) -> None:
    """Inserta los ítems en la tabla compra_servicios."""
    pass


def obtener_compras_por_usuario_db(id_usuario: int) -> list[dict]:
    """Obtiene las compras de un usuario ordenadas por creada_en DESC."""
    pass


def obtener_detalle_compra_db(id_compra: int) -> dict | None:
    """Obtiene la cabecera de la compra por id_compra."""
    pass


def obtener_entradas_por_compra_db(id_compra: int) -> list[dict]:
    """Obtiene las entradas y butacas asociadas a una compra."""
    pass


def obtener_servicios_por_compra_db(id_compra: int) -> list[dict]:
    """Obtiene los servicios adquiridos en una compra."""
    pass


def actualizar_estado_compra_db(id_compra: int, estado: str, cancelada_en: str = None) -> int:
    """Actualiza el estado de la compra."""
    pass


def liberar_butacas_compra_db(id_compra: int) -> int:
    """Actualiza el estado de las entradas a CANCELADA para liberar butacas."""
    pass
