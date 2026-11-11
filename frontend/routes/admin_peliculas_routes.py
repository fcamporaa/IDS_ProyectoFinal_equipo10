from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.admin_peliculas_service import (
    actualizar_pelicula,
    buscar_peliculas_externas,
    crear_pelicula,
    dar_de_baja_pelicula,
    listar_peliculas_admin,
    obtener_pelicula,
    obtener_pelicula_externa,
    reactivar_pelicula,
)
from services.peliculas_service import obtener_generos
from utils.auth import admin_required
from utils.errores import extraer_mensaje_error
from utils.peliculas import mapear_generos_externos

admin_peliculas_bp = Blueprint(
    "admin_peliculas", __name__, url_prefix="/admin/peliculas"
)

CLASIFICACIONES_SUGERIDAS = ("ATP", "+13", "+16", "+18", "PG", "PG-13", "R")


def _redirigir_sesion_expirada():
    """Limpia la sesión local y manda al login cuando el backend rechaza el token."""
    session.pop("access_token", None)
    session.pop("usuario", None)
    flash("La sesión expiró. Volvé a iniciar sesión.", "error")
    return redirect(url_for("auth.login"))


def _borrador_vacio() -> dict:
    """Borrador inicial del formulario de alta, con todas las claves del contrato."""
    return {
        "titulo": "",
        "sinopsis": "",
        "poster_url": "",
        "trailer_url": "",
        "duracion_min": "",
        "clasificacion": "",
        "anio_estreno": "",
        "origen_api": "CUSTOM",
        "id_api": "",
        "generos_ids": [],
        "generos_no_mapeados": [],
        "activa": True,
    }


def _leer_generos_ids(form) -> list[int]:
    """Convierte los checkboxes de géneros en una lista de ids enteros."""
    ids_generos = []
    for valor in form.getlist("generos_ids"):
        try:
            ids_generos.append(int(valor))
        except (TypeError, ValueError):
            continue
    return ids_generos


def _convertir_entero_formulario(valor, etiqueta: str) -> int | None:
    """Convierte un campo numérico del formulario; vacío es None y texto inválido es error local."""
    texto = (valor or "").strip()
    if not texto:
        return None
    try:
        return int(texto)
    except ValueError:
        raise ValueError(f"El campo {etiqueta} debe ser un número entero.") from None


def _leer_formulario(form, convertir_numeros: bool = True) -> dict:
    """
    Lee el formulario de alta o edición una sola vez.
    Con `convertir_numeros=False` conserva los valores crudos para re-renderizar sin perder datos.
    """
    id_api = (form.get("id_api") or "").strip() or None
    datos = {
        "titulo": (form.get("titulo") or "").strip(),
        "sinopsis": (form.get("sinopsis") or "").strip() or None,
        "poster_url": (form.get("poster_url") or "").strip() or None,
        "trailer_url": (form.get("trailer_url") or "").strip() or None,
        "clasificacion": (form.get("clasificacion") or "").strip() or None,
        "origen_api": "OMDB" if id_api else "CUSTOM",
        "id_api": id_api,
        "generos_ids": _leer_generos_ids(form),
        "generos_no_mapeados": [],
        "activa": form.get("activa") == "on",
    }

    if convertir_numeros:
        datos["duracion_min"] = _convertir_entero_formulario(
            form.get("duracion_min"), "duración"
        )
        datos["anio_estreno"] = _convertir_entero_formulario(
            form.get("anio_estreno"), "año"
        )
    else:
        datos["duracion_min"] = (form.get("duracion_min") or "").strip()
        datos["anio_estreno"] = (form.get("anio_estreno") or "").strip()

    return datos


def _cargar_contexto_listado(token: str):
    """
    Carga películas y géneros para las tres vistas que comparten el listado.
    Devuelve (peliculas, generos, error_backend, redireccion).
    """
    peliculas, estado = listar_peliculas_admin(token)
    if estado in (401, 403):
        return None, None, None, _redirigir_sesion_expirada()

    errores = []
    if estado != 200 or not isinstance(peliculas, list):
        flash("No se pudo cargar el listado de películas.", "error")
        peliculas = []
        errores.append("No se pudo cargar el listado de películas.")

    generos, estado_generos = obtener_generos()
    if estado_generos != 200 or not isinstance(generos, list):
        flash("No se pudieron cargar los géneros.", "error")
        generos = []
        errores.append("No se pudieron cargar los géneros.")

    return peliculas, generos, " ".join(errores) or None, None


