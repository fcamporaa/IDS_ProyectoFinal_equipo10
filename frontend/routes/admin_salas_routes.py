from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.admin_salas_service import (
    actualizar_sala,
    crear_sala,
    dar_de_baja_sala,
    generar_butacas,
    listar_locales,
    listar_salas_admin,
    reactivar_sala,
)
from utils.auth import admin_required
from utils.errores import extraer_mensaje_error

admin_salas_bp = Blueprint("admin_salas", __name__, url_prefix="/admin/salas")

MAX_FILAS = 26
MAX_ASIENTOS = 30


def _redirigir_sesion_expirada():
    """Limpia la sesión local y manda al login cuando el backend rechaza el token."""
    session.pop("access_token", None)
    session.pop("usuario", None)
    flash("La sesión expiró. Volvé a iniciar sesión.", "error")
    return redirect(url_for("auth.login"))


def _borrador_vacio() -> dict:
    return {
        "id_local": "",
        "numero": "",
        "filas": "",
        "asientos_por_fila": "",
        "activa": True,
    }


def _borrador_desde_formulario(form, incluir_activa: bool = False) -> dict:
    borrador = {
        "id_local": form.get("id_local", ""),
        "numero": form.get("numero", ""),
        "filas": form.get("filas", ""),
        "asientos_por_fila": form.get("asientos_por_fila", ""),
    }
    if incluir_activa:
        borrador["activa"] = "activa" in form
    return borrador


def _leer_entero_positivo(form, campo: str, etiqueta: str) -> int:
    raw = (form.get(campo) or "").strip()
    if not raw:
        raise ValueError(f"El campo {etiqueta} es obligatorio.")
    try:
        valor = int(raw)
    except ValueError as exc:
        raise ValueError(f"El campo {etiqueta} debe ser un número entero.") from exc
    if valor <= 0:
        raise ValueError(f"El campo {etiqueta} debe ser un entero positivo.")
    return valor


def _leer_formulario_alta(form) -> tuple[int, dict]:
    """Lee el formulario de alta de sala + layout de butacas."""
    id_local = _leer_entero_positivo(form, "id_local", "complejo")
    numero = _leer_entero_positivo(form, "numero", "número de sala")
    filas = _leer_entero_positivo(form, "filas", "filas")
    asientos = _leer_entero_positivo(form, "asientos_por_fila", "asientos por fila")

    if filas > MAX_FILAS:
        raise ValueError(f"Las filas no pueden superar {MAX_FILAS} (A-Z).")
    if asientos > MAX_ASIENTOS:
        raise ValueError(f"Los asientos por fila no pueden superar {MAX_ASIENTOS}.")

    return id_local, {
        "numero": numero,
        "filas": filas,
        "asientos_por_fila": asientos,
        "activa": True,
    }


def _leer_formulario_edicion(form) -> dict:
    """Lee el formulario de edición (número y estado)."""
    numero = _leer_entero_positivo(form, "numero", "número de sala")
    return {
        "numero": numero,
        "activa": "activa" in form,
    }


def _leer_formulario_butacas(form) -> dict:
    filas = _leer_entero_positivo(form, "filas", "filas")
    asientos = _leer_entero_positivo(form, "asientos_por_fila", "asientos por fila")
    if filas > MAX_FILAS:
        raise ValueError(f"Las filas no pueden superar {MAX_FILAS} (A-Z).")
    if asientos > MAX_ASIENTOS:
        raise ValueError(f"Los asientos por fila no pueden superar {MAX_ASIENTOS}.")
    return {"filas": filas, "asientos_por_fila": asientos}


def _cargar_locales(token: str):
    locales, estado = listar_locales(token)
    if estado in (401, 403):
        return None, estado
    if estado != 200 or not isinstance(locales, list):
        return [], estado
    return locales, estado


