from datetime import datetime
import re

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.dashboard_service import obtener_locales
from services.validaciones_service import (
    listar_validaciones_qr,
    obtener_salas_por_local,
    validar_ingreso_qr,
)
from utils.auth import admin_required
from utils.errores import extraer_mensaje_error
from utils.formatos import formatear_fecha_corta, formatear_hora
from utils.validaciones import validar_entero_positivo

validaciones_bp = Blueprint("validaciones", __name__, url_prefix="/admin")

RESULTADOS_VALIDOS = ("EXITO", "REUTILIZADO", "FALLIDO")
PATRON_QR_TOKEN = re.compile(r"^[A-Za-z0-9_-]{8,160}$")


def _redirigir_sesion_expirada():
    """Limpia la sesión local y redirige al login cuando el backend rechaza el token."""
    session.pop("access_token", None)
    session.pop("usuario", None)
    flash("La sesión expiró. Volvé a iniciar sesión.", "error")
    return redirect(url_for("auth.login"))


def _validar_qr_token_formulario(valor: str) -> str:
    """Valida el formato del token QR antes de consultar al backend."""
    token_limpio = (valor or "").strip()
    if not token_limpio or not PATRON_QR_TOKEN.fullmatch(token_limpio):
        raise ValueError(
            "El código QR debe tener entre 8 y 160 caracteres alfanuméricos, guiones o guiones bajos."
        )
    return token_limpio


def _validar_id_sala_opcional(valor: str) -> int | None:
    """Convierte el selector opcional de sala a entero positivo o None."""
    texto = (valor or "").strip()
    if not texto:
        return None
    return validar_entero_positivo(texto, "Sala")


def _validar_filtros_historial(args) -> dict:
    """Valida los filtros opcionales del historial de validaciones."""
    filtros = {}
    resultado = (args.get("resultado") or "").strip().upper()
    if resultado:
        if resultado not in RESULTADOS_VALIDOS:
            raise ValueError("El filtro de resultado debe ser EXITO, REUTILIZADO o FALLIDO.")
        filtros["resultado"] = resultado

    id_compra_raw = (args.get("id_compra") or "").strip()
    if id_compra_raw:
        filtros["id_compra"] = validar_entero_positivo(id_compra_raw, "ID de compra")

    return filtros


def _formatear_fecha_hora(valor_iso: str | None) -> str:
    """Convierte un timestamp ISO en texto legible para la tabla e indicador de resultado."""
    if not valor_iso:
        return "—"
    try:
        momento = datetime.fromisoformat(valor_iso)
    except ValueError:
        return valor_iso
    return f"{formatear_fecha_corta(momento.date())} · {formatear_hora(momento)}"


def _cargar_salas_activas(token: str) -> list[dict]:
    """Obtiene salas activas agrupadas con el nombre del complejo."""
    locales, estado_locales = obtener_locales(token)
    if estado_locales != 200 or not isinstance(locales, list):
        return []

    salas_disponibles = []
    for local in locales:
        id_local = local.get("id_local")
        if not id_local:
            continue
        salas, estado_salas = obtener_salas_por_local(token, id_local)
        if estado_salas != 200 or not isinstance(salas, list):
            continue
        for sala in salas:
            if sala.get("activa", True):
                salas_disponibles.append({
                    "id_sala": sala["id_sala"],
                    "etiqueta": f"{local.get('nombre', 'Complejo')} · Sala {sala.get('numero', sala['id_sala'])}",
                })
    return salas_disponibles


def _construir_resultado_ui(respuesta: dict, estado: int, qr_token: str) -> dict:
    """Normaliza la respuesta del backend para mostrar el cartel verde o rojo en pantalla."""
    if estado == 200 and isinstance(respuesta, dict):
        return {
            "autorizado": bool(respuesta.get("autorizado", True)),
            "resultado": respuesta.get("resultado", "EXITO"),
            "mensaje": respuesta.get("mensaje", "Ingreso autorizado. Compra validada con éxito."),
            "id_compra": respuesta.get("id_compra"),
            "pelicula": respuesta.get("pelicula") or "—",
            "entradas_validadas": respuesta.get("entradas_validadas", 0),
            "fecha_validacion": _formatear_fecha_hora(respuesta.get("fecha_validacion")),
            "qr_token": qr_token,
        }

    codigo_error = ""
    if isinstance(respuesta, dict):
        errores = respuesta.get("errors")
        if isinstance(errores, list) and errores and isinstance(errores[0], dict):
            codigo_error = errores[0].get("code", "")

    resultado_rechazo = "REUTILIZADO" if "reutilizado" in codigo_error else "FALLIDO"
    return {
        "autorizado": False,
        "resultado": resultado_rechazo,
        "mensaje": extraer_mensaje_error(respuesta, "El código QR no es válido para ingresar."),
        "id_compra": None,
        "pelicula": None,
        "entradas_validadas": 0,
        "fecha_validacion": None,
        "qr_token": qr_token,
    }


@validaciones_bp.route("/validador-qr", methods=["GET", "POST"])
@admin_required
def index():
    """Pantalla de recepción para escanear códigos QR y consultar el historial de puerta."""
    token = session["access_token"]

    if request.method == "POST":
        qr_raw = request.form.get("qr_token", "")
        id_sala_raw = request.form.get("id_sala", "")

        try:
            id_sala = _validar_id_sala_opcional(id_sala_raw)
            qr_token = _validar_qr_token_formulario(qr_raw)
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("validaciones.index", id_sala=id_sala_raw or None))

        respuesta, estado = validar_ingreso_qr(token, qr_token, id_sala=id_sala)
        if estado in (401, 403):
            return _redirigir_sesion_expirada()
        if estado >= 500:
            flash(extraer_mensaje_error(respuesta, "No se pudo validar el código QR."), "error")
            return redirect(url_for("validaciones.index", id_sala=id_sala or None))

        # PRG evita reenviar el mismo POST al recargar la página y provocar un falso REUTILIZADO.
        session["ultimo_resultado_qr"] = _construir_resultado_ui(respuesta, estado, qr_token)
        return redirect(url_for("validaciones.index", id_sala=id_sala or None))

    resultado_validacion = session.pop("ultimo_resultado_qr", None)

    try:
        filtros = _validar_filtros_historial(request.args)
    except ValueError as error:
        flash(str(error), "error")
        filtros = {}

    try:
        sala_seleccionada = _validar_id_sala_opcional(request.args.get("id_sala", ""))
    except ValueError:
        sala_seleccionada = None

    historial, estado_historial = listar_validaciones_qr(token, filtros)
    if estado_historial in (401, 403):
        return _redirigir_sesion_expirada()

    error_backend = None
    if estado_historial != 200 or not isinstance(historial, list):
        error_backend = extraer_mensaje_error(
            historial, "No se pudo cargar el historial de validaciones."
        )
        historial = []

    for item in historial:
        item["fecha_legible"] = _formatear_fecha_hora(item.get("fecha_validacion"))

    salas = _cargar_salas_activas(token)

    return render_template(
        "backoffice/validador_qr.html",
        resultado_validacion=resultado_validacion,
        historial=historial,
        filtros=filtros,
        salas=salas,
        sala_seleccionada=sala_seleccionada,
        resultados_disponibles=RESULTADOS_VALIDOS,
        error_backend=error_backend,
    )

