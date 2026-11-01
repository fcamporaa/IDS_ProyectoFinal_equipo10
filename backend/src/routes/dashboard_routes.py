from flask import jsonify, request
from src.services.dashboard_services import (
    obtener_metricas_ocupacion,
    obtener_ventas_por_genero,
    obtener_ventas_franjas_horarias,
    obtener_estadisticas_cancelaciones,
    obtener_reporte_ventas_consolidado,
)
from src.validators.dashboard_validators import (
    validar_filtros_dashboard,
)


def register_dashboard_routes(app):

    @app.route("/dashboard/ocupacion", methods=["GET"])
    def get_ocupacion():
        """
        GET /dashboard/ocupación: Métricas de porcentaje de ocupación por función, sala y película (Solo Admin).
        """
        pass

    @app.route("/dashboard/ventas-genero", methods=["GET"])
    def get_ventas_genero():
        """
        GET /dashboard/ventas-genero: Estadísticas de recaudación y entradas vendidas agrupadas por género (Solo Admin).
        """
        pass

    @app.route("/dashboard/franjas-horarias", methods=["GET"])
    def get_franjas_horarias():
        """
        GET /dashboard/franjas-horarias: Reporte de los horarios y turnos con mayor volumen de entradas vendidas (Solo Admin).
        """
        pass

    @app.route("/dashboard/cancelaciones", methods=["GET"])
    def get_cancelaciones():
        """
        GET /dashboard/cancelaciones: Tasa y estadísticas de compras canceladas (Solo Admin).
        """
        pass

    @app.route("/dashboard/reporte-ventas", methods=["GET"])
    def get_reporte_ventas():
        """
        GET /dashboard/reporte-ventas: Obtiene el consolidado de ventas por función y ranking de películas más vistas (Solo Admin).
        """
        pass
