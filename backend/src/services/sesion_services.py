from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from src.repositories.compras_repository import obtener_usuario_para_compra_db
from src.config import obtener_auth_secret


def _firmador():
    return URLSafeTimedSerializer(obtener_auth_secret(), salt="cine-paradiso-auth-v1")


def emitir_token_sesion(id_usuario: int) -> str:
    """Punto de integración: US-02 debe emitirlo SOLO tras autenticar credenciales."""
    if type(id_usuario) is not int or id_usuario <= 0:
        raise ValueError("Usuario inválido")
    return _firmador().dumps({"id_usuario": id_usuario})


def obtener_cliente_autenticado(cabecera_autorizacion: str) -> dict | None:
    if not cabecera_autorizacion.startswith("Bearer "):
        return None
    try:
        carga = _firmador().loads(
            cabecera_autorizacion.removeprefix("Bearer ").strip(),
            max_age=8 * 3600,
        )
    except (BadSignature, SignatureExpired):
        return None
    if not isinstance(carga, dict) or type(carga.get("id_usuario")) is not int:
        return None
    usuario = obtener_usuario_para_compra_db(carga["id_usuario"])
    if not usuario or not usuario["activo"] or usuario["rol"] != "CLIENTE":
        return None
    return usuario
