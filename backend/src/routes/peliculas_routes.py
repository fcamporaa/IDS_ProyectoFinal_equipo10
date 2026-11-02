from flask import jsonify, request
from src.services.peliculas_services import (
    listar_cartelera,
    obtener_detalle_pelicula,
    crear_pelicula,
    actualizar_pelicula,
    eliminar_pelicula,
    buscar_peliculas_externas,
    listar_generos,
    listar_resenas_pelicula,
    crear_resena_pelicula,
)
from src.validators.peliculas_validators import (
    validar_id_pelicula,
    validar_filtros_cartelera,
    validar_crear_pelicula,
    validar_actualizar_pelicula,
    validar_busqueda_externa,
    validar_crear_resena,
)


def register_peliculas_routes(app):

    @app.route("/peliculas", methods=["GET"])
    def get_peliculas():
        """
        GET /peliculas: Lista la cartelera vigente.
        """
        pass

    @app.route("/peliculas/<int:id>", methods=["GET"])
    def get_pelicula(id):
        """
        GET /peliculas/{id}: Muestra el detalle de una película y sus funciones vigentes.
        """
        pass

    @app.route("/peliculas", methods=["POST"])
    def post_pelicula():
        """
        POST /peliculas: Guarda una película nueva en la base de datos local y asocia sus géneros (Solo Admin).
        """
        pass

    @app.route("/peliculas/<int:id>", methods=["PUT"])
    def put_pelicula(id):
        """
        PUT /peliculas/{id}: Modifica los datos de una película existente (Solo Admin).
        """
        pass

    @app.route("/peliculas/<int:id>", methods=["DELETE"])
    def delete_pelicula(id):
        """
        DELETE /peliculas/{id}: Da de baja una película de la cartelera (Solo Admin).
        """
        pass

    @app.route("/peliculas/externas/buscar", methods=["GET"])
    def search_peliculas_externas():
        """
        GET /peliculas/externas/buscar: Busca películas clásicas consultando la API externa (Solo Admin).
        """
        pass

    @app.route("/generos", methods=["GET"])
    def get_generos():
        """
        GET /generos: Lista todos los géneros cinematográficos disponibles.
        """
        pass

    @app.route("/peliculas/<int:id>/resenas", methods=["GET"])
    def get_resenas(id):
        try:
            reseñas = obtener_reseñas_por_pelicula(id)
            return jsonify(reseñas), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        pass

    @app.route("/peliculas/<int:id>/resenas", methods=["POST"])
    def post_resena(id):
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
        pass
