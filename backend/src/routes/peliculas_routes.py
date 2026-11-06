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
from src.utils import validar_admin, validar_usuario
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
        filtros = validar_filtros_cartelera(request.args)
        return jsonify(listar_cartelera(filtros)), 200

    @app.route("/peliculas/<int:id>", methods=["GET"])
    def get_pelicula(id):
        """
        GET /peliculas/{id}: Muestra el detalle de una película y sus funciones vigentes.
        """
        id_pelicula = validar_id_pelicula(id)
        return jsonify(obtener_detalle_pelicula(id_pelicula)), 200

    @app.route("/peliculas", methods=["POST"])
    def post_pelicula():
        """
        POST /peliculas: Guarda una película nueva en la base de datos local y asocia sus géneros (Solo Admin).
        """
        validar_admin(request.headers.get("Authorization"))
        datos = validar_crear_pelicula(request.get_json(silent=True))
        return jsonify(crear_pelicula(datos)), 201

    @app.route("/peliculas/<int:id>", methods=["PUT"])
    def put_pelicula(id):
        """
        PUT /peliculas/{id}: Modifica los datos de una película existente (Solo Admin).
        """
        validar_admin(request.headers.get("Authorization"))
        id_pelicula = validar_id_pelicula(id)
        datos = validar_actualizar_pelicula(request.get_json(silent=True))
        return jsonify(actualizar_pelicula(id_pelicula, datos)), 200

    @app.route("/peliculas/<int:id>", methods=["DELETE"])
    def delete_pelicula(id):
        """
        DELETE /peliculas/{id}: Da de baja una película de la cartelera (Solo Admin).
        """
        validar_admin(request.headers.get("Authorization"))
        id_pelicula = validar_id_pelicula(id)
        eliminar_pelicula(id_pelicula)
        return jsonify({"mensaje": "Película dada de baja con éxito."}), 200

    @app.route("/peliculas/externas/buscar", methods=["GET"])
    def search_peliculas_externas():
        """
        GET /peliculas/externas/buscar: Busca películas clásicas consultando la API externa (Solo Admin).
        """
        validar_admin(request.headers.get("Authorization"))
        filtros = validar_busqueda_externa(request.args)
        return jsonify(buscar_peliculas_externas(filtros)), 200

    @app.route("/generos", methods=["GET"])
    def get_generos():
        """
        GET /generos: Lista todos los géneros cinematográficos disponibles.
        """
        return jsonify(listar_generos()), 200

    @app.route("/peliculas/<int:id>/resenas", methods=["GET"])
    def get_resenas(id):
        """
        GET /peliculas/{id}/resenas: Lista las reseñas y puntuaciones de una película.
        """
        id_pelicula = validar_id_pelicula(id)
        return jsonify(listar_resenas_pelicula(id_pelicula)), 200

    @app.route("/peliculas/<int:id>/resenas", methods=["POST"])
    def post_resena(id):
        """
        POST /peliculas/{id}/resenas: Registra una puntuación (1 a 5) y comentario, solo para
        usuarios cuya compra de esa película tiene el QR validado (asistieron a la función).
        """
        usuario = validar_usuario(request.headers.get("Authorization"))
        id_pelicula = validar_id_pelicula(id)
        datos = validar_crear_resena(request.get_json(silent=True))
        return jsonify(crear_resena_pelicula(id_pelicula, usuario["id_usuario"], datos)), 201
