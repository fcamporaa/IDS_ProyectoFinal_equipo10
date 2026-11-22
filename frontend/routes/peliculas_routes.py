from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from services.peliculas_service import (
    crear_resena_pelicula,
    obtener_detalle_pelicula,
    obtener_resenas_pelicula,
)
from utils.csrf import crear_token_csrf, validar_token_csrf
from utils.errores import extraer_mensaje_error
from utils.peliculas import (
    armar_detalle_pelicula,
    procesar_resenas,
    verificar_usuario_puede_resenar,
)

peliculas_bp = Blueprint("peliculas", __name__, url_prefix="/peliculas")


@peliculas_bp.route("/<int:id_pelicula>")
def detalle_pelicula(id_pelicula):
    pelicula, estado = obtener_detalle_pelicula(id_pelicula)
    if estado == 404:
        abort(404)
    if estado != 200 or not isinstance(pelicula, dict):
        flash("No pudimos cargar la película. Intentá de nuevo en unos minutos.", "error")
        return redirect(url_for("home.index"))

    token = session.get("access_token")
    usuario = session.get("usuario")
    id_usuario = usuario.get("id_usuario") if isinstance(usuario, dict) else None

    # Obtener y estructurar reseñas de la película
    resenas_resp, estado_resenas = obtener_resenas_pelicula(id_pelicula, token=token)
    resenas_raw = resenas_resp if estado_resenas == 200 and isinstance(resenas_resp, list) else []
    resenas_data = procesar_resenas(resenas_raw, id_usuario_actual=id_usuario)

    # Verificar si el cliente logueado asistió y puede publicar una reseña
    puede_resenar, id_compra_habilitada = verificar_usuario_puede_resenar(
        id_pelicula=id_pelicula,
        token=token,
        resena_propia=resenas_data.get("resena_propia"),
    )

    csrf_token = crear_token_csrf()

    return render_template(
        "pelicula_detalle.html",
        p=armar_detalle_pelicula(pelicula),
        resenas_data=resenas_data,
        puede_resenar=puede_resenar,
        id_compra_habilitada=id_compra_habilitada,
        csrf_token=csrf_token,
    )


@peliculas_bp.route("/<int:id_pelicula>/resenas", methods=["POST"])
def crear_resena(id_pelicula: int):
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        flash("Formulario vencido o inválido. Volvé a intentarlo.", "error")
        return redirect(url_for("peliculas.detalle_pelicula", id_pelicula=id_pelicula) + "#seccion-resenas")

    token = session.get("access_token")
    if not token:
        flash("Iniciá sesión para publicar una reseña.", "info")
        return redirect(url_for("auth.login"))

    try:
        id_compra = int(request.form.get("id_compra", ""))
        puntuacion = int(request.form.get("puntuacion", ""))
    except (ValueError, TypeError):
        flash("Seleccioná una puntuación válida para la reseña.", "error")
        return redirect(url_for("peliculas.detalle_pelicula", id_pelicula=id_pelicula) + "#seccion-resenas")

    comentario = request.form.get("comentario", "").strip()

    respuesta, estado = crear_resena_pelicula(
        id_pelicula,
        token,
        {
            "id_compra": id_compra,
            "puntuacion": puntuacion,
            "comentario": comentario,
        },
    )

    if estado == 201:
        flash("¡Tu reseña se publicó exitosamente! Gracias por tu opinión.", "success")
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

    return redirect(url_for("peliculas.detalle_pelicula", id_pelicula=id_pelicula) + "#seccion-resenas")
