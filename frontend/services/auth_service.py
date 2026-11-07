from services.api_client import consultar_backend


def iniciar_sesion(email: str, contrasena: str):
    """
    Envía las credenciales al endpoint POST /auth/login del backend.
    Retorna una tupla (datos_respuesta, codigo_http).
    """
    return consultar_backend(
        ruta="/auth/login",
        metodo="POST",
        datos={"email": email, "contrasena": contrasena},
    )


def obtener_perfil(token: str):
    """Obtiene el perfil del usuario autenticado para validar su rol."""
    return consultar_backend("/auth/me", token=token, metodo="GET")