def _renderizar_pagina(
    *,
    borrador: dict,
    abrir_formulario: bool,
    modo_formulario: str,
    accion_formulario: str,
    busqueda: str = "",
    resultados_externos: list[dict] | None = None,
    detalle_externo: dict | None = None,
):
    """
    Centraliza la carga del listado y el render de la vista del ABM.
    Si recibe un detalle de OMDb, arma el borrador y abre el formulario precargado.
    """
    token = session.get("access_token")
    peliculas, generos, error_backend, redireccion = _cargar_contexto_listado(token)
    if redireccion is not None:
        return redireccion

    if detalle_externo:
        generos_ids, generos_no_mapeados = mapear_generos_externos(
            detalle_externo.get("generos", []), generos
        )
        borrador = {
            "titulo": detalle_externo.get("titulo") or "",
            "sinopsis": detalle_externo.get("sinopsis") or "",
            "poster_url": detalle_externo.get("poster_url") or "",
            "trailer_url": "",
            "duracion_min": detalle_externo.get("duracion_min") or "",
            "clasificacion": detalle_externo.get("clasificacion") or "",
            "anio_estreno": detalle_externo.get("anio_estreno") or "",
            "origen_api": detalle_externo.get("origen_api") or "OMDB",
            "id_api": detalle_externo.get("id_api") or "",
            "generos_ids": generos_ids,
            "generos_no_mapeados": generos_no_mapeados,
            "activa": True,
        }
        abrir_formulario = True

    return render_template(
        "backoffice/peliculas.html",
        peliculas=peliculas,
        generos=generos,
        busqueda=busqueda,
        resultados_externos=resultados_externos or [],
        borrador=borrador,
        abrir_formulario=abrir_formulario,
        modo_formulario=modo_formulario,
        accion_formulario=accion_formulario,
        clasificaciones=CLASIFICACIONES_SUGERIDAS,
        anio_maximo=datetime.now().year + 5,
        error_backend=error_backend,
    )


@admin_peliculas_bp.route("", methods=["GET"])
@admin_required
def index():
    """Lista el catálogo completo y resuelve la búsqueda o la precarga desde OMDb."""
    token = session["access_token"]
    busqueda = request.args.get("busqueda", "").strip()
    id_api = request.args.get("id_api", "").strip()
    resultados_externos = []
    detalle_externo = None

    if busqueda:
        resultados, estado = buscar_peliculas_externas(token, busqueda)
        if estado in (401, 403):
            return _redirigir_sesion_expirada()
        if estado == 200 and isinstance(resultados, list):
            resultados_externos = resultados
        else:
            flash(
                extraer_mensaje_error(resultados, "No se pudo buscar en OMDb."),
                "error",
            )

    if id_api:
        detalle, estado = obtener_pelicula_externa(token, id_api)
        if estado in (401, 403):
            return _redirigir_sesion_expirada()
        if estado == 200 and isinstance(detalle, dict):
            detalle_externo = detalle
        else:
            flash(
                extraer_mensaje_error(detalle, "No se pudo obtener la ficha de OMDb."),
                "error",
            )

    return _renderizar_pagina(
        borrador=_borrador_vacio(),
        abrir_formulario=False,
        modo_formulario="crear",
        accion_formulario=url_for("admin_peliculas.crear"),
        busqueda=busqueda,
        resultados_externos=resultados_externos,
        detalle_externo=detalle_externo,
    )


@admin_peliculas_bp.route("", methods=["POST"])
@admin_required
def crear():
    """Procesa el alta de una película y refresca el listado."""
    token = session["access_token"]
    try:
        datos = _leer_formulario(request.form)
    except ValueError as error:
        flash(str(error), "error")
        return _renderizar_pagina(
            borrador=_leer_formulario(request.form, convertir_numeros=False),
            abrir_formulario=True,
            modo_formulario="crear",
            accion_formulario=url_for("admin_peliculas.crear"),
        )

    respuesta, estado = crear_pelicula(token, datos)
    if estado == 201:
        flash("Película creada correctamente.", "success")
        return redirect(url_for("admin_peliculas.index"))
    if estado in (401, 403):
        return _redirigir_sesion_expirada()

    flash(extraer_mensaje_error(respuesta, "No se pudo crear la película."), "error")
    return _renderizar_pagina(
        borrador=datos,
        abrir_formulario=True,
        modo_formulario="crear",
        accion_formulario=url_for("admin_peliculas.crear"),
    )