def _renderizar_pagina(
    *,
    borrador: dict,
    abrir_formulario: bool,
    modo_formulario: str,
    accion_formulario: str,
    id_sala_editando: int | None = None,
    abrir_butacas: bool = False,
    id_sala_butacas: int | None = None,
    borrador_butacas: dict | None = None,
):
    """Centraliza la carga del listado y el render del ABM de salas."""
    token = session.get("access_token")
    salas, estado = listar_salas_admin(token)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()

    error_backend = None
    if estado != 200 or not isinstance(salas, list):
        flash("No se pudo cargar el listado de salas.", "error")
        salas = []
        error_backend = "No se pudo cargar el listado de salas."

    locales, estado_locales = _cargar_locales(token)
    if estado_locales in (401, 403):
        return _redirigir_sesion_expirada()
    if locales is None:
        locales = []

    return render_template(
        "backoffice/salas.html",
        salas=salas,
        locales=locales,
        borrador=borrador,
        abrir_formulario=abrir_formulario,
        modo_formulario=modo_formulario,
        accion_formulario=accion_formulario,
        id_sala_editando=id_sala_editando,
        abrir_butacas=abrir_butacas,
        id_sala_butacas=id_sala_butacas,
        borrador_butacas=borrador_butacas
        or {"filas": "", "asientos_por_fila": ""},
        max_filas=MAX_FILAS,
        max_asientos=MAX_ASIENTOS,
        error_backend=error_backend,
    )


@admin_salas_bp.route("", methods=["GET"])
@admin_required
def index():
    """Lista todas las salas del sistema."""
    abrir_nuevo = request.args.get("nuevo") == "1"
    return _renderizar_pagina(
        borrador=_borrador_vacio(),
        abrir_formulario=abrir_nuevo,
        modo_formulario="crear",
        accion_formulario=url_for("admin_salas.crear"),
    )


@admin_salas_bp.route("", methods=["POST"])
@admin_required
def crear():
    """Crea una nueva sala con butacas."""
    token = session["access_token"]
    try:
        id_local, datos = _leer_formulario_alta(request.form)
    except ValueError as e:
        flash(str(e), "error")
        return _renderizar_pagina(
            borrador=_borrador_desde_formulario(request.form),
            abrir_formulario=True,
            modo_formulario="crear",
            accion_formulario=url_for("admin_salas.crear"),
        )

    respuesta, estado = crear_sala(token, id_local, datos)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 201:
        flash("Sala creada correctamente con su grilla de butacas.", "success")
        return redirect(url_for("admin_salas.index"))

    flash(extraer_mensaje_error(respuesta), "error")
    return _renderizar_pagina(
        borrador={
            "id_local": str(id_local),
            "numero": str(datos["numero"]),
            "filas": str(datos["filas"]),
            "asientos_por_fila": str(datos["asientos_por_fila"]),
            "activa": True,
        },
        abrir_formulario=True,
        modo_formulario="crear",
        accion_formulario=url_for("admin_salas.crear"),
    )


@admin_salas_bp.route("/<int:id>/editar", methods=["GET"])
@admin_required
def editar(id):
    """Carga el formulario de edición con los datos de la sala."""
    token = session["access_token"]
    salas, estado = listar_salas_admin(token)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado != 200 or not isinstance(salas, list):
        flash("No se pudo obtener la sala.", "error")
        return redirect(url_for("admin_salas.index"))

    sala = next((s for s in salas if s["id_sala"] == id), None)
    if not sala:
        flash("Sala no encontrada.", "error")
        return redirect(url_for("admin_salas.index"))

    borrador = {
        "id_local": str(sala.get("id_local", "")),
        "numero": str(sala.get("numero", "")),
        "filas": "",
        "asientos_por_fila": "",
        "activa": sala.get("activa", True),
    }

    return _renderizar_pagina(
        borrador=borrador,
        abrir_formulario=True,
        modo_formulario="editar",
        accion_formulario=url_for("admin_salas.actualizar", id=id),
        id_sala_editando=id,
    )


