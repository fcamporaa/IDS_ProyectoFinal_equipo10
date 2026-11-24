"""Rutas del backoffice para la administración de funciones."""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.admin_funciones_service import (
    actualizar_funcion,
    crear_funcion,
    dar_de_baja_funcion,
    reactivar_funcion,
    listar_funciones_admin,
    listar_locales,
    listar_peliculas_admin,
    listar_salas_por_local,
)
from utils.auth import admin_required
from utils.errores import extraer_mensaje_error
from utils.funciones import (
    ESTADOS_FUNCION_TERMINALES,
    armar_inicio_iso,
    borrador_desde_funcion,
    combinar_salas,
    preparar_funciones_para_tabla,
)

admin_funciones_bp = Blueprint("admin_funciones", __name__, url_prefix="/admin/funciones")

FORMATOS_FUNCION = ("2D", "3D", "4D")


def _redirigir_sesion_expirada():
    """Limpia la sesión local y manda al login cuando el backend rechaza el token."""
    session.pop("access_token", None)
    session.pop("usuario", None)
    flash("La sesión expiró. Volvé a iniciar sesión.", "error")
    return redirect(url_for("auth.login"))


def _borrador_vacio() -> dict:
    """Borrador inicial del formulario de alta."""
    return {
        "id_pelicula": "",
        "id_sala": "",
        "id_local": "",
        "fecha": "",
        "hora": "",
        "formato": "2D",
        "idioma": "",
        "subtitulada": False,
        "precio_entrada": "",
    }


def _borrador_desde_formulario(form) -> dict:
    """Conserva los valores crudos del formulario para re-renderizar sin perder datos."""
    return {
        "id_pelicula": (form.get("id_pelicula") or "").strip(),
        "id_sala": (form.get("id_sala") or "").strip(),
        "id_local": (form.get("id_local") or "").strip(),
        "fecha": (form.get("fecha") or "").strip(),
        "hora": (form.get("hora") or "").strip(),
        "formato": (form.get("formato") or "2D").strip(),
        "idioma": (form.get("idioma") or "").strip(),
        "subtitulada": "subtitulada" in form,
        "precio_entrada": (form.get("precio_entrada") or "").strip(),
    }


def _leer_formulario(form) -> dict:
    """Lee el formulario de alta o edición y valida tipos y formato de fecha/hora."""
    borrador = _borrador_desde_formulario(form)

    try:
        id_pelicula = int(borrador["id_pelicula"]) if borrador["id_pelicula"] else None
    except ValueError:
        raise ValueError("La película seleccionada no es válida.") from None

    try:
        id_sala = int(borrador["id_sala"]) if borrador["id_sala"] else None
    except ValueError:
        raise ValueError("La sala seleccionada no es válida.") from None

    try:
        precio_entrada = (
            float(borrador["precio_entrada"]) if borrador["precio_entrada"] else None
        )
    except ValueError:
        raise ValueError("El precio de la entrada debe ser un número válido.") from None

    inicio = None
    if borrador["fecha"] or borrador["hora"]:
        inicio = armar_inicio_iso(borrador["fecha"], borrador["hora"])

    return {
        **borrador,
        "id_pelicula": id_pelicula,
        "id_sala": id_sala,
        "inicio": inicio,
        "idioma": borrador["idioma"] or None,
        "precio_entrada": precio_entrada,
    }


def _cargar_contexto(token: str):
    """
    Carga funciones admin, películas activas, locales y salas por local.
    Devuelve (funciones, peliculas_activas, locales, salas, error_backend, redireccion).
    """
    funciones_raw, estado_func = listar_funciones_admin(token)
    if estado_func in (401, 403):
        return None, None, None, None, None, _redirigir_sesion_expirada()

    errores = []
    if estado_func != 200 or not isinstance(funciones_raw, list):
        flash("No se pudo cargar el listado de funciones.", "error")
        funciones_raw = []
        errores.append("No se pudo cargar el listado de funciones.")

    funciones = preparar_funciones_para_tabla(funciones_raw)

    peliculas_raw, estado_pel = listar_peliculas_admin(token)
    if estado_pel in (401, 403):
        return None, None, None, None, None, _redirigir_sesion_expirada()

    peliculas_activas = []
    if estado_pel == 200 and isinstance(peliculas_raw, list):
        peliculas_activas = [p for p in peliculas_raw if p.get("activa", True)]
    else:
        flash("No se pudo cargar el listado de películas.", "error")
        errores.append("No se pudo cargar el listado de películas.")

    locales_raw, estado_loc = listar_locales(token)
    if estado_loc in (401, 403):
        return None, None, None, None, None, _redirigir_sesion_expirada()

    locales = []
    salas_por_local = {}
    if estado_loc == 200 and isinstance(locales_raw, list):
        locales = [local for local in locales_raw if local.get("activo", True)]
        for local in locales:
            id_local = local["id_local"]
            s_list, s_estado = listar_salas_por_local(token, id_local)
            if s_estado in (401, 403):
                return None, None, None, None, None, _redirigir_sesion_expirada()
            if s_estado == 200 and isinstance(s_list, list):
                salas_por_local[id_local] = s_list
            else:
                salas_por_local[id_local] = []
                errores.append(f"No se pudieron cargar las salas del complejo {id_local}.")
    else:
        flash("No se pudieron cargar los complejos.", "error")
        errores.append("No se pudieron cargar los complejos.")

    salas = combinar_salas(locales, salas_por_local)

    return funciones, peliculas_activas, locales, salas, " ".join(errores) or None, None


