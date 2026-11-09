from flask import Blueprint, flash, render_template, request
from services.peliculas_service import obtener_cartelera_vigente
from utils.filtros import validar_filtros_cartelera
from utils.peliculas import adaptar_pelicula_para_card

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    """
    Ruta principal (Cartelera / Home).
    Consume el catálogo real del Backend mediante el servicio de películas.
    Si el backend responde con éxito, provee las películas dinámicas.
    Si el backend no está disponible o falla, renderiza el fallback integrado del template.
    """
    try:
        filtros = validar_filtros_cartelera(request.args)
    except ValueError as error:
        flash(str(error), "error")
        filtros = {}

    respuesta, estado = obtener_cartelera_vigente(filtros)
    if estado == 200 and isinstance(respuesta, list) and respuesta:
        peliculas = [adaptar_pelicula_para_card(p) for p in respuesta]
        return render_template("index.html", peliculas=peliculas)
    return render_template("index.html")