@admin_salas_bp.route("/<int:id>/editar", methods=["POST"])
@admin_required
def actualizar(id):
    """Actualiza número y estado de una sala."""
    token = session["access_token"]
    try:
        datos = _leer_formulario_edicion(request.form)
    except ValueError as e:
        flash(str(e), "error")
        return _renderizar_pagina(
            borrador=_borrador_desde_formulario(request.form, incluir_activa=True),
            abrir_formulario=True,
            modo_formulario="editar",
            accion_formulario=url_for("admin_salas.actualizar", id=id),
            id_sala_editando=id,
        )

    respuesta, estado = actualizar_sala(token, id, datos)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 200:
        flash("Cambios guardados correctamente.", "success")
        return redirect(url_for("admin_salas.index"))

    flash(extraer_mensaje_error(respuesta), "error")
    return _renderizar_pagina(
        borrador={
            "id_local": request.form.get("id_local", ""),
            "numero": str(datos["numero"]),
            "filas": "",
            "asientos_por_fila": "",
            "activa": datos["activa"],
        },
        abrir_formulario=True,
        modo_formulario="editar",
        accion_formulario=url_for("admin_salas.actualizar", id=id),
        id_sala_editando=id,
    )


@admin_salas_bp.route("/<int:id>/butacas", methods=["GET"])
@admin_required
def formulario_butacas(id):
    """Abre el formulario para generar butacas en una sala vacía."""
    token = session["access_token"]
    salas, estado = listar_salas_admin(token)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado != 200 or not isinstance(salas, list):
        flash("No se pudo obtener la sala.", "error")
        return redirect(url_for("admin_salas.index"))

    sala = next((s for s in salas if s["id_sala"] == id), None)
    if not sala:
        flash("Sala no encontrada.", "error")
        return redirect(url_for("admin_salas.index"))
    if int(sala.get("capacidad") or 0) > 0:
        flash("La sala ya tiene butacas registradas.", "error")
        return redirect(url_for("admin_salas.index"))

    return _renderizar_pagina(
        borrador=_borrador_vacio(),
        abrir_formulario=False,
        modo_formulario="crear",
        accion_formulario=url_for("admin_salas.crear"),
        abrir_butacas=True,
        id_sala_butacas=id,
    )


@admin_salas_bp.route("/<int:id>/butacas", methods=["POST"])
@admin_required
def crear_butacas(id):
    """Genera butacas para una sala vacía."""
    token = session["access_token"]
    try:
        datos = _leer_formulario_butacas(request.form)
    except ValueError as e:
        flash(str(e), "error")
        return _renderizar_pagina(
            borrador=_borrador_vacio(),
            abrir_formulario=False,
            modo_formulario="crear",
            accion_formulario=url_for("admin_salas.crear"),
            abrir_butacas=True,
            id_sala_butacas=id,
            borrador_butacas={
                "filas": request.form.get("filas", ""),
                "asientos_por_fila": request.form.get("asientos_por_fila", ""),
            },
        )

    respuesta, estado = generar_butacas(token, id, datos)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 201:
        flash("Butacas generadas correctamente.", "success")
        return redirect(url_for("admin_salas.index"))

    flash(extraer_mensaje_error(respuesta), "error")
    return _renderizar_pagina(
        borrador=_borrador_vacio(),
        abrir_formulario=False,
        modo_formulario="crear",
        accion_formulario=url_for("admin_salas.crear"),
        abrir_butacas=True,
        id_sala_butacas=id,
        borrador_butacas={
            "filas": str(datos["filas"]),
            "asientos_por_fila": str(datos["asientos_por_fila"]),
        },
    )


@admin_salas_bp.route("/<int:id>/eliminar", methods=["POST"])
@admin_required
def eliminar(id):
    """Da de baja lógica una sala."""
    token = session["access_token"]
    respuesta, estado = dar_de_baja_sala(token, id)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 200:
        flash("Sala dada de baja correctamente.", "success")
    else:
        flash(extraer_mensaje_error(respuesta), "error")
    return redirect(url_for("admin_salas.index"))


@admin_salas_bp.route("/<int:id>/reactivar", methods=["POST"])
@admin_required
def reactivar(id):
    """Reactiva una sala inactiva."""
    token = session["access_token"]
    respuesta, estado = reactivar_sala(token, id)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 200:
        flash("Sala reactivada correctamente.", "success")
    else:
        flash(extraer_mensaje_error(respuesta), "error")
    return redirect(url_for("admin_salas.index"))