def _normalizar_inicio(valor) -> str:
    """Reduce el inicio a minutos, la precisión que maneja el formulario."""
    if not valor:
        return ""
    try:
        return datetime.fromisoformat(str(valor)).strftime("%Y-%m-%dT%H:%M")
    except (ValueError, TypeError):
        return str(valor)[:16]


def _payload_actualizacion(datos: dict, funcion_actual: dict) -> dict:
    """
    Envía solo los campos modificados. Evita revalidar un inicio ya pasado al
    editar una función en curso y evita chequeos innecesarios de solapamiento.
    """
    comparaciones = {
        "id_pelicula": funcion_actual.get("id_pelicula"),
        "id_sala": funcion_actual.get("id_sala"),
        "inicio": funcion_actual.get("inicio"),
        "formato": funcion_actual.get("formato"),
        "idioma": funcion_actual.get("idioma"),
        "subtitulada": bool(funcion_actual.get("subtitulada")),
        "precio_entrada": funcion_actual.get("precio_entrada"),
    }
    payload = {}
    for campo, valor_actual in comparaciones.items():
        valor_nuevo = datos.get(campo)
        if campo == "precio_entrada" and valor_nuevo is not None:
            valor_nuevo = float(valor_nuevo)
        if campo == "inicio":
            cambia = _normalizar_inicio(valor_nuevo) != _normalizar_inicio(valor_actual)
        else:
            cambia = valor_nuevo != valor_actual
        if cambia:
            payload[campo] = valor_nuevo

    if funcion_actual.get("estado") in ESTADOS_FUNCION_TERMINALES:
        payload["estado"] = funcion_actual["estado"]

    return payload


def _renderizar_pagina(
    *,
    borrador: dict,
    abrir_formulario: bool,
    modo_formulario: str,
    accion_formulario: str,
    id_funcion_editando: int | None = None,
):
    """Centraliza la carga de datos y el renderizado de la vista de gestión de funciones."""
    token = session.get("access_token")
    funciones, peliculas, locales, salas, error_backend, redireccion = _cargar_contexto(token)
    if redireccion is not None:
        return redireccion

    # Determinar el id_local de la función que se está editando (para filtrar salas)
    id_local_funcion = None
    local_match = None
    if borrador.get("id_sala"):
        # Buscar la función raw para obtener su id_local
        funciones_raw, _ = listar_funciones_admin(token) if token else ([], 200)
        if isinstance(funciones_raw, list):
            func = next((f for f in funciones_raw if str(f.get("id_funcion", "")) == str(borrador.get("id_sala"))), None)
            if func:
                id_local_funcion = func.get("id_local")
                local_match = func  # Pasar la función completa para usarla en el template
        # Fallback: si no se encontró la función raw, intentar desde el borrador
        if not id_local_funcion and borrador.get("id_sala"):
            id_local_funcion = borrador.get("id_local")

    if not borrador.get("id_local") and borrador.get("id_sala") and id_local_funcion:
        sala_actual = next(
            (
                sala
                for sala in salas
                if str(sala.get("id_local")) == str(id_local_funcion) and str(sala.get("id_sala")) == str(borrador["id_sala"])
            ),
            None,
        )
        if sala_actual:
            borrador = {**borrador, "id_local": sala_actual["id_local"]}

    fecha_minima = datetime.now().strftime("%Y-%m-%d")
    if modo_formulario == "editar" and borrador.get("fecha"):
        # Una función en curso pudo empezar antes de medianoche; el navegador
        # debe permitir guardar cambios sin reenviar el inicio.
        fecha_minima = min(fecha_minima, borrador["fecha"])

    return render_template(
        "backoffice/funciones.html",
        funciones=funciones,
        peliculas=peliculas,
        locales=locales,
        salas=salas,
        borrador=borrador,
        abrir_formulario=abrir_formulario,
        modo_formulario=modo_formulario,
        accion_formulario=accion_formulario,
        id_funcion_editando=id_funcion_editando,
        formatos=FORMATOS_FUNCION,
        fecha_minima=fecha_minima,
        error_backend=error_backend,
        id_local_funcion=id_local_funcion,
        local_match=local_match,
    )


@admin_funciones_bp.route("", methods=["GET"])
@admin_required
def index():
    """Lista todas las funciones y permite abrir el formulario de alta si viene ?nuevo=1."""
    abrir_formulario = request.args.get("nuevo") == "1"
    return _renderizar_pagina(
        borrador=_borrador_vacio(),
        abrir_formulario=abrir_formulario,
        modo_formulario="crear",
        accion_formulario=url_for("admin_funciones.crear"),
    )


