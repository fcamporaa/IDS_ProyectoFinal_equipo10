from src.repositories.dashboard_repository import (
    obtener_porcentaje_ocupacion_db,
    obtener_ventas_por_genero_db,
    obtener_ventas_por_franja_horaria_db,
    obtener_metricas_cancelaciones_db,
    obtener_consolidado_ventas_db,
)
from src.utils import construir_error_api


def obtener_metricas_ocupacion(filtros: dict) -> list[dict]:
    """Calcula el porcentaje de ocupación agrupado por función, sala y película."""
    pass


def obtener_ventas_por_genero(filtros: dict) -> list[dict]:
    """Calcula recaudación y entradas vendidas agrupadas por género cinematográfico."""
    pass


def obtener_ventas_franjas_horarias(filtros: dict) -> list[dict]:
    """Genera reporte de turnos y franjas horarias con mayor volumen de entradas."""
    pass


def obtener_estadisticas_cancelaciones(filtros: dict) -> dict:
    """Calcula tasa y estadísticas de compras canceladas."""
    pass


def obtener_reporte_ventas_consolidado(filtros: dict) -> dict:
    """Genera consolidado de ventas por función y ranking de películas más vistas."""
    pass
