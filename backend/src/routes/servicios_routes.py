from flask import jsonify, request
from src.services.servicios_services import (
    listar_servicios,
    listar_servicios_admin,
    crear_servicio,
    actualizar_servicio,
    eliminar_servicio,
)
from src.validators.servicios_validators import (
    validar_id_servicio,
    validar_crear_servicio,
    validar_actualizar_servicio,
)
from src.utils import construir_error_api, validar_admin


def register_servicios_routes(app):

    @app.route("/servicios", methods=["GET"])
    def get_servicios():
        """GET /servicios: Lista los servicios adicionales activos."""
        return jsonify(listar_servicios()), 200

    @app.route("/servicios/admin", methods=["GET"])
    def get_servicios_admin():
        """GET /servicios/admin: Lista todos los servicios, activos e inactivos (Solo Admin)."""
        validar_admin(request.headers.get("Authorization"))
        return jsonify(listar_servicios_admin()), 200

    @app.route("/servicios", methods=["POST"])
    def post_servicio():
        """POST /servicios: Crea un servicio adicional (Solo Admin)."""
        validar_admin(request.headers.get("Authorization"))

        datos_validados = validar_crear_servicio(request.get_json(silent=True))
        if isinstance(datos_validados, dict) and "errors" in datos_validados:
            return jsonify(datos_validados), 400

        resultado = crear_servicio(datos_validados)
        if "errors" in resultado:
            return jsonify(resultado), 400
        return jsonify(resultado), 201

    @app.route("/servicios/<int:id>", methods=["PUT"])
    def put_servicio(id):
        """PUT /servicios/{id}: Modifica un servicio existente (Solo Admin)."""
        validar_admin(request.headers.get("Authorization"))

        id_validado = validar_id_servicio(id)
        if isinstance(id_validado, dict):
            return jsonify(id_validado), 400

        datos_validados = validar_actualizar_servicio(request.get_json(silent=True))
        if isinstance(datos_validados, dict) and "errors" in datos_validados:
            return jsonify(datos_validados), 400

        resultado = actualizar_servicio(id_validado, datos_validados)
        if resultado is None:
            return jsonify(construir_error_api(
                "error.servicio.no_encontrado",
                "Servicio no encontrado",
                "No existe un servicio con el ID indicado.",
            )), 404
        if "errors" in resultado:
            return jsonify(resultado), 400
        return jsonify(resultado), 200

    @app.route("/servicios/<int:id>", methods=["DELETE"])
    def delete_servicio(id):
        """DELETE /servicios/{id}: Da de baja un servicio (Solo Admin)."""
        validar_admin(request.headers.get("Authorization"))

        id_validado = validar_id_servicio(id)
        if isinstance(id_validado, dict):
            return jsonify(id_validado), 400

        if not eliminar_servicio(id_validado):
            return jsonify(construir_error_api(
                "error.servicio.no_encontrado",
                "Servicio no encontrado",
                "No existe un servicio activo con el ID indicado.",
            )), 404
        return jsonify({"mensaje": "Servicio dado de baja exitosamente."}), 200
