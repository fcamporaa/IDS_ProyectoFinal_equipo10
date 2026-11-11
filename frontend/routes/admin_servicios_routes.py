from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.admin_servicios_service import (
    actualizar_servicio,
    crear_servicio,
    dar_de_baja_servicio,
    listar_servicios_admin,
    reactivar_servicio,
)
from utils.auth import admin_required
from utils.errores import extraer_mensaje_error

admin_servicios_bp = Blueprint(
    "admin_servicios", __name__, url_prefix="/admin/servicios"
)

TIPOS_SERVICIO = ("COMIDA", "BEBIDA")


def _redirigir_sesion_expirada():
    """Limpia la sesión local y manda al login cuando el backend rechaza el token."""
    session.pop("access_token", None)
    session.pop("usuario", None)
    flash("La sesión expiró. Volvé a iniciar sesión.", "error")
    return redirect(url_for("auth.login"))


def _borrador_vacio() -> dict:
    """Borrador inicial del formulario de alta."""
    return {
        "nombre": "",
        "tipo": "COMIDA",
        "precio": "",
        "activo": True,
    }


def _leer_formulario(form) -> dict:
    """Lee el formulario de alta o edición."""
    nombre = (form.get("nombre") or "").strip()
    tipo = (form.get("tipo") or "COMIDA").strip()
    
    precio_raw = (form.get("precio") or "").strip()
    precio = None
    if precio_raw:
        try:
            precio = float(precio_raw)
        except ValueError:
            raise ValueError("El precio debe ser un número válido.") from None

    datos = {
        "nombre": nombre,
        "tipo": tipo,
        "precio": precio,
    }
    if "activo" in form:
        datos["activo"] = form.get("activo") == "on"

    return datos


def _renderizar_pagina(
    *,
    borrador: dict,
    abrir_formulario: bool,
    modo_formulario: str,
    accion_formulario: str,
    id_servicio_editando: int | None = None,
):
    """Centraliza la carga del listado y el render de la vista del ABM de servicios."""
    token = session.get("access_token")
    servicios, estado = listar_servicios_admin(token)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()

    error_backend = None
    if estado != 200 or not isinstance(servicios, list):
        flash("No se pudo cargar el listado de servicios.", "error")
        servicios = []
        error_backend = "No se pudo cargar el listado de servicios."

    return render_template(
        "backoffice/servicios.html",
        servicios=servicios,
        borrador=borrador,
        abrir_formulario=abrir_formulario,
        modo_formulario=modo_formulario,
        accion_formulario=accion_formulario,
        id_servicio_editando=id_servicio_editando,
        tipos_servicio=TIPOS_SERVICIO,
        error_backend=error_backend,
    )


@admin_servicios_bp.route("", methods=["GET"])
@admin_required
def index():
    """Lista el catálogo completo de servicios (activos e inactivos)."""
    return _renderizar_pagina(
        borrador=_borrador_vacio(),
        abrir_formulario=False,
        modo_formulario="crear",
        accion_formulario=url_for("admin_servicios.crear"),
    )


@admin_servicios_bp.route("", methods=["POST"])
@admin_required
def crear():
    """Crea un nuevo servicio."""
    token = session["access_token"]
    try:
        datos = _leer_formulario(request.form)
    except ValueError as e:
        flash(str(e), "error")
        return _renderizar_pagina(
            borrador=_borrador_vacio(),
            abrir_formulario=True,
            modo_formulario="crear",
            accion_formulario=url_for("admin_servicios.crear"),
        )

    respuesta, estado = crear_servicio(token, datos)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 201:
        flash("Servicio creado correctamente.", "success")
        return redirect(url_for("admin_servicios.index"))

    flash(extraer_mensaje_error(respuesta), "error")
    return _renderizar_pagina(
        borrador=datos,
        abrir_formulario=True,
        modo_formulario="crear",
        accion_formulario=url_for("admin_servicios.crear"),
    )


@admin_servicios_bp.route("/<int:id>/editar", methods=["GET"])
@admin_required
def editar(id):
    """Carga el formulario de edición con los datos del servicio."""
    token = session["access_token"]
    servicios, estado = listar_servicios_admin(token)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado != 200 or not isinstance(servicios, list):
        flash("No se pudo obtener el servicio.", "error")
        return redirect(url_for("admin_servicios.index"))

    servicio = next((s for s in servicios if s["id_servicio"] == id), None)
    if not servicio:
        flash("Servicio no encontrado.", "error")
        return redirect(url_for("admin_servicios.index"))

    borrador = {
        "nombre": servicio.get("nombre", ""),
        "tipo": servicio.get("tipo", "COMIDA"),
        "precio": servicio.get("precio", ""),
        "activo": servicio.get("activo", True),
    }

    return _renderizar_pagina(
        borrador=borrador,
        abrir_formulario=True,
        modo_formulario="editar",
        accion_formulario=url_for("admin_servicios.actualizar", id=id),
        id_servicio_editando=id,
    )


@admin_servicios_bp.route("/<int:id>/editar", methods=["POST"])
@admin_required
def actualizar(id):
    """Actualiza los datos de un servicio existente."""
    token = session["access_token"]
    try:
        datos = _leer_formulario(request.form)
    except ValueError as e:
        flash(str(e), "error")
        return _renderizar_pagina(
            borrador=_borrador_vacio(),
            abrir_formulario=True,
            modo_formulario="editar",
            accion_formulario=url_for("admin_servicios.actualizar", id=id),
            id_servicio_editando=id,
        )

    respuesta, estado = actualizar_servicio(token, id, datos)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 200:
        flash("Cambios guardados correctamente.", "success")
        return redirect(url_for("admin_servicios.index"))

    flash(extraer_mensaje_error(respuesta), "error")
    return _renderizar_pagina(
        borrador=datos,
        abrir_formulario=True,
        modo_formulario="editar",
        accion_formulario=url_for("admin_servicios.actualizar", id=id),
        id_servicio_editando=id,
    )


@admin_servicios_bp.route("/<int:id>/eliminar", methods=["POST"])
@admin_required
def eliminar(id):
    """Da de baja lógica un servicio."""
    token = session["access_token"]
    respuesta, estado = dar_de_baja_servicio(token, id)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 200:
        flash("Servicio dado de baja correctamente.", "success")
    else:
        flash(extraer_mensaje_error(respuesta), "error")
    return redirect(url_for("admin_servicios.index"))


@admin_servicios_bp.route("/<int:id>/reactivar", methods=["POST"])
@admin_required
def reactivar(id):
    """Reactiva un servicio inactivo."""
    token = session["access_token"]
    respuesta, estado = reactivar_servicio(token, id)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 200:
        flash("Servicio reactivado correctamente.", "success")
    else:
        flash(extraer_mensaje_error(respuesta), "error")
    return redirect(url_for("admin_servicios.index"))
