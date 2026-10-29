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
        """
        GET /peliculas/{id}/reseñas: Lista las puntuaciones y comentarios dejados por los espectadores en una película.
        """
        pass

    @app.route("/peliculas/<int:id>/resenas", methods=["POST"])
    def post_resena(id):
        """
        POST /peliculas/{id}/reseñas: Registra una puntuación y reseña, validando que el usuario tenga una compra
        para esa película con el QR efectivamente validado.
        """
        pass
