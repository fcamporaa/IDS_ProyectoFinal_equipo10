from flask import jsonify, request
from src.services.salas_services import (
    listar_locales,
    listar_salas_por_local,
    obtener_detalle_sala,
    actualizar_configuracion_sala,
)
from src.validators.salas_validators import (
    validar_id_local,
    validar_id_sala,
    validar_actualizar_sala,
    validar_autorizacion_admin,
)


def register_salas_routes(app):

    @app.route("/locales", methods=["GET"])
    def get_locales():
        """
        GET /locales: Lista los complejos de cine disponibles.
        """
        locales = listar_locales()
        return jsonify(locales), 200

    @app.route("/locales/<int:id>/salas", methods=["GET"])
    def get_salas_por_local(id):
        """
        GET /locales/{id}/salas: Lista todas las salas pertenecientes a un complejo específico y su capacidad.
        """
        id_local = validar_id_local(id)
        salas = listar_salas_por_local(id_local)
        return jsonify(salas), 200

    @app.route("/salas/<int:id>", methods=["GET"])
    def get_sala(id):
        """
        GET /salas/{id}: Obtiene el detalle de una sala y la distribución física de sus butacas.
        """
        id_sala = validar_id_sala(id)
        sala = obtener_detalle_sala(id_sala)
        return jsonify(sala), 200

    @app.route("/salas/<int:id>", methods=["PUT"])
    def put_sala(id):
        """
        PUT /salas/{id}: Habilita/deshabilita una sala o actualiza su configuración (Solo Admin).
        """
        # Verificar permisos de administrador
        autorizacion = validar_autorizacion_admin(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify({"errors": autorizacion["errors"]}), autorizacion.get("status", 401)

        id_sala = validar_id_sala(id)
        datos = request.get_json(silent=True)
        datos_validados = validar_actualizar_sala(datos)
        sala = actualizar_configuracion_sala(id_sala, datos_validados)
        return jsonify(sala), 200



