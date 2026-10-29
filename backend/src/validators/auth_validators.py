from src.utils import construir_error_api


def validar_registro_usuario(datos: dict) -> dict:
    """
    Valida datos obligatorios para el registro de cliente:
    - nombre: str no vacío
    - email: formato de email válido
    - contrasena: str longitud mínima
    """
    pass


def validar_login_usuario(datos: dict) -> dict:
    """
    Valida credenciales para inicio de sesión:
    - email: formato de email válido
    - contrasena: str no vacía
    """
    pass


def validar_actualizacion_perfil(datos: dict) -> dict:
    """
    Valida campos permitidos para actualización de perfil:
    - nombre (opcional)
    - contrasena (opcional)
    """
    pass
