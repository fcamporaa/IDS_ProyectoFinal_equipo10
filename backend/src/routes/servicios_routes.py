from flask import jsonify, request
from src.services.servicios_services import (
    autorizar_administrador,
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
from src.utils import construir_error_api


def _obtener_usuario_administrador():
    partes_autorizacion = request.headers.get("Authorization", "").split()
    if len(partes_autorizacion) != 2 or partes_autorizacion[0].lower() != "bearer":
        return None, construir_error_api(
            "error.auth.token_requerido",
            "Autenticación requerida",
            "Envía un token válido como Bearer en el encabezado Authorization.",
        )

    resultado = autorizar_administrador(partes_autorizacion[1])
    if "errors" in resultado:
        codigo_error = resultado["errors"][0]["code"]
        if codigo_error == "error.auth.permisos_insuficientes":
            return None, resultado
        if codigo_error == "error.auth.usuario_inactivo":
            return None, resultado
        if codigo_error == "error.auth.usuario_no_encontrado":
            return None, resultado
        return None, resultado
    return resultado, None


def register_servicios_routes(app):

    @app.route("/servicios", methods=["GET"])
    def get_servicios():
        """GET /servicios: Lista los servicios adicionales activos."""
        return jsonify(listar_servicios()), 200

    @app.route("/servicios", methods=["POST"])
    def post_servicio():
        """POST /servicios: Crea un servicio adicional (Solo Admin)."""
        usuario, error = _obtener_usuario_administrador()
        if error is not None:
            codigo_error = error["errors"][0]["code"]
            estado = 403 if codigo_error == "error.auth.permisos_insuficientes" else 401
            return jsonify(error), estado

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
        usuario, error = _obtener_usuario_administrador()
        if error is not None:
            codigo_error = error["errors"][0]["code"]
            estado = 403 if codigo_error == "error.auth.permisos_insuficientes" else 401
            return jsonify(error), estado

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
        usuario, error = _obtener_usuario_administrador()
        if error is not None:
            codigo_error = error["errors"][0]["code"]
            estado = 403 if codigo_error == "error.auth.permisos_insuficientes" else 401
            return jsonify(error), estado

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
