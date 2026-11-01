from http import HTTPStatus

from flask import jsonify, request

from src.services.validaciones_services import (
    autenticar_administrador_validacion,
    procesar_validacion_qr,
    listar_historial_validaciones_qr,
)
from src.validators.validaciones_validators import (
    validar_payload_validacion_qr,
    validar_filtros_validaciones_qr,
)
from src.utils import construir_error_api


def register_validaciones_routes(app):
    @app.route("/validaciones-qr", methods=["POST"])
    def post_validacion_qr():
        id_administrador, error, estado = autenticar_administrador_validacion(
            request.headers.get("Authorization")
        )
        if error:
            return jsonify(error), estado
        datos = validar_payload_validacion_qr(request.get_json(silent=True))
        if "errors" in datos:
            return jsonify(datos), HTTPStatus.BAD_REQUEST
        resultado = procesar_validacion_qr(datos, id_administrador)
        if not resultado["autorizado"]:
            codigo = ("error.qr.reutilizado" if resultado["resultado"] == "REUTILIZADO"
                      else "error.qr.rechazado")
            return jsonify(construir_error_api(
                codigo, "Ingreso rechazado", resultado["mensaje"]
            )), HTTPStatus.BAD_REQUEST
        return jsonify(resultado), HTTPStatus.OK

    @app.route("/validaciones-qr", methods=["GET"])
    def get_validaciones_qr():
        _, error, estado = autenticar_administrador_validacion(
            request.headers.get("Authorization")
        )
        if error:
            return jsonify(error), estado
        filtros = validar_filtros_validaciones_qr(request.args)
        if "errors" in filtros:
            return jsonify(filtros), HTTPStatus.BAD_REQUEST
        return jsonify(listar_historial_validaciones_qr(filtros)), HTTPStatus.OK
