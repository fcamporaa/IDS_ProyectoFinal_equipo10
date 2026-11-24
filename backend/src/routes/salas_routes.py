from flask import jsonify, request

from src.constants import HTTP_CREADO, HTTP_OK
from src.services.salas_services import (
    listar_locales,
    listar_salas_por_local,
    listar_salas_admin,
    obtener_detalle_sala,
    crear_sala,
    generar_butacas_sala,
    actualizar_configuracion_sala,
)
from src.utils import validar_admin
from src.validators.salas_validators import (
    validar_id_local,
    validar_id_sala,
    validar_crear_sala,
    validar_generar_butacas,
    validar_actualizar_sala,
)


def register_salas_routes(app):

    @app.route("/locales", methods=["GET"])
    def get_locales():
        """
        GET /locales: Lista los complejos de cine disponibles.
        """
        locales = listar_locales()
        return jsonify(locales), HTTP_OK

    @app.route("/locales/<int:id>/salas", methods=["GET"])
    def get_salas_por_local(id):
        """
        GET /locales/{id}/salas: Lista todas las salas pertenecientes a un complejo específico y su capacidad.
        """
        id_local = validar_id_local(id)
        salas = listar_salas_por_local(id_local)
        return jsonify(salas), HTTP_OK

    @app.route("/locales/<int:id>/salas", methods=["POST"])
    def post_sala(id):
        """
        POST /locales/{id}/salas: Crea una sala con su grilla de butacas (Solo Admin).
        """
        validar_admin(request.headers.get("Authorization"))

        id_local = validar_id_local(id)
        datos = request.get_json(silent=True)
        datos_validados = validar_crear_sala(datos)
        sala = crear_sala(id_local, datos_validados)
        return jsonify(sala), HTTP_CREADO

    @app.route("/salas/admin", methods=["GET"])
    def get_salas_admin():
        """
        GET /salas/admin: Lista todas las salas activas e inactivas (Solo Admin).
        """
        validar_admin(request.headers.get("Authorization"))
        salas = listar_salas_admin()
        return jsonify(salas), HTTP_OK

    @app.route("/salas/<int:id>", methods=["GET"])
    def get_sala(id):
        """
        GET /salas/{id}: Obtiene el detalle de una sala y la distribución física de sus butacas.
        """
        id_sala = validar_id_sala(id)
        sala = obtener_detalle_sala(id_sala)
        return jsonify(sala), HTTP_OK

    @app.route("/salas/<int:id>/butacas", methods=["POST"])
    def post_butacas_sala(id):
        """
        POST /salas/{id}/butacas: Genera la grilla de butacas de una sala vacía (Solo Admin).
        """
        validar_admin(request.headers.get("Authorization"))

        id_sala = validar_id_sala(id)
        datos = request.get_json(silent=True)
        datos_validados = validar_generar_butacas(datos)
        sala = generar_butacas_sala(id_sala, datos_validados)
        return jsonify(sala), HTTP_CREADO

    @app.route("/salas/<int:id>", methods=["PUT"])
    def put_sala(id):
        """
        PUT /salas/{id}: Habilita/deshabilita una sala o actualiza su configuración (Solo Admin).
        """
        validar_admin(request.headers.get("Authorization"))

        id_sala = validar_id_sala(id)
        datos = request.get_json(silent=True)
        datos_validados = validar_actualizar_sala(datos)
        sala = actualizar_configuracion_sala(id_sala, datos_validados)
        return jsonify(sala), HTTP_OK
