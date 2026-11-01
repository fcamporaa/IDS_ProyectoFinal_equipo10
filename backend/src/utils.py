import urllib.parse


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
