from flask import Blueprint, flash, render_template, request
from services.peliculas_service import obtener_cartelera_vigente
from utils.filtros import validar_filtros_cartelera
from utils.peliculas import adaptar_pelicula_para_card

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    """
    Ruta principal (Cartelera / Home).
    Consume exclusivamente el catálogo real del Backend.
    Si el backend responde vacío o falla, refleja el estado real sin inventar datos.
    """
     try:
        filtros = validar_filtros_cartelera(request.args)
    except ValueError as error:
        flash(str(error), "error")
        filtros = {}

    respuesta, estado = obtener_cartelera_vigente(filtros)
    backend_disponible = estado == 200 and isinstance(respuesta, list)
    peliculas = (
        [adaptar_pelicula_para_card(p) for p in respuesta]
        if backend_disponible
        else []
    )
    return render_template(
        "index.html",
        peliculas=peliculas,
        backend_disponible=backend_disponible,
    )