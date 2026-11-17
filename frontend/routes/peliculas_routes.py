
from flask import Blueprint, abort, flash, redirect, render_template, url_for

from services.peliculas_service import obtener_detalle_pelicula
from utils.peliculas import armar_detalle_pelicula

peliculas_bp = Blueprint("peliculas", __name__, url_prefix="/peliculas")


@peliculas_bp.route("/<int:id_pelicula>")
def detalle_pelicula(id_pelicula):
    pelicula, estado = obtener_detalle_pelicula(id_pelicula)
    if estado == 404:
        abort(404)
    if estado != 200 or not isinstance(pelicula, dict):
        flash("No pudimos cargar la película. Intentá de nuevo en unos minutos.", "error")
        return redirect(url_for("home.index"))
    return render_template("pelicula_detalle.html", p=armar_detalle_pelicula(pelicula))
    

