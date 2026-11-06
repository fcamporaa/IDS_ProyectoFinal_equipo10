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
        # Obtenemos los filtros que puedan venir en la URL (ej: ?idioma=ES)
        filtros = request.args.to_dict()
            # Llamamos al servicio
        funciones = listar_funciones(filtros)
        return jsonify(funciones), 200

    @app.route("/funciones", methods=["POST"])
    def post_funcion():
        """
        POST /funciones: Programa una nueva función validando que esté disponible el horario en la misma sala (Solo Admin).
        """
        try:
            datos = request.json
            # Pasamos el JSON crudo del Swagger directo al servicio
            crear_funcion(datos)
        
            # Retornamos exactamente lo que pide el Swagger: código 201 y mensaje
            return jsonify({"mensaje": "Función programada exitosamente"}), 201
        except ValueError as e:
            return jsonify({"mensaje":"Conflicto - la sala ya se encuentra ocupada en ese horario"}), 409
        except Exception as e:
            
            # Si es otro error de código o base de datos, mandamos un 500
            return jsonify({"mensaje":"error interno"}), 500   
            raise e

        
        
    @app.route("/funciones/<int:id>", methods=["PUT"])
    def put_funcion(id):
        """
        PUT /funciones/{id}: Modifica el horario, precio o estado de una función programada (Solo Admin).
        """
        try:
            datos = request.json
            actualizar_funcion(id, datos)
            # 204 No Content es el estándar cuando se actualiza bien y no se devuelve nada
            return "", 204
        except Exception as e:
            return jsonify({"error": "Error interno"}), 500

    @app.route("/funciones/<int:id>", methods=["DELETE"])
    def delete_funcion(id):
        """
        DELETE /funciones/{id}: Cancela o da de baja una función programada sin entradas activas (Solo Admin).
        """
        try:
            eliminar_funcion(id)
            return "", 204
        except Exception as e:
           
            return jsonify({"error": "Error interno"}), 500

    @app.route("/funciones/<int:id>/butacas", methods=["GET"])
    def get_butacas_funcion(id):
        """
        GET /funciones/{id}/butacas: Devuelve el mapa de butacas de la sala indicando cuáles están libres y cuáles ocupadas para esa función.
        """
        respuesta = obtener_mapa_butacas_funcion(id)    
        return jsonify(respuesta), 200
