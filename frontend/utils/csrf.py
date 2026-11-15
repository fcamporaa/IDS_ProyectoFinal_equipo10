import secrets
from flask import session


def crear_token_csrf() -> str:
    """Reutiliza el token de la sesión hasta que un formulario lo consuma."""
    token = session.get("csrf_compra")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_compra"] = token
    return token


def validar_token_csrf(token: str) -> bool:
    """Consume el token solamente si coincide con el de la sesión."""
    esperado = session.get("csrf_compra")
    if not esperado or not token or not secrets.compare_digest(esperado, token):
        return False
    session.pop("csrf_compra", None)
    return True
