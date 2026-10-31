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
    validar_token_acceso,
)
from src.utils import construir_error_api


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
        partes_autorizacion = request.headers.get("Authorization", "").split()
        if (
            len(partes_autorizacion) != 2
            or partes_autorizacion[0].lower() != "bearer"
        ):
            return jsonify(
                construir_error_api(
                    "error.auth.token_requerido",
                    "Autenticación requerida",
                    "Envía un token válido como Bearer en el encabezado Authorization.",
                )
            ), 401

        usuario_id = validar_token_acceso(partes_autorizacion[1])
        if usuario_id is None:
            return jsonify(
                construir_error_api(
                    "error.auth.token_invalido",
                    "Token inválido",
                    "El token es inválido o expiró.",
                )
            ), 401

        perfil = obtener_perfil_usuario(usuario_id)
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
        partes_autorizacion = request.headers.get("Authorization", "").split()
        if (
            len(partes_autorizacion) != 2
            or partes_autorizacion[0].lower() != "bearer"
        ):
            return jsonify(
                construir_error_api(
                    "error.auth.token_requerido",
                    "Autenticación requerida",
                    "Envía un token válido como Bearer en el encabezado Authorization.",
                )
            ), 401

        usuario_id = validar_token_acceso(partes_autorizacion[1])
        if usuario_id is None:
            return jsonify(
                construir_error_api(
                    "error.auth.token_invalido",
                    "Token inválido",
                    "El token es inválido o expiró.",
                )
            ), 401

        datos = request.get_json(silent=True)
        datos_validados = validar_actualizacion_perfil(datos)
        if "errors" in datos_validados:
            return jsonify(datos_validados), 400

        perfil = obtener_perfil_usuario(usuario_id)
        if "errors" in perfil:
            codigo_error = perfil["errors"][0]["code"]
            estado = 401 if codigo_error == "error.auth.usuario_inactivo" else 404
            return jsonify(perfil), estado

        actualizar_perfil_usuario(usuario_id, datos_validados)
        return jsonify({"mensaje": "Perfil actualizado correctamente."}), 200
