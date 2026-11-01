from flask import jsonify, request

from src.constants import HTTP_CREATED, HTTP_OK
from src.services.funciones_services import (
    actualizar_funcion,
    crear_funcion,
    eliminar_funcion,
    listar_funciones,
    obtener_mapa_butacas_funcion,
)
from src.validators.funciones_validators import (
    validar_actualizar_funcion,
    validar_crear_funcion,
    validar_filtros_funciones,
    validar_id_funcion,
)


def register_funciones_routes(app):

    @app.route("/funciones", methods=["GET"])
    def get_funciones():
        """
        GET /funciones: Lista las funciones programadas.
        """
        filtros = validar_filtros_funciones(request.args)
        return jsonify(listar_funciones(filtros)), HTTP_OK

    @app.route("/funciones", methods=["POST"])
    def post_funcion():
        """
        POST /funciones: Programa una nueva función validando que esté disponible el horario en la misma sala (Solo Admin).
        """
        datos = validar_crear_funcion(request.get_json(silent=True))
        return jsonify(crear_funcion(datos)), HTTP_CREATED

    @app.route("/funciones/<int:id>", methods=["PUT"])
    def put_funcion(id):
        """
        PUT /funciones/{id}: Modifica el horario, precio o estado de una función programada (Solo Admin).
        """
        id_funcion = validar_id_funcion(id)
        cambios = validar_actualizar_funcion(request.get_json(silent=True))
        return jsonify(actualizar_funcion(id_funcion, cambios)), HTTP_OK

    @app.route("/funciones/<int:id>", methods=["DELETE"])
    def delete_funcion(id):
        """
        DELETE /funciones/{id}: Cancela o da de baja una función programada sin entradas activas (Solo Admin).
        """
        return jsonify(eliminar_funcion(validar_id_funcion(id))), HTTP_OK

    @app.route("/funciones/<int:id>/butacas", methods=["GET"])
    def get_butacas_funcion(id):
        """
        GET /funciones/{id}/butacas: Devuelve el mapa de butacas de la sala indicando cuáles están libres y cuáles ocupadas para esa función.
        """
        return jsonify(obtener_mapa_butacas_funcion(validar_id_funcion(id))), HTTP_OK
