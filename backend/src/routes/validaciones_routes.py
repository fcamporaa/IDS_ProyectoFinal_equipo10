from flask import jsonify, request

from src.constants import HTTP_OK, HTTP_SOLICITUD_INVALIDA
from src.services.validaciones_services import (
    procesar_validacion_qr,
    listar_historial_validaciones_qr,
)
from src.validators.auth_validators import validar_autorizacion_admin
from src.validators.validaciones_validators import (
    validar_payload_validacion_qr,
    validar_filtros_validaciones_qr,
)
from src.utils import construir_error_api


def register_validaciones_routes(app):
    @app.route("/validaciones-qr", methods=["POST"])
    def post_validacion_qr():
        """Autoriza o rechaza el ingreso y registra la validación de un QR (solo Admin)."""
        autorizacion = validar_autorizacion_admin(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify({"errors": autorizacion["errors"]}), autorizacion.get("status", 401)

        datos = validar_payload_validacion_qr(request.get_json(silent=True))
        if "errors" in datos:
            return jsonify(datos), HTTP_SOLICITUD_INVALIDA

        resultado = procesar_validacion_qr(datos, autorizacion["usuario_id"])
        if not resultado["autorizado"]:
            codigo = (
                "error.qr.reutilizado"
                if resultado["resultado"] == "REUTILIZADO"
                else "error.qr.rechazado"
            )
            return jsonify(construir_error_api(
                codigo, "Ingreso rechazado", resultado["mensaje"]
            )), HTTP_SOLICITUD_INVALIDA
        return jsonify(resultado), HTTP_OK

    @app.route("/validaciones-qr", methods=["GET"])
    def get_validaciones_qr():
        """Lista el historial de validaciones QR (solo Admin)."""
        autorizacion = validar_autorizacion_admin(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify({"errors": autorizacion["errors"]}), autorizacion.get("status", 401)

        filtros = validar_filtros_validaciones_qr(request.args)
        if "errors" in filtros:
            return jsonify(filtros), HTTP_SOLICITUD_INVALIDA
        return jsonify(listar_historial_validaciones_qr(filtros)), HTTP_OK
