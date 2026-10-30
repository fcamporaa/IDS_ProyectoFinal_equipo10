import re
from src.constants import PATRON_EMAIL
from src.utils import construir_error_api


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
    pass


def validar_actualizacion_perfil(datos: dict) -> dict:
    """
    Valida campos permitidos para actualización de perfil:
    - nombre (opcional)
    - contrasena (opcional)
    """
    pass
