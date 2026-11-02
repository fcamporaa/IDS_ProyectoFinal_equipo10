from services.api_client import consultar_backend


def obtener_locales(token: str):
    """Obtiene los complejos disponibles para el filtro del dashboard."""
    return consultar_backend("/locales", token)


def obtener_metricas_ocupacion(token: str, filtros: dict):
    """Obtiene las métricas de ocupación por función, sala y película."""
    return consultar_backend("/dashboard/ocupacion", token, filtros)


def obtener_ventas_por_genero(token: str, filtros: dict):
    """Obtiene la recaudación y las entradas vendidas por género."""
    return consultar_backend("/dashboard/ventas-genero", token, filtros)


def obtener_franjas_horarias(token: str, filtros: dict):
    """Obtiene el volumen de entradas vendidas por franja horaria."""
    return consultar_backend("/dashboard/franjas-horarias", token, filtros)


def obtener_estadisticas_cancelaciones(token: str, filtros: dict):
    """Obtiene la tasa y el detalle de compras canceladas."""
    return consultar_backend("/dashboard/cancelaciones", token, filtros)
