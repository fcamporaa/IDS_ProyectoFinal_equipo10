from flask import jsonify, request
from src.services.salas_services import (
    listar_locales,
    listar_salas_por_local,
    obtener_detalle_sala,
    actualizar_configuracion_sala,
)
from src.validators.salas_validators import (
    validar_id_local,
    validar_id_sala,
    validar_actualizar_sala,
)


def register_salas_routes(app):

    @app.route("/locales", methods=["GET"])
    def get_locales():
        """
        GET /locales: Lista los 3 complejos de cine disponibles.
        """
        pass

    @app.route("/locales/<int:id>/salas", methods=["GET"])
    def get_salas_por_local(id):
        """
        GET /locales/{id}/salas: Lista todas las salas pertenecientes a un complejo específico y su capacidad.
        """
        pass

    @app.route("/salas/<int:id>", methods=["GET"])
    def get_sala(id):
        """
        GET /salas/{id}: Obtiene el detalle de una sala y la distribución física de sus butacas.
        """
        pass

    @app.route("/salas/<int:id>", methods=["PUT"])
    def put_sala(id):
        """
        PUT /salas/{id}: Habilita/deshabilita una sala o actualiza su configuración (Solo Admin).
        """
        pass
