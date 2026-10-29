from flask import jsonify, request
from src.services.funciones_services import (
    listar_funciones,
    crear_funcion,
    actualizar_funcion,
    eliminar_funcion,
    obtener_mapa_butacas_funcion,
)
from src.validators.funciones_validators import (
    validar_id_funcion,
    validar_filtros_funciones,
    validar_crear_funcion,
    validar_actualizar_funcion,
)


def register_funciones_routes(app):

    @app.route("/funciones", methods=["GET"])
    def get_funciones():
        """
        GET /funciones: Lista las funciones programadas.
        """
        pass

    @app.route("/funciones", methods=["POST"])
    def post_funcion():
        """
        POST /funciones: Programa una nueva función validando que esté disponible el horario en la misma sala (Solo Admin).
        """
        pass

    @app.route("/funciones/<int:id>", methods=["PUT"])
    def put_funcion(id):
        """
        PUT /funciones/{id}: Modifica el horario, precio o estado de una función programada (Solo Admin).
        """
        pass

    @app.route("/funciones/<int:id>", methods=["DELETE"])
    def delete_funcion(id):
        """
        DELETE /funciones/{id}: Cancela o da de baja una función programada sin entradas activas (Solo Admin).
        """
        pass

    @app.route("/funciones/<int:id>/butacas", methods=["GET"])
    def get_butacas_funcion(id):
        """
        GET /funciones/{id}/butacas: Devuelve el mapa de butacas de la sala indicando cuáles están libres y cuáles ocupadas para esa función.
        """
        pass
