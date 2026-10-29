from src.db import ejecutar_consulta


def obtener_porcentaje_ocupacion_db(filtros: dict = None) -> list[dict]:
    """Consulta de ocupación por función cruzando entradas vendidas vs capacidad de sala."""
    pass


def obtener_ventas_por_genero_db(filtros: dict = None) -> list[dict]:
    """Consulta de ventas agrupada por género cinematográfico."""
    pass


def obtener_ventas_por_franja_horaria_db(filtros: dict = None) -> list[dict]:
    """Consulta de ventas agrupada por hora/turno de inicio de función."""
    pass


def obtener_metricas_cancelaciones_db(filtros: dict = None) -> dict:
    """Consulta de total de compras vs compras canceladas."""
    pass


def obtener_consolidado_ventas_db(filtros: dict = None) -> list[dict]:
    """Consulta de ranking de películas con más recaudación y espectadores."""
    pass
