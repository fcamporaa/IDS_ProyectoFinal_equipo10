from flask import jsonify, request
from src.services.validaciones_services import (
    procesar_validacion_qr,
    listar_historial_validaciones_qr,
)
from src.validators.validaciones_validators import (
    validar_payload_validacion_qr,
    validar_filtros_validaciones_qr,
)


def register_validaciones_routes(app):

    @app.route("/validaciones-qr", methods=["POST"])
    def post_validacion_qr():
        """
        POST /validaciones-qr: Escanea el QR en el ingreso a la sala, verifica que sea válido
        (función/fecha, que no esté usado ni cancelado), marca la compra como utilizada y registra la auditoría (Solo Admin).
        """
        pass

    @app.route("/validaciones-qr", methods=["GET"])
    def get_validaciones_qr():
        """
        GET /validaciones-qr: Lista el registro histórico de validaciones de QR realizadas en puerta (Solo Admin).
        """
        pass
