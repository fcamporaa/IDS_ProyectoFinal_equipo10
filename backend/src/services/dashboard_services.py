from src.constants import FRANJAS_HORARIAS_DASHBOARD
from src.repositories.dashboard_repository import (
    obtener_porcentaje_ocupacion_db,
    obtener_ventas_por_genero_db,
    obtener_ventas_por_franja_horaria_db,
    obtener_metricas_cancelaciones_db,
)


def _a_float(valor) -> float:
    """Convierte Decimal o None proveniente de MySQL a float seguro."""
    return round(float(valor or 0), 2)


def _turno_de_hora(hora: int) -> str:
    """Traduce una hora de inicio de función a su franja horaria."""
    for franja in FRANJAS_HORARIAS_DASHBOARD:
        if hora in franja["horas"]:
            return franja["turno"]
    return "Sin turno"


def obtener_metricas_ocupacion(filtros: dict) -> list[dict]:
    """Calcula el porcentaje de ocupación agrupado por función, sala y película."""
    filas = obtener_porcentaje_ocupacion_db(filtros)
    metricas = []

    for fila in filas:
        capacidad = int(fila["capacidad_total"] or 0)
        vendidas = int(fila["entradas_vendidas"] or 0)
        porcentaje = round(vendidas * 100.0 / capacidad, 2) if capacidad else 0.0
        metricas.append(
            {
                "id_funcion": fila["id_funcion"],
                "pelicula": fila["pelicula"],
                "sala": fila["sala"],
                "local": fila["local"],
                "capacidad_total": capacidad,
                "entradas_vendidas": vendidas,
                "porcentaje_ocupacion": porcentaje,
            }
        )

    return sorted(
        metricas,
        key=lambda metrica: (
            metrica["porcentaje_ocupacion"],
            metrica["entradas_vendidas"],
        ),
        reverse=True,
    )


def obtener_ventas_por_genero(filtros: dict) -> list[dict]:
    """Calcula recaudación y entradas vendidas agrupadas por género cinematográfico."""
    return [
        {
            "genero": fila["genero"],
            "entradas_vendidas": int(fila["entradas_vendidas"] or 0),
            "total_recaudado": _a_float(fila["total_recaudado"]),
        }
        for fila in obtener_ventas_por_genero_db(filtros)
    ]


def obtener_ventas_franjas_horarias(filtros: dict) -> list[dict]:
    """Genera reporte de turnos y franjas horarias con mayor volumen de entradas."""
    agrupado = {}

    for fila in obtener_ventas_por_franja_horaria_db(filtros):
        turno = _turno_de_hora(int(fila["hora"]))
        if turno not in agrupado:
            agrupado[turno] = {
                "turno": turno,
                "entradas_vendidas": 0,
                "total_recaudado": 0.0,
            }
        agrupado[turno]["entradas_vendidas"] += int(fila["entradas_vendidas"] or 0)
        agrupado[turno]["total_recaudado"] += float(fila["total_recaudado"] or 0)

    resultado = []
    for fila in agrupado.values():
        fila["total_recaudado"] = _a_float(fila["total_recaudado"])
        resultado.append(fila)

    return sorted(
        resultado,
        key=lambda fila: (fila["entradas_vendidas"], fila["total_recaudado"]),
        reverse=True,
    )


def obtener_estadisticas_cancelaciones(filtros: dict) -> dict:
    """Calcula tasa y estadísticas de compras canceladas."""
    fila = obtener_metricas_cancelaciones_db(filtros)
    total_compras = int(fila.get("total_compras") or 0)
    total_canceladas = int(fila.get("total_canceladas") or 0)
    tasa = (
        round(total_canceladas * 100.0 / total_compras, 2)
        if total_compras
        else 0.0
    )

    return {
        "total_compras": total_compras,
        "total_canceladas": total_canceladas,
        "tasa_cancelacion_porcentaje": tasa,
        "monto_devuelto": _a_float(fila.get("monto_devuelto")),
    }


def obtener_reporte_ventas_consolidado(filtros: dict) -> dict:
        detalle_por_funcion = obtener_ventas_por_funcion_db()
    ranking_peliculas = obtener_ranking_peliculas_db()
    
    return {
        "detalle_por_funcion": detalle_por_funcion,
        "ranking_peliculas": ranking_peliculas
        }

