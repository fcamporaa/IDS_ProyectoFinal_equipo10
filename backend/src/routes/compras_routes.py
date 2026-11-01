from flask import Blueprint, jsonify, request
from src.constants import HTTP_OK, HTTP_CREADO, HTTP_NO_AUTORIZADO, HTTP_NO_ENCONTRADO
from src.utils import construir_error_api
from src.services.sesion_services import obtener_cliente_autenticado
from src.services.compras_services import (
    procesar_compra, obtener_detalle_compra, listar_mis_compras, reenviar_comprobante,
)
from src.validators.compras_validators import validar_id_compra, validar_datos_compra

compras_bp = Blueprint("compras", __name__)


def _cliente_actual():
    usuario = obtener_cliente_autenticado(request.headers.get("Authorization", ""))
    if not usuario:
        return None, (jsonify(construir_error_api(
            "auth.required", "No autorizado", "Se requiere una sesión de cliente válida."
        )), HTTP_NO_AUTORIZADO)
    return usuario, None


@compras_bp.route("/compras", methods=["POST"])
def post_compra():
    usuario, error = _cliente_actual()
    if error:
        return error
    datos = validar_datos_compra(request.get_json(silent=True))
    compra = procesar_compra(usuario["id_usuario"], datos)
    return jsonify(compra), HTTP_CREADO


@compras_bp.route("/compras/mis-compras", methods=["GET"])
def get_mis_compras():
    usuario, error = _cliente_actual()
    if error:
        return error
    return jsonify(listar_mis_compras(usuario["id_usuario"])), HTTP_OK


@compras_bp.route("/compras/<int:id>", methods=["GET"])
def get_compra(id):
    usuario, error = _cliente_actual()
    if error:
        return error
    compra = obtener_detalle_compra(validar_id_compra(id), usuario["id_usuario"])
    if not compra:
        return jsonify(construir_error_api("compras.no_existe", "No encontrada",
                                            "No existe esa compra para el usuario.")), HTTP_NO_ENCONTRADO
    return jsonify(compra), HTTP_OK


@compras_bp.route("/compras/<int:id>/reenviar-comprobante", methods=["POST"])
def post_reenviar_comprobante(id):
    usuario, error = _cliente_actual()
    if error:
        return error
    estado = reenviar_comprobante(validar_id_compra(id), usuario["id_usuario"])
    if estado is None:
        return jsonify(construir_error_api("compras.no_existe", "No encontrada",
                                            "No existe esa compra para el usuario.")), HTTP_NO_ENCONTRADO
    return jsonify({"mensaje": "Solicitud de envío procesada.", "email_estado": estado}), HTTP_OK


@compras_bp.route("/compras/<int:id>/cancelar", methods=["PUT"])
def put_cancelar_compra(id):
    return jsonify(construir_error_api("compras.pendiente", "No implementado",
                                        "La cancelación pertenece a US-10.")), 501
