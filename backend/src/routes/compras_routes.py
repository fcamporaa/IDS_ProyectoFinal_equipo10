from flask import jsonify, request
from src.services.compras_services import (
    procesar_compra,
    listar_mis_compras,
    obtener_detalle_compra,
    cancelar_compra,
)
from src.validators.compras_validators import (
    validar_id_compra,
    validar_datos_compra,
)


def register_compras_routes(app):

    @app.route("/compras", methods=["POST"])
    def post_compra():
        """
        POST /compras: Procesa la compra (verifica que las butacas sigan libres,
        calcula los servicios adicionales y procesa el pago), genera el QR y envía la factura/QR por email.
        """
        pass

    @app.route("/compras/mis-compras", methods=["GET"])
    def get_mis_compras():
        """
        GET /compras/mis-compras: Devuelve el historial de compras del cliente logueado.
        """
        pass

    @app.route("/compras/<int:id>", methods=["GET"])
    def get_compra(id):
        """
        GET /compras/{id}: Muestra el detalle completo de una compra, sus entradas, servicios asociados y datos del QR.
        """
        pass

    @app.route("/compras/<int:id>/cancelar", methods=["PUT"])
    def put_cancelar_compra(id):
        """
        PUT /compras/{id}/cancelar: Cancela una compra, la registra y libera las butacas,
        validando estar dentro del tiempo límite previo a la función.
        """
        pass
