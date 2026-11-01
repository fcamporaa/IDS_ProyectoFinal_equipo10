from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import pymysql
from src.constants import JWT_ACCESS_TOKEN_MINUTES, JWT_SECRET_KEY
from src.repositories.usuarios_repository import (
    buscar_usuario_por_email_db,
    insertar_usuario_db,
    buscar_usuario_por_id_db,
    actualizar_usuario_db,
)
from src.utils import construir_error_api


def _crear_token_acceso(id_usuario: int) -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError("La variable JWT_SECRET_KEY no está configurada.")

    ahora = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(id_usuario),
            "iat": ahora,
            "exp": ahora + timedelta(minutes=JWT_ACCESS_TOKEN_MINUTES),
        },
        JWT_SECRET_KEY,
        algorithm="HS256",
    )


def registrar_usuario(datos: dict) -> dict:
    """
    Registra un nuevo cliente verificando que el email no esté en uso.
    Retorna los datos del usuario registrado sin datos sensibles.
    """
    if buscar_usuario_por_email_db(datos["email"]):
        return construir_error_api(
            "error.auth.email_existente",
            "Email ya registrado",
            "Ya existe un usuario registrado con ese email.",
        )

    usuario = {
        "nombre": datos["nombre"],
        "email": datos["email"],
        "numero_socio": datos.get("numero_socio"),
        "contrasena_hash": bcrypt.hashpw(
            datos["contrasena"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8"),
        "rol": "CLIENTE",
    }
    try:
        id_usuario = insertar_usuario_db(usuario)
    except pymysql.err.IntegrityError as error:
        if error.args and error.args[0] == 1062:
            return construir_error_api(
                "error.auth.email_existente",
                "Email ya registrado",
                "Ya existe un usuario registrado con ese email.",
            )
        raise

    return {
        "id_usuario": id_usuario,
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "numero_socio": usuario["numero_socio"],
        "rol": usuario["rol"],
    }


def autenticar_usuario(datos: dict) -> dict:
    """
    Verifica credenciales contra el hash de contraseña y retorna datos de sesión.
    """
    usuario = buscar_usuario_por_email_db(datos["email"])
    hash_guardado = usuario.get("contrasena_hash") if usuario else None
    credenciales_validas = False

    if usuario and usuario.get("activo") and isinstance(hash_guardado, str):
        try:
            credenciales_validas = bcrypt.checkpw(
                datos["contrasena"].encode("utf-8"),
                hash_guardado.encode("utf-8"),
            )
        except ValueError:
            credenciales_validas = False

    if not credenciales_validas:
        return construir_error_api(
            "error.auth.credenciales_invalidas",
            "Credenciales inválidas",
            "El email o la contraseña son incorrectos, o la cuenta no está activa.",
        )

    fecha_registro = usuario["fecha_registro"]
    return {
        "token": _crear_token_acceso(usuario["id_usuario"]),
        "usuario": {
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "email": usuario["email"],
            "numero_socio": usuario["numero_socio"],
            "rol": usuario["rol"],
            "fecha_registro": fecha_registro.isoformat()
            if hasattr(fecha_registro, "isoformat")
            else fecha_registro,
            "activo": bool(usuario["activo"]),
        },
    }


def obtener_perfil_usuario(id_usuario: int) -> dict:
    """
    Obtiene los datos del perfil del usuario logueado actualmente.
    """
    usuario = buscar_usuario_por_id_db(id_usuario)
    if not usuario:
        return construir_error_api(
            "error.auth.usuario_no_encontrado",
            "Usuario no encontrado",
            "No existe un usuario asociado al token de autenticación.",
        )

    if not usuario["activo"]:
        return construir_error_api(
            "error.auth.usuario_inactivo",
            "Usuario inactivo",
            "La cuenta asociada al token ya no está activa.",
        )

    fecha_registro = usuario["fecha_registro"]
    return {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "numero_socio": usuario["numero_socio"],
        "rol": usuario["rol"],
        "fecha_registro": fecha_registro.isoformat()
        if hasattr(fecha_registro, "isoformat")
        else fecha_registro,
        "activo": bool(usuario["activo"]),
    }


def actualizar_perfil_usuario(id_usuario: int, datos: dict) -> None:
    """
    Actualiza datos de perfil o contraseña del usuario logueado.
    """
    datos_actualizados = {}
    if "nombre" in datos:
        datos_actualizados["nombre"] = datos["nombre"]
    if "contrasena" in datos:
        datos_actualizados["contrasena_hash"] = bcrypt.hashpw(
            datos["contrasena"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    actualizar_usuario_db(id_usuario, datos_actualizados)


def actualizar_perfil_autenticado(id_usuario: int, datos: dict) -> dict:
    """Verifica el estado de la cuenta y actualiza el perfil autenticado."""
    perfil = obtener_perfil_usuario(id_usuario)
    if "errors" in perfil:
        return perfil

    actualizar_perfil_usuario(id_usuario, datos)
    return {"mensaje": "Perfil actualizado correctamente."}
