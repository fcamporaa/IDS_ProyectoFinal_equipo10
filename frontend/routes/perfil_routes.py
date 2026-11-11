from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.auth_service import actualizar_perfil, obtener_perfil
from services.compras_service import (
    cancelar_compra_al_backend,
    obtener_compra_del_backend,
    obtener_mis_compras,
)
from services.peliculas_service import (
    crear_resena_pelicula as enviar_resena_pelicula,
    obtener_resenas_pelicula,
)
from utils.csrf import crear_token_csrf, validar_token_csrf
from utils.errores import extraer_mensaje_error

perfil_bp = Blueprint("perfil", __name__)


def _fecha_funcion(compra: dict) -> datetime | None:
    valor = compra.get("fecha_funcion")
    if not isinstance(valor, str) or not valor:
        return None

    try:
        fecha = parsedate_to_datetime(valor)
    except (TypeError, ValueError, OverflowError):
        try:
            fecha = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        except ValueError:
            return None

    if fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)
    return fecha


def _cargar_peliculas_vistas(compras: list, usuario: dict, token: str) -> list[dict]:
    peliculas_vistas = []
    id_usuario = usuario.get("id_usuario")
    ahora = datetime.now(timezone.utc)

    for compra in compras:
        fecha_funcion = _fecha_funcion(compra)
        if (
            compra.get("estado", "").upper() != "PAGADA"
            or fecha_funcion is None
            or fecha_funcion > ahora
        ):
            continue

        detalle, estado_detalle = obtener_compra_del_backend(
            compra.get("id_compra"), token
        )
        if estado_detalle != 200 or not isinstance(detalle, dict):
            continue

        funcion = detalle.get("funcion", {})
        id_pelicula = funcion.get("id_pelicula")
        if not detalle.get("qr_validado_en") or not id_pelicula:
            continue

        resenas, estado_resenas = obtener_resenas_pelicula(id_pelicula, token)
        if estado_resenas != 200 or not isinstance(resenas, list):
            resena_propia = None
            puede_resenar = False
        else:
            resena_propia = next(
                (
                    resena
                    for resena in resenas
                    if resena.get("id_usuario") == id_usuario
                ),
                None,
            )
            puede_resenar = resena_propia is None

        peliculas_vistas.append(
            {
                "id_pelicula": id_pelicula,
                "id_compra": compra.get("id_compra"),
                "titulo": funcion.get("titulo_pelicula", compra.get("pelicula")),
                "fecha_funcion": compra.get("fecha_funcion"),
                "puntuacion": resena_propia.get("puntuacion") if resena_propia else None,
                "comentario": resena_propia.get("comentario") if resena_propia else None,
                "puede_resenar": puede_resenar,
            }
        )

    return peliculas_vistas


def _marcar_reservas_cancelables(reservas: list, token: str) -> None:
    ahora = datetime.now(timezone.utc)
    for compra in reservas:
        compra["puede_cancelar"] = False
        fecha_funcion = _fecha_funcion(compra)
        if fecha_funcion is None or fecha_funcion <= ahora + timedelta(hours=24):
            continue

        detalle, estado_detalle = obtener_compra_del_backend(
            compra.get("id_compra"), token
        )
        compra["puede_cancelar"] = (
            estado_detalle == 200
            and isinstance(detalle, dict)
            and detalle.get("estado") == "PAGADA"
            and detalle.get("qr_validado_en") is None
        )


@perfil_bp.route("/perfil", methods=["GET"])
def index():
    token = session.get("access_token")
    if not token:
        flash("Iniciá sesión para ver tu perfil.", "info")
        return redirect(url_for("auth.login"))

    perfil, estado_perfil = obtener_perfil(token)
    if estado_perfil != 200 or not isinstance(perfil, dict):
        if estado_perfil in (401, 403):
            session.pop("access_token", None)
            session.pop("usuario", None)
            flash("Tu sesión venció. Volvé a iniciar sesión.", "error")
            return redirect(url_for("auth.login"))

        flash(extraer_mensaje_error(perfil, "No se pudo cargar tu perfil."), "error")
        return redirect(url_for("home.index"))

    if perfil.get("rol") != "CLIENTE":
        return redirect(url_for("dashboard.index"))

    session["usuario"] = perfil
    compras, estado_compras = obtener_mis_compras(token)
    error_backend = None
    if estado_compras != 200 or not isinstance(compras, list):
        respuesta_compras = compras
        compras = []
        error_backend = extraer_mensaje_error(
            respuesta_compras, "No se pudo cargar tu historial de compras."
        )

    ahora = datetime.now(timezone.utc)
    reservas_activas = []
    compras_pasadas = []
    for compra in compras:
        fecha_funcion = _fecha_funcion(compra)
        es_futura = (
            compra.get("estado", "").upper() == "PAGADA"
            and fecha_funcion is not None
            and fecha_funcion > ahora
        )
        (reservas_activas if es_futura else compras_pasadas).append(compra)

    _marcar_reservas_cancelables(reservas_activas, token)
    peliculas_vistas = _cargar_peliculas_vistas(compras, perfil, token)

    return render_template(
        "client/perfil_cliente.html",
        usuario_activo=perfil,
        reservas_activas=reservas_activas,
        compras_pasadas=compras_pasadas,
        peliculas_vistas=peliculas_vistas,
        datos_facturacion={},
        error_backend=error_backend,
        csrf_token=crear_token_csrf(),
    )


