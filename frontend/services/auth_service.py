from services.api_client import consultar_backend


def obtener_perfil(token: str):
    """Obtiene el perfil del usuario autenticado para validar su rol."""
    return consultar_backend("/auth/me", token)
