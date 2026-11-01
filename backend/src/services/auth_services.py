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
    pass


def autenticar_usuario(datos: dict) -> dict:
    """
    Verifica credenciales contra el hash de contraseña y retorna datos de sesión.
    """
    pass


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
