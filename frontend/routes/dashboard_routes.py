from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.dashboard_service import (
    obtener_estadisticas_cancelaciones,
    obtener_franjas_horarias,
    obtener_locales,
    obtener_metricas_ocupacion,
    obtener_ventas_por_genero,
)
from utils.auth import admin_required
from utils.filtros import validar_filtros_dashboard

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/admin")


def _agregar_porcentaje_visual(filas: list[dict], clave: str) -> list[dict]:
    """Calcula el ancho relativo de la barra respecto del mayor valor del reporte."""
    maximo = max((fila.get(clave, 0) for fila in filas), default=0)
    for fila in filas:
        fila["porcentaje_visual"] = (
            round(fila.get(clave, 0) * 100.0 / maximo, 2) if maximo else 0.0
        )
    return filas


def _limpiar_sesion() -> None:
    session.pop("access_token", None)
    session.pop("usuario", None)


@dashboard_bp.route("/dashboard")
@admin_required
def index():
    try:
        filtros = validar_filtros_dashboard(request.args)
    except ValueError as error:
        flash(str(error), "error")
        filtros = {}

    token = session["access_token"]
    consultas = (
        ("ocupacion", obtener_metricas_ocupacion, []),
        ("ventas_genero", obtener_ventas_por_genero, []),
        ("franjas", obtener_franjas_horarias, []),
        ("cancelaciones", obtener_estadisticas_cancelaciones, {}),
    )
    respuestas = {}
    error_backend = None

    for clave, consultar, valor_vacio in consultas:
        datos, estado = consultar(token, filtros)
        if estado in (401, 403):
            _limpiar_sesion()
            flash("La sesión expiró. Volvé a iniciar sesión.", "error")
            return redirect(url_for("home.index"))
        if estado != 200 or not isinstance(datos, type(valor_vacio)):
            error_backend = "No se pudieron cargar todos los reportes del dashboard."
            datos = valor_vacio
        respuestas[clave] = datos

    locales, estado_locales = obtener_locales(token)
    if estado_locales != 200:
        locales = []
        error_backend = error_backend or "No se pudo cargar el listado de complejos."

    ocupacion = respuestas["ocupacion"]
    ventas_genero = _agregar_porcentaje_visual(
        respuestas["ventas_genero"], "entradas_vendidas"
    )
    franjas = _agregar_porcentaje_visual(
        respuestas["franjas"], "entradas_vendidas"
    )
    cancelaciones = respuestas["cancelaciones"]

    total_capacidad = sum(int(fila.get("capacidad_total") or 0) for fila in ocupacion)
    total_ocupadas = sum(int(fila.get("entradas_vendidas") or 0) for fila in ocupacion)
    entradas_vendidas = sum(
        int(fila.get("entradas_vendidas") or 0) for fila in franjas
    )
    recaudacion_total = sum(
        float(fila.get("total_recaudado") or 0) for fila in franjas
    )
    kpis = {
        "ocupacion_promedio": (
            round(total_ocupadas * 100.0 / total_capacidad, 2)
            if total_capacidad
            else 0.0
        ),
        "entradas_vendidas": entradas_vendidas,
        "recaudacion_total": round(recaudacion_total, 2),
        "tasa_cancelacion": cancelaciones.get("tasa_cancelacion_porcentaje", 0.0),
    }

    return render_template(
        "backoffice/dashboard.html",
        ocupacion=ocupacion,
        ventas_genero=ventas_genero,
        franjas=franjas,
        cancelaciones=cancelaciones,
        kpis=kpis,
        filtros=filtros,
        locales=locales if isinstance(locales, list) else [],
        error_backend=error_backend,
    )
