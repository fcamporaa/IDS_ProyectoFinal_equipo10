import secrets
from flask import session


def crear_token_csrf() -> str:
    token = secrets.token_urlsafe(32)
    session["csrf_compra"] = token
    return token


def validar_token_csrf(token: str) -> bool:
    esperado = session.pop("csrf_compra", None)
    return bool(esperado and token and secrets.compare_digest(esperado, token))
