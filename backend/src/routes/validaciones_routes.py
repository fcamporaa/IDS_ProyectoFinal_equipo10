from http import HTTPStatus
from flask import jsonify, request
from src.services.auth_services import obtener_perfil_usuario
from src.validators.auth_validators import validar_autorizacion
from src.utils import construir_error_api
from src.services.validaciones_services import (
    procesar_validacion_qr, listar_historial_validaciones_qr,
)
from src.validators.validaciones_validators import (
    validar_payload_validacion_qr, validar_filtros_validaciones_qr,
)


def _administrador_actual():
    autorizacion = validar_autorizacion(request.headers.get("Authorization"))
    if "errors" in autorizacion:
        return None, (jsonify(autorizacion), HTTPStatus.UNAUTHORIZED)
    usuario = obtener_perfil_usuario(autorizacion["usuario_id"])
    if "errors" in usuario or not usuario.get("activo"):
        return None, (jsonify(construir_error_api(
            "error.auth.inactivo", "Autenticación requerida",
            "La cuenta no está activa o no existe."
        )), HTTPStatus.UNAUTHORIZED)
    if usuario["rol"] != "ADMINISTRADOR":
        return None, (jsonify(construir_error_api(
            "error.auth.prohibido", "Acceso denegado",
            "Solo un administrador puede validar códigos QR."
        )), HTTPStatus.FORBIDDEN)
    return usuario, None


def register_validaciones_routes(app):
    @app.route("/validaciones-qr", methods=["POST"])
    def post_validacion_qr():
        usuario, error = _administrador_actual()
        if error:
            return error
        datos = validar_payload_validacion_qr(request.get_json(silent=True))
        if "errors" in datos:
            return jsonify(datos), HTTPStatus.BAD_REQUEST
        resultado = procesar_validacion_qr(datos, usuario["id_usuario"])
        estado_http = 200 if resultado["autorizado"] else 400
        return jsonify(resultado), estado_http

    @app.route("/validaciones-qr", methods=["GET"])
    def get_validaciones_qr():
        usuario, error = _administrador_actual()
        if error:
            return error
        filtros = validar_filtros_validaciones_qr(request.args)
        if "errors" in filtros:
            return jsonify(filtros), HTTPStatus.BAD_REQUEST
        return jsonify(listar_historial_validaciones_qr(filtros)), HTTPStatus.OK
