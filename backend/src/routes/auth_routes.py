from flask import jsonify, request
from src.services.auth_services import (
    registrar_usuario,
    autenticar_usuario,
    obtener_perfil_usuario,
    actualizar_perfil_autenticado,
)
from src.validators.auth_validators import (
    validar_registro_usuario,
    validar_login_usuario,
    validar_actualizacion_perfil,
    validar_autorizacion,
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
        autorizacion = validar_autorizacion(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify(autorizacion), 401

        perfil = obtener_perfil_usuario(autorizacion["usuario_id"])
        if "errors" in perfil:
            codigo_error = perfil["errors"][0]["code"]
            estado = 401 if codigo_error == "error.auth.usuario_inactivo" else 404
            return jsonify(perfil), estado

        return jsonify(perfil), 200

    @app.route("/auth/me", methods=["PUT"])
    def update_profile():
        """
        PUT /auth/me: Permite al usuario logueado actualizar sus datos personales o contraseña.
        """
        autorizacion = validar_autorizacion(request.headers.get("Authorization"))
        if "errors" in autorizacion:
            return jsonify(autorizacion), 401

        datos = request.get_json(silent=True)
        datos_validados = validar_actualizacion_perfil(datos)
        if "errors" in datos_validados:
            return jsonify(datos_validados), 400

        resultado = actualizar_perfil_autenticado(
            autorizacion["usuario_id"], datos_validados
        )
        if "errors" in resultado:
            codigo_error = resultado["errors"][0]["code"]
            estado = 401 if codigo_error == "error.auth.usuario_inactivo" else 404
            return jsonify(resultado), estado

        return jsonify(resultado), 200
