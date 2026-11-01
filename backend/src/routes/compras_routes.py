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
from src.validators.auth_validators import validar_autorizacion
from src.services.auth_services import obtener_perfil_usuario
from src.utils import construir_error_api
from src.services.compras_services import reenviar_comprobante


def register_compras_routes(app):

    @app.route("/compras", methods=["POST"])
    def post_compra():
        """POST /compras: registra una compra de desarrollo y prepara su QR."""
        autorizacion = validar_autorizacion(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify(autorizacion), 401
        perfil = obtener_perfil_usuario(autorizacion["usuario_id"])
        if "errors" in perfil:
            return jsonify(perfil), 401
        if perfil["rol"] != "CLIENTE":
            return jsonify(construir_error_api(
                "error.auth.prohibido", "Acceso denegado", "Se requiere rol cliente."
            )), 403
        datos = validar_datos_compra(request.get_json(silent=True), perfil["email"])
        if "errors" in datos:
            return jsonify(datos), 400
        compra = procesar_compra(autorizacion["usuario_id"], datos)
        return jsonify(compra), 201

    @app.route("/compras/<int:id>/reenviar-comprobante", methods=["POST"])
    def post_reenviar_comprobante(id):
        """Reenvía un comprobante al dueño de una compra pagada."""
        id_compra = validar_id_compra(id)
        if isinstance(id_compra, dict):
            return jsonify(id_compra), 400
        autorizacion = validar_autorizacion(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify(autorizacion), 401
        perfil = obtener_perfil_usuario(autorizacion["usuario_id"])
        if "errors" in perfil:
            return jsonify(perfil), 401
        if perfil["rol"] != "CLIENTE":
            return jsonify(construir_error_api(
                "error.auth.prohibido", "Acceso denegado", "Se requiere rol cliente."
            )), 403
        estado = reenviar_comprobante(id_compra, autorizacion["usuario_id"])
        if estado is None:
            return jsonify(construir_error_api(
                "error.compras.no_encontrada", "Compra no encontrada", "No existe esa compra."
            )), 404
        return jsonify({"mensaje": "Solicitud procesada", "email_estado": estado}), 200

    @app.route("/compras/mis-compras", methods=["GET"])
    def get_mis_compras():
        """
        GET /compras/mis-compras: Devuelve el historial de compras del cliente logueado.
        """
        autorizacion = validar_autorizacion(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify(autorizacion), 401
        return jsonify(listar_mis_compras(autorizacion["usuario_id"])), 200

    @app.route("/compras/<int:id>", methods=["GET"])
    def get_compra(id):
        """
        GET /compras/{id}: Muestra el detalle completo de una compra, sus entradas, servicios asociados y datos del QR.
        """
        id_compra = validar_id_compra(id)
        if isinstance(id_compra, dict):
            return jsonify(id_compra), 400
        autorizacion = validar_autorizacion(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify(autorizacion), 401
        resultado = obtener_detalle_compra(id_compra, autorizacion["usuario_id"])
        if "errors" in resultado:
            codigo = resultado["errors"][0]["code"]
            estado = 403 if codigo == "error.auth.prohibido" else 404
            return jsonify(resultado), estado
        return jsonify(resultado), 200

    @app.route("/compras/<int:id>/cancelar", methods=["PUT"])
    def put_cancelar_compra(id):
        """
        PUT /compras/{id}/cancelar: Cancela una compra, la registra y libera las butacas,
        validando estar dentro del tiempo límite previo a la función.
        """
        id_compra = validar_id_compra(id)
        if isinstance(id_compra, dict):
            return jsonify(id_compra), 400
        autorizacion = validar_autorizacion(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify(autorizacion), 401
        resultado = cancelar_compra(id_compra, autorizacion["usuario_id"])
        if resultado and "errors" in resultado:
            codigo = resultado["errors"][0]["code"]
            if codigo == "error.auth.prohibido":
                estado = 403
            elif codigo == "error.compras.no_encontrada":
                estado = 404
            else:
                estado = 400
            return jsonify(resultado), estado
        return jsonify(
            {
                "mensaje": "Compra cancelada con éxito. Las butacas han sido liberadas.",
                "id_compra": id_compra,
                "estado": "CANCELADA",
            }
        ), 200