@admin_peliculas_bp.route("/<int:id_pelicula>/editar", methods=["GET"])
@admin_required
def editar(id_pelicula: int):
    """Muestra el formulario de edición precargado con el detalle local."""
    token = session["access_token"]
    detalle, estado = obtener_pelicula(token, id_pelicula)
    if estado == 404:
        flash("Película no encontrada.", "error")
        return redirect(url_for("admin_peliculas.index"))
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado != 200 or not isinstance(detalle, dict):
        flash(
            extraer_mensaje_error(detalle, "No se pudo cargar la película."),
            "error",
        )
        return redirect(url_for("admin_peliculas.index"))

    borrador = {
        "titulo": detalle.get("titulo") or "",
        "sinopsis": detalle.get("sinopsis") or "",
        "poster_url": detalle.get("poster_url") or "",
        "trailer_url": detalle.get("trailer_url") or "",
        "duracion_min": detalle.get("duracion_min") or "",
        "clasificacion": detalle.get("clasificacion") or "",
        "anio_estreno": detalle.get("anio_estreno") or "",
        "origen_api": detalle.get("origen_api") or "CUSTOM",
        "id_api": detalle.get("id_api") or "",
        "generos_ids": [
            genero.get("id_genero")
            for genero in detalle.get("generos", [])
            if isinstance(genero, dict)
        ],
        "generos_no_mapeados": [],
        "activa": bool(detalle.get("activa")),
    }

    return _renderizar_pagina(
        borrador=borrador,
        abrir_formulario=True,
        modo_formulario="editar",
        accion_formulario=url_for(
            "admin_peliculas.actualizar", id_pelicula=id_pelicula
        ),
        busqueda="",
    )


@admin_peliculas_bp.route("/<int:id_pelicula>/editar", methods=["POST"])
@admin_required
def actualizar(id_pelicula: int):
    """Procesa la edición completa de una película."""
    token = session["access_token"]
    try:
        datos = _leer_formulario(request.form)
    except ValueError as error:
        flash(str(error), "error")
        return _renderizar_pagina(
            borrador=_leer_formulario(request.form, convertir_numeros=False),
            abrir_formulario=True,
            modo_formulario="editar",
            accion_formulario=url_for(
                "admin_peliculas.actualizar", id_pelicula=id_pelicula
            ),
        )

    respuesta, estado = actualizar_pelicula(token, id_pelicula, datos)
    if estado == 200:
        flash("Cambios guardados.", "success")
        return redirect(url_for("admin_peliculas.index"))
    if estado == 404:
        flash("Película no encontrada.", "error")
        return redirect(url_for("admin_peliculas.index"))
    if estado in (401, 403):
        return _redirigir_sesion_expirada()

    flash(
        extraer_mensaje_error(respuesta, "No se pudieron guardar los cambios."),
        "error",
    )
    return _renderizar_pagina(
        borrador=datos,
        abrir_formulario=True,
        modo_formulario="editar",
        accion_formulario=url_for(
            "admin_peliculas.actualizar", id_pelicula=id_pelicula
        ),
    )


@admin_peliculas_bp.route("/<int:id_pelicula>/eliminar", methods=["POST"])
@admin_required
def eliminar(id_pelicula: int):
    """Da de baja lógica una película y vuelve al listado."""
    token = session["access_token"]
    respuesta, estado = dar_de_baja_pelicula(token, id_pelicula)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 404:
        flash("Película no encontrada.", "error")
    elif estado == 200:
        flash("Película dada de baja.", "success")
    else:
        flash(
            extraer_mensaje_error(respuesta, "No se pudo dar de baja la película."),
            "error",
        )
    return redirect(url_for("admin_peliculas.index"))


@admin_peliculas_bp.route("/<int:id_pelicula>/reactivar", methods=["POST"])
@admin_required
def reactivar(id_pelicula: int):
    """Reactiva una película dada de baja y vuelve al listado."""
    token = session["access_token"]
    respuesta, estado = reactivar_pelicula(token, id_pelicula)
    if estado in (401, 403):
        return _redirigir_sesion_expirada()
    if estado == 404:
        flash("Película no encontrada.", "error")
    elif estado == 200:
        flash("Película reactivada.", "success")
    else:
        flash(
            extraer_mensaje_error(respuesta, "No se pudo reactivar la película."),
            "error",
        )
    return redirect(url_for("admin_peliculas.index"))