@perfil_bp.route("/perfil/actualizar", methods=["POST"])
def actualizar():
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        flash("Formulario vencido o inválido. Volvé a intentarlo.", "error")
        return redirect(url_for("perfil.index") + "#perfil-datos")

    token = session.get("access_token")
    if not token:
        flash("Iniciá sesión para editar tu perfil.", "info")
        return redirect(url_for("auth.login"))

    nombre = request.form.get("nombre", "").strip()
    contrasena = request.form.get("contrasena", "")
    confirmar_contrasena = request.form.get("confirmar_contrasena", "")
    if contrasena != confirmar_contrasena:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("perfil.index") + "#perfil-datos")

    datos = {"nombre": nombre}
    if contrasena:
        datos["contrasena"] = contrasena

    respuesta, estado = actualizar_perfil(token, datos)
    if estado == 200:
        perfil, estado_perfil = obtener_perfil(token)
        if estado_perfil == 200 and isinstance(perfil, dict):
            session["usuario"] = perfil
        flash("Tus datos se actualizaron correctamente.", "success")
    else:
        if estado == 401:
            session.pop("access_token", None)
            session.pop("usuario", None)
            flash("Tu sesión venció. Volvé a iniciar sesión.", "error")
            return redirect(url_for("auth.login"))
        flash(
            extraer_mensaje_error(respuesta, "No se pudo actualizar tu perfil."),
            "error",
        )

    return redirect(url_for("perfil.index") + "#perfil-datos")


@perfil_bp.route("/perfil/resenas/<int:id_pelicula>", methods=["POST"])
def crear_resena(id_pelicula: int):
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        flash("Formulario vencido o inválido. Volvé a intentarlo.", "error")
        return redirect(url_for("perfil.index") + "#perfil-vistas")

    token = session.get("access_token")
    if not token:
        flash("Iniciá sesión para publicar una reseña.", "info")
        return redirect(url_for("auth.login"))

    try:
        id_compra = int(request.form.get("id_compra", ""))
        puntuacion = int(request.form.get("puntuacion", ""))
    except ValueError:
        flash("Seleccioná una puntuación válida para la reseña.", "error")
        return redirect(url_for("perfil.index") + "#perfil-vistas")

    respuesta, estado = enviar_resena_pelicula(
        id_pelicula,
        token,
        {
            "id_compra": id_compra,
            "puntuacion": puntuacion,
            "comentario": request.form.get("comentario", "").strip(),
        },
    )
    if estado == 201:
        flash("Tu reseña se publicó correctamente.", "success")
    elif estado == 401:
        session.pop("access_token", None)
        session.pop("usuario", None)
        flash("Tu sesión venció. Volvé a iniciar sesión.", "error")
        return redirect(url_for("auth.login"))
    else:
        flash(
            extraer_mensaje_error(respuesta, "No se pudo publicar la reseña."),
            "error",
        )

    return redirect(url_for("perfil.index") + "#perfil-vistas")


@perfil_bp.route("/perfil/compras/<int:id_compra>/cancelar", methods=["POST"])
def cancelar_compra(id_compra: int):
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        flash("Formulario vencido o inválido. Volvé a intentarlo.", "error")
        return redirect(url_for("perfil.index") + "#perfil-reservas")

    token = session.get("access_token")
    if not token:
        flash("Iniciá sesión para cancelar una compra.", "info")
        return redirect(url_for("auth.login"))

    respuesta, estado = cancelar_compra_al_backend(id_compra, token)
    if estado == 200:
        flash("Compra cancelada. Las butacas quedaron liberadas.", "success")
    elif estado == 401:
        session.pop("access_token", None)
        session.pop("usuario", None)
        flash("Tu sesión venció. Volvé a iniciar sesión.", "error")
        return redirect(url_for("auth.login"))
    else:
        flash(
            extraer_mensaje_error(respuesta, "No se pudo cancelar la compra."),
            "error",
        )

    return redirect(url_for("perfil.index") + "#perfil-reservas")