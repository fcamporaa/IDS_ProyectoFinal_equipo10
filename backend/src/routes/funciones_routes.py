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

def registrar_rutas_deseables(app):

    @app.route("/peliculas/<int:id>/reseñas", methods=["GET"])
    def get_reseñas_pelicula(id):
        """
        GET /peliculas/{id}/reseñas: Lista las puntuaciones y comentarios dejados por los espectadores en una película[cite: 10].
        """
        try:
            reseñas = obtener_reseñas_por_pelicula(id)
            return jsonify(reseñas), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/peliculas/<int:id>/reseñas", methods=["POST"])
    def post_reseña_pelicula(id):
        """
        POST /peliculas/{id}/reseñas: Registra una puntuación y reseña, validando que el usuario tenga una compra para esa película con el QR efectivamente validado[cite: 10].
        """
        if 'usuario_id' not in session:
            return jsonify({"error": "No autorizado. Inicie sesión."}), 401
        
        usuario_id = session['usuario_id']
        data = request.get_json()
        puntuacion = data.get('puntuacion')
        comentario = data.get('comentario', '')

        if not puntuacion or not (1 <= int(puntuacion) <= 5):
            return jsonify({"error": "La puntuación es obligatoria y debe ser entre 1 y 5."}), 400

        asistio = verificar_asistencia_usuario(usuario_id, id)
        if not asistio:
            return jsonify({"error": "Acceso denegado. Solo los usuarios con asistencia validada pueden dejar reseñas."}), 403

        try:
            reseña_id = crear_reseña(id, usuario_id, puntuacion, comentario)
            return jsonify({"mensaje": "Reseña creada exitosamente", "id": reseña_id}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

