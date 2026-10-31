import re

import jwt
from src.constants import JWT_SECRET_KEY, PATRON_EMAIL
from src.utils import construir_error_api


def validar_token_acceso(token: str) -> int | None:
    """Valida el token JWT recibido en el encabezado Authorization."""
    if not isinstance(token, str) or not token.strip():
        return None

    if not JWT_SECRET_KEY:
        raise RuntimeError("La variable JWT_SECRET_KEY no está configurada.")

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
            options={"require": ["sub", "iat", "exp"]},
        )
        id_usuario = int(payload["sub"])
        return id_usuario if id_usuario > 0 else None
    except (jwt.InvalidTokenError, TypeError, ValueError):
        return None


def validar_registro_usuario(datos: dict) -> dict:
    """
    Valida datos obligatorios para el registro de cliente:
    - nombre: str no vacío
    - email: formato de email válido
    - contrasena: str longitud mínima
    """
    if not isinstance(datos, dict):
        return construir_error_api(
            "error.validacion.cuerpo",
            "Cuerpo de solicitud inválido",
            "Se esperaba un objeto JSON con los datos del registro.",
        )

    campos_permitidos = {"nombre", "email", "contrasena", "numero_socio"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        return construir_error_api(
            "error.validacion.campo_no_permitido",
            "Campo no permitido",
            f"Los campos no están permitidos: {', '.join(sorted(campos_desconocidos))}.",
        )

    nombre = datos.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip() or len(nombre.strip()) > 120:
        return construir_error_api(
            "error.validacion.nombre",
            "Nombre inválido",
            "El nombre es obligatorio y debe tener entre 1 y 120 caracteres.",
        )

    email = datos.get("email")
    if (
        not isinstance(email, str)
        or len(email.strip()) > 255
        or not re.fullmatch(PATRON_EMAIL, email.strip())
    ):
        return construir_error_api(
            "error.validacion.email",
            "Email inválido",
            "Se requiere un email válido de hasta 255 caracteres.",
        )

    contrasena = datos.get("contrasena")
    if not isinstance(contrasena, str):
        return construir_error_api(
            "error.validacion.contrasena",
            "Contraseña inválida",
            "La contraseña debe ser texto de al menos 8 caracteres, con mayúscula, minúscula y número.",
        )
    if (
        len(contrasena) < 8
        or len(contrasena.encode("utf-8")) > 72
        or not re.search(r"[a-z]", contrasena)
        or not re.search(r"[A-Z]", contrasena)
        or not re.search(r"[0-9]", contrasena)
    ):
        return construir_error_api(
            "error.validacion.contrasena",
            "Contraseña inválida",
            "La contraseña debe tener al menos 8 caracteres, incluir mayúscula, minúscula y número, y no superar 72 bytes en UTF-8.",
        )

    numero_socio = datos.get("numero_socio")
    if numero_socio is not None:
        if not isinstance(numero_socio, str) or len(numero_socio.strip()) > 30:
            return construir_error_api(
                "error.validacion.numero_socio",
                "Número de socio inválido",
                "El número de socio debe ser texto de hasta 30 caracteres.",
            )
        numero_socio = numero_socio.strip() or None

    return {
        "nombre": nombre.strip(),
        "email": email.strip().lower(),
        "contrasena": contrasena,
        "numero_socio": numero_socio,
    }


def validar_login_usuario(datos: dict) -> dict:
    """
    Valida credenciales para inicio de sesión:
    - email: formato de email válido
    - contrasena: str no vacía
    """
    if not isinstance(datos, dict):
        return construir_error_api(
            "error.validacion.cuerpo",
            "Cuerpo de solicitud inválido",
            "Se esperaba un objeto JSON con email y contraseña.",
        )

    campos_permitidos = {"email", "contrasena"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        return construir_error_api(
            "error.validacion.campo_no_permitido",
            "Campo no permitido",
            f"Los campos no están permitidos: {', '.join(sorted(campos_desconocidos))}.",
        )

    email = datos.get("email")
    if (
        not isinstance(email, str)
        or len(email.strip()) > 255
        or not re.fullmatch(PATRON_EMAIL, email.strip())
    ):
        return construir_error_api(
            "error.validacion.email",
            "Email inválido",
            "Se requiere un email válido de hasta 255 caracteres.",
        )

    contrasena = datos.get("contrasena")
    if not isinstance(contrasena, str) or not contrasena.strip():
        return construir_error_api(
            "error.validacion.contrasena",
            "Contraseña inválida",
            "La contraseña es obligatoria y debe ser texto no vacío.",
        )

    return {"email": email.strip().lower(), "contrasena": contrasena}


def validar_actualizacion_perfil(datos: dict) -> dict:
    """
    Valida campos permitidos para actualización de perfil:
    - nombre (opcional)
    - contrasena (opcional)
    """
    if not isinstance(datos, dict):
        return construir_error_api(
            "error.validacion.cuerpo",
            "Cuerpo de solicitud inválido",
            "Se esperaba un objeto JSON con nombre o contraseña.",
        )

    campos_permitidos = {"nombre", "contrasena"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        return construir_error_api(
            "error.validacion.campo_no_permitido",
            "Campo no permitido",
            f"Los campos no están permitidos: {', '.join(sorted(campos_desconocidos))}.",
        )

    if not datos:
        return construir_error_api(
            "error.validacion.perfil_vacio",
            "Datos de perfil requeridos",
            "Debe proporcionar al menos nombre o contraseña para actualizar el perfil.",
        )

    datos_validados = {}
    if "nombre" in datos:
        nombre = datos["nombre"]
        if not isinstance(nombre, str) or not nombre.strip() or len(nombre.strip()) > 120:
            return construir_error_api(
                "error.validacion.nombre",
                "Nombre inválido",
                "El nombre debe tener entre 1 y 120 caracteres.",
            )
        datos_validados["nombre"] = nombre.strip()

    if "contrasena" in datos:
        contrasena = datos["contrasena"]
        if (
            not isinstance(contrasena, str)
            or len(contrasena) < 8
            or len(contrasena.encode("utf-8")) > 72
            or not re.search(r"[a-z]", contrasena)
            or not re.search(r"[A-Z]", contrasena)
            or not re.search(r"[0-9]", contrasena)
        ):
            return construir_error_api(
                "error.validacion.contrasena",
                "Contraseña inválida",
                "La contraseña debe tener al menos 8 caracteres, incluir mayúscula, minúscula y número, y no superar 72 bytes en UTF-8.",
            )
        datos_validados["contrasena"] = contrasena

    return datos_validados
