from flask import jsonify, request
from src.services.auth_services import (
    registrar_usuario,
    autenticar_usuario,
    obtener_perfil_usuario,
    actualizar_perfil_usuario,
)
from src.validators.auth_validators import (
    validar_registro_usuario,
    validar_login_usuario,
    validar_actualizacion_perfil,
)


def register_auth_routes(app):

    @app.route("/auth/register", methods=["POST"])
    def register():
        """
        POST /auth/register: Registra a un nuevo cliente.
        """
        datos = request.get_json(silent=True)
        datos_validados = validar_registro_usuario(datos)
        if "errors" in datos_validados:
            return jsonify(datos_validados), 400

        resultado = registrar_usuario(datos_validados)
        if "errors" in resultado:
            return jsonify(resultado), 409

        return jsonify(resultado), 201

    @app.route("/auth/login", methods=["POST"])
    def login():
        """
        POST /auth/login: Autentica a un usuario (Cliente o Admin) y devuelve sus datos de sesión.
        """
        datos = request.get_json(silent=True)
        datos_validados = validar_login_usuario(datos)
        if "errors" in datos_validados:
            return jsonify(datos_validados), 400

        resultado = autenticar_usuario(datos_validados)
        if "errors" in resultado:
            return jsonify(resultado), 401

        return jsonify(resultado), 200

    @app.route("/auth/me", methods=["GET"])
    def get_profile():
        """
        GET /auth/me: Devuelve los datos del perfil del usuario logueado actualmente.
        """
        # usuario_id = ... (obtener de token / sesión)
        # perfil = obtener_perfil_usuario(usuario_id)
        # return jsonify(perfil), 200
        pass

    @app.route("/auth/me", methods=["PUT"])
    def update_profile():
        """
        PUT /auth/me: Permite al usuario logueado actualizar sus datos personales o contraseña.
        """
        # usuario_id = ... (obtener de token / sesión)
        # datos = request.get_json(silent=True)
        # datos_validados = validar_actualizacion_perfil(datos)
        # actualizar_perfil_usuario(usuario_id, datos_validados)
        # return "", 204
        pass
