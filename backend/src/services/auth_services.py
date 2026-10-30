import bcrypt
import pymysql
from src.repositories.usuarios_repository import (
    buscar_usuario_por_email_db,
    insertar_usuario_db,
    buscar_usuario_por_id_db,
    actualizar_usuario_db,
)
from src.utils import construir_error_api


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

    return {
        "usuario": {
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "email": usuario["email"],
            "numero_socio": usuario["numero_socio"],
            "rol": usuario["rol"],
        }
    }


def obtener_perfil_usuario(id_usuario: int) -> dict:
    """
    Obtiene los datos del perfil del usuario logueado actualmente.
    """
    pass


def actualizar_perfil_usuario(id_usuario: int, datos: dict) -> None:
    """
    Actualiza datos de perfil o contraseña del usuario logueado.
    """
    pass
