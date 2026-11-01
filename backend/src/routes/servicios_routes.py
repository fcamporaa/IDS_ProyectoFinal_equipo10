from flask import jsonify, request
from src.services.servicios_services import (
    listar_servicios,
    crear_servicio,
    actualizar_servicio,
    eliminar_servicio,
)
from src.validators.servicios_validators import (
    validar_id_servicio,
    validar_crear_servicio,
    validar_actualizar_servicio,
)


def register_servicios_routes(app):

    @app.route("/servicios", methods=["GET"])
    def get_servicios():
        """
        GET /servicios: Lista los servicios adicionales activos (comida, bebidas, estacionamiento, VIP).
        """
        pass

    @app.route("/servicios", methods=["POST"])
    def post_servicio():
        """
        POST /servicios: Crea un nuevo servicio adicional (Solo Admin).
        """
        pass

    @app.route("/servicios/<int:id>", methods=["PUT"])
    def put_servicio(id):
        """
        PUT /servicios/{id}: Modifica los datos o el precio de un servicio existente (Solo Admin).
        """
        pass

    @app.route("/servicios/<int:id>", methods=["DELETE"])
    def delete_servicio(id):
        """
        DELETE /servicios/{id}: Da de baja un servicio (Solo Admin).
        """
        pass