@admin_funciones_bp.route("", methods=["POST"])
@admin_required
def crear():
    """Crea una nueva función."""
    token = session["access_token"]
    try:
        datos_form = _leer_formulario(request.form)
    except ValueError as e:
        flash(str(e), "error")
        return _renderizar_pagina(
            borrador=_borrador_desde_formulario(request.form),
            abrir_formulario=True,
            modo_formulario="crear",
            accion_formulario=url_for("admin_funciones.crear"),
        )

    payload = {
        "id_pelicula": datos_form["id_pelicula"],
        "id_sala": datos_form["id_sala"],
        "inicio": datos_form["inicio"],
        "formato": datos_form["formato"],
        "idioma": datos_form["idioma"],
        "subtitulada": datos_form["subtitulada"],
        "precio_entrada": datos_form["precio_entrada"],
    }

    respuesta, estado = crear_funcion(token, payload)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 201:
        flash("Función programada correctamente.", "success")
        return redirect(url_for("admin_funciones.index"))

    flash(extraer_mensaje_error(respuesta), "error")
    return _renderizar_pagina(
        borrador=_borrador_desde_formulario(request.form),
        abrir_formulario=True,
        modo_formulario="crear",
        accion_formulario=url_for("admin_funciones.crear"),
    )


@admin_funciones_bp.route("/<int:id_funcion>/editar", methods=["GET"])
@admin_required
def editar(id_funcion):
    """Carga el formulario de edición con los datos de la función."""
    token = session["access_token"]
    funciones_raw, estado = listar_funciones_admin(token)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado != 200 or not isinstance(funciones_raw, list):
        flash("No se pudo obtener la función.", "error")
        return redirect(url_for("admin_funciones.index"))

    funcion = next((f for f in funciones_raw if f["id_funcion"] == id_funcion), None)
    if not funcion:
        flash("Función no encontrada.", "error")
        return redirect(url_for("admin_funciones.index"))

    return _renderizar_pagina(
        borrador=borrador_desde_funcion(funcion),
        abrir_formulario=True,
        modo_formulario="editar",
        accion_formulario=url_for("admin_funciones.actualizar", id_funcion=id_funcion),
        id_funcion_editando=id_funcion,
    )


@admin_funciones_bp.route("/<int:id_funcion>/editar", methods=["POST"])
@admin_required
def actualizar(id_funcion):
    """Actualiza una función existente."""
    token = session["access_token"]
    try:
        datos_form = _leer_formulario(request.form)
    except ValueError as e:
        flash(str(e), "error")
        return _renderizar_pagina(
            borrador=_borrador_desde_formulario(request.form),
            abrir_formulario=True,
            modo_formulario="editar",
            accion_formulario=url_for("admin_funciones.actualizar", id_funcion=id_funcion),
            id_funcion_editando=id_funcion,
        )

    funciones_raw, estado_listado = listar_funciones_admin(token)
    if estado_listado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado_listado != 200 or not isinstance(funciones_raw, list):
        flash("No se pudo obtener la función.", "error")
        return redirect(url_for("admin_funciones.index"))

    funcion_actual = next(
        (funcion for funcion in funciones_raw if funcion["id_funcion"] == id_funcion),
        None,
    )
    if not funcion_actual:
        flash("Función no encontrada.", "error")
        return redirect(url_for("admin_funciones.index"))

    payload = _payload_actualizacion(datos_form, funcion_actual)
    if not payload:
        flash("No se detectaron cambios en la función.", "info")
        return redirect(url_for("admin_funciones.index"))

    respuesta, estado = actualizar_funcion(token, id_funcion, payload)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 200:
        flash("Función actualizada correctamente.", "success")
        return redirect(url_for("admin_funciones.index"))

    flash(extraer_mensaje_error(respuesta), "error")
    return _renderizar_pagina(
        borrador=_borrador_desde_formulario(request.form),
        abrir_formulario=True,
        modo_formulario="editar",
        accion_formulario=url_for("admin_funciones.actualizar", id_funcion=id_funcion),
        id_funcion_editando=id_funcion,
    )


@admin_funciones_bp.route("/<int:id_funcion>/eliminar", methods=["POST"])
@admin_required
def eliminar(id_funcion):
    """Da de baja (cancela) una función."""
    token = session["access_token"]
    respuesta, estado = dar_de_baja_funcion(token, id_funcion)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 200:
        flash("Función cancelada correctamente.", "success")
        return redirect(url_for("admin_funciones.index"))

    flash(extraer_mensaje_error(respuesta), "error")
    return redirect(url_for("admin_funciones.index"))

@admin_funciones_bp.route("/<int:id_funcion>/reactivar", methods=["POST"])
@admin_required
def reactivar(id_funcion):
    """Reactiva una función cancelada volviéndola a estado PROGRAMADA."""
    token = session["access_token"]
    respuesta, estado = reactivar_funcion(token, id_funcion)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 200:
        flash("Función reactivada correctamente.", "success")
        return redirect(url_for("admin_funciones.index"))

    flash(extraer_mensaje_error(respuesta), "error")
    return redirect(url_for("admin_funciones.index"))
