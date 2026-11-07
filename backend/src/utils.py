import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal, InvalidOperation
#import para validaciones genericas de datos de entrada. 

from src.constants import ROL_ADMINISTRADOR
from src.repositories.usuarios_repository import buscar_usuario_por_id_db

ZONA_HORARIA_LOCAL = ZoneInfo("America/Argentina/Buenos_Aires")
def construir_error_api(
    code: str, message: str, description: str, level: str = "error"
) -> dict:
    """Construye un payload de error estándar compatible con la API."""
    return {
        "errors": [
            {
                "code": code,
                "message": message,
                "level": level,
                "description": description,
            }
        ]
    }


def construir_links_hateoas(
    base_url: str,
    query_params: dict,
    limit: int,
    offset: int,
    total_registros: int,
) -> dict:
    """Construye los enlaces HATEOAS (_first, _prev, _next, _last)."""
    params_base = {
        k: v for k, v in query_params.items() if k not in ("_limit", "_offset")
    }

    def _crear_url(l, o):
        qp = params_base.copy()
        qp["_limit"] = l
        qp["_offset"] = o
        return f"{base_url}?{urllib.parse.urlencode(qp)}"

    ultimo_offset = (
        max(0, ((total_registros - 1) // limit) * limit)
        if total_registros > 0
        else 0
    )
    prev_offset = max(0, offset - limit)
    next_offset = min(ultimo_offset, offset + limit)

    return {
        "_first": {"href": _crear_url(limit, 0)},
        "_prev": {"href": _crear_url(limit, prev_offset)},
        "_next": {"href": _crear_url(limit, next_offset)},
        "_last": {"href": _crear_url(limit, ultimo_offset)},
    }

import re
import smtplib
from email.message import EmailMessage
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.constants import PATRON_EMAIL
from src.config import obtener_config_email


def es_entero_positivo(valor) -> bool:
    return type(valor) is int and valor > 0


def es_email_valido(valor) -> bool:
    return isinstance(valor, str) and len(valor) <= 255 and bool(
        re.fullmatch(PATRON_EMAIL, valor.strip())
    )


def error_de_negocio(codigo: str, mensaje: str, descripcion: str, estado: int):
    raise ValueError(construir_error_api(codigo, mensaje, descripcion), estado)


def renderizar_correo_html(plantilla: str, contexto: dict) -> str:
    """Plantillas confiables del proyecto, no nombres aportados por el usuario HTTP."""
    if plantilla not in ("compra_confirmada", "comprobante_provisorio"):
        raise ValueError("Plantilla de correo no admitida")
    carpeta = Path(__file__).resolve().parent / "templates" / "emails"
    entorno = Environment(
        loader=FileSystemLoader(str(carpeta)),
        autoescape=select_autoescape(["html"]),
    )
    return entorno.get_template(plantilla + ".html").render(**contexto)


def enviar_correo_html(
    destinatario: str,
    asunto: str,
    plantilla: str,
    contexto: dict,
    imagenes_inline: dict | None = None,
) -> str:
    """Envía cualquier plantilla admitida, con imágenes CID opcionales.

    EMAIL_MODE=console no envía correo: sirve exclusivamente para pruebas.
    """
    if not es_email_valido(destinatario):
        raise ValueError("Destinatario inválido")
    html = renderizar_correo_html(plantilla, contexto)
    configuracion = obtener_config_email()
    if configuracion["modo"] == "console":
        return "SIMULADO"
    if configuracion["modo"] != "smtp":
        raise RuntimeError("EMAIL_MODE debe ser 'console' o 'smtp'")

    host = configuracion["host"]
    remitente = configuracion["remitente"]
    puerto = configuracion["puerto"]
    if not host or not es_email_valido(remitente):
        raise RuntimeError("Configuración SMTP incompleta")

    mensaje = EmailMessage()
    mensaje["To"] = destinatario
    mensaje["From"] = remitente
    mensaje["Subject"] = asunto
    mensaje.set_content("Cine Paradiso: consultá la versión HTML de este correo.")
    mensaje.add_alternative(html, subtype="html")
    parte_html = mensaje.get_payload()[-1]
    for identificador, png in (imagenes_inline or {}).items():
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", identificador):
            raise ValueError("Identificador de imagen inválido")
        parte_html.add_related(
            png, maintype="image", subtype="png", cid=f"<{identificador}>"
        )

    with smtplib.SMTP(host, puerto, timeout=15) as servidor:
        if configuracion["starttls"]:
            servidor.starttls()
        usuario = configuracion["usuario"]
        clave = configuracion["password"]
        if usuario:
            servidor.login(usuario, clave)
        servidor.send_message(mensaje)
    return "ENVIADO"

#Evito tener funciones sueltas en [los validators y repository de [Peliculas]. Como son genéricas y se repiten, las dejó en utils
# ==========================================
# Errores de negocio (ValueError con payload estándar y código HTTP)
# ==========================================
def crear_error_http(codigo: str, mensaje: str, descripcion: str, estado: int) -> ValueError:
    """Arma el ValueError que app.py convierte en respuesta JSON con ese código HTTP."""
    return ValueError(construir_error_api(codigo, mensaje, descripcion), estado)


def error_validacion(descripcion: str) -> ValueError:
    """Error 400 estándar de validación de datos de entrada."""
    return crear_error_http(
        "error.validacion.parametro", "Dato inválido", descripcion, 400
    )


def error_no_encontrado(descripcion: str) -> ValueError:
    """Error 404 estándar para un recurso inexistente."""
    return crear_error_http(
        "error.recurso.no_encontrado", "Recurso no encontrado", descripcion, 404
    )


def error_conflicto(descripcion: str) -> ValueError:
    """Error 409 estándar para conflictos de estado u horario."""
    return crear_error_http(
        "error.recurso.conflicto", "Conflicto", descripcion, 409
    )


# ==========================================
# Autenticación y autorización
# ==========================================
def validar_usuario(encabezado: str | None) -> dict:
    """
    Exige un usuario autenticado y activo, de cualquier rol. Pensada para reutilizarse
    en cualquier endpoint que pida BearerAuth (ver swagger: respuesta 401).

    Uso en una ruta, antes de validar el cuerpo o los parámetros:
        usuario = validar_usuario(request.headers.get("Authorization"))

    - Header ausente/mal formado, token inválido o vencido, o usuario inexistente/inactivo: 401.
    - Si todo está bien devuelve el usuario (id_usuario, nombre, email, rol, ...).

    Lanza ValueError con el payload estándar y el código HTTP; app.py lo convierte en JSON.
    """
    # Import local: auth_validators ya importa utils, y un import arriba sería circular.
    from src.validators.auth_validators import validar_autorizacion

    autorizacion = validar_autorizacion(encabezado)
    if "errors" in autorizacion:
        error = autorizacion["errors"][0]
        raise crear_error_http(
            error["code"], error["message"], error["description"], 401
        )

    usuario = buscar_usuario_por_id_db(autorizacion["usuario_id"])
    if not usuario or not usuario["activo"]:
        raise crear_error_http(
            "error.auth.token_invalido",
            "Token inválido",
            "El usuario asociado al token no existe o está inactivo.",
            401,
        )
    return usuario


def validar_admin(encabezado: str | None) -> dict:
    """
    Exige que la petición venga de un usuario ADMINISTRADOR. Pensada para reutilizarse
    en cualquier endpoint "Solo Admin" (ver swagger: respuestas 401 y 403).

    Uso en una ruta, antes de validar el cuerpo o los parámetros:
        admin = validar_admin(request.headers.get("Authorization"))

    - Mismos 401 que validar_usuario.
    - Usuario válido sin rol ADMINISTRADOR: 403.
    - Si todo está bien devuelve el usuario, por si la ruta necesita saber qué admin
      hizo la acción (ej. auditoría).

    Lanza ValueError con el payload estándar y el código HTTP; app.py lo convierte en JSON.
    """
    usuario = validar_usuario(encabezado)
    if usuario["rol"] != ROL_ADMINISTRADOR:
        raise crear_error_http(
            "error.auth.prohibido",
            "Acceso denegado",
            "El usuario no tiene rol ADMINISTRADOR para ejecutar esta acción.",
            403,
        )
    return usuario


# ==========================================
# Validaciones genéricas de datos de entrada
# ==========================================
def validar_objeto_json(datos) -> dict:
    """Lanza 400 si el cuerpo de la petición no es un objeto JSON."""
    if not isinstance(datos, dict):
        raise error_validacion("El cuerpo de la petición debe ser un objeto JSON.")
    return datos


def es_entero(valor) -> bool:
    """True si es un entero real (en JSON, true/false llegan como bool y no cuentan)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def validar_entero_positivo(valor, nombre: str) -> int:
    """Valida un entero positivo; acepta también texto numérico (query params)."""
    if isinstance(valor, str):
        valor = valor.strip()
        if valor.isascii() and valor.isdigit():
            valor = int(valor)
    if not es_entero(valor) or valor <= 0:
        raise error_validacion(f"El campo {nombre} debe ser un entero positivo.")
    return valor


def validar_entero_en_rango(valor, nombre: str, minimo: int, maximo: int) -> int:
    """Valida un entero dentro de un rango inclusivo."""
    if not es_entero(valor) or not minimo <= valor <= maximo:
        raise error_validacion(
            f"El campo {nombre} debe ser un entero entre {minimo} y {maximo}."
        )
    return valor


def validar_texto(valor, nombre: str, largo_max: int) -> str:
    """Valida un texto no vacío, sin espacios sobrantes y de hasta largo_max caracteres."""
    if not isinstance(valor, str):
        raise error_validacion(f"El campo {nombre} debe ser texto.")
    valor = valor.strip()
    if not valor:
        raise error_validacion(f"El campo {nombre} no puede estar vacío.")
    if len(valor) > largo_max:
        raise error_validacion(
            f"El campo {nombre} no puede superar los {largo_max} caracteres."
        )
    return valor


def validar_texto_opcional(valor, nombre: str, largo_max: int) -> str | None:
    """Como validar_texto, pero None o texto vacío devuelven None."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None
    return validar_texto(valor, nombre, largo_max)


def validar_booleano(valor, nombre: str) -> bool:
    """Valida que el valor sea true o false."""
    if not isinstance(valor, bool):
        raise error_validacion(f"El campo {nombre} debe ser true o false.")
    return valor


def validar_opcion(valor, opciones, nombre: str):
    """Valida que el valor pertenezca a un conjunto de opciones permitidas."""
    if valor not in opciones:
        opciones_legibles = ", ".join(sorted(opciones))
        raise error_validacion(
            f"El campo {nombre} debe ser uno de: {opciones_legibles}."
        )
    return valor


def validar_decimal_positivo(valor, nombre: str) -> Decimal:
    """Valida un número decimal positivo (acepta texto numérico de formularios/JSON)."""
    if isinstance(valor, bool) or not isinstance(
        valor, (int, float, str, Decimal)
    ):
        raise error_validacion(f"El campo {nombre} debe ser un número decimal positivo.")

    try:
        numero = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError):
        raise error_validacion(
            f"El campo {nombre} debe ser un número decimal positivo."
        ) from None

    if not numero.is_finite() or numero <= 0:
        raise error_validacion(f"El campo {nombre} debe ser un número decimal positivo.")
    return numero


def parsear_datetime(valor, nombre: str) -> datetime:
    """Parsea un DATETIME ISO 8601 y lo devuelve naive en la zona horaria local."""
    if not isinstance(valor, str) or not valor.strip():
        raise error_validacion(
            f"El campo {nombre} debe ser una fecha y hora ISO 8601."
        )

    try:
        fecha = datetime.fromisoformat(valor.strip().replace("Z", "+00:00"))
    except ValueError:
        raise error_validacion(
            f"El campo {nombre} debe ser una fecha y hora ISO 8601."
        ) from None

    if fecha.tzinfo is not None:
        fecha = fecha.astimezone(ZONA_HORARIA_LOCAL).replace(tzinfo=None)
    return fecha


# ==========================================
# Fechas y horas
# ==========================================
def ahora_local() -> datetime:
    """Hora actual en la zona local, sin tzinfo para comparar con columnas DATETIME."""
    return datetime.now(ZONA_HORARIA_LOCAL).replace(tzinfo=None)


def formatear_datetime_iso(valor: datetime) -> str:
    """Formatea un DATETIME como ISO 8601 sin zona (ej. 2026-11-15T20:00:00), según el swagger."""
    return valor.isoformat()


# ==========================================
# Formato de respuestas (contrato del swagger)
# ==========================================
def formatear_funcion(funcion: dict) -> dict:
    """Adapta una fila de funciones (datetime, Decimal, tinyint) al contrato del swagger."""
    return {
        **funcion,
        "inicio": formatear_datetime_iso(funcion["inicio"]),
        "fin": formatear_datetime_iso(funcion["fin"]),
        "precio_entrada": float(funcion["precio_entrada"]),
        "subtitulada": bool(funcion["subtitulada"]),
    }

