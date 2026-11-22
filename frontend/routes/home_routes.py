from flask import Blueprint, flash, render_template, request
from services.peliculas_service import obtener_cartelera_vigente, obtener_generos
from utils.filtros import validar_filtros_cartelera
from utils.peliculas import adaptar_pelicula_para_card

home_bp = Blueprint("home", __name__)


def _cargar_generos() -> list[dict]:
    """
    Trae los géneros desde GET /generos para armar los chips del filtro.
    Si el backend falla, devuelve lista vacía: la cartelera sigue funcionando
    y solo queda el chip "Todos".
    """
    generos, estado = obtener_generos()
    if estado != 200 or not isinstance(generos, list):
        return []
    return [
        g
        for g in generos
        if isinstance(g, dict) and g.get("id_genero") is not None and g.get("nombre")
    ]


@home_bp.route("/")
def index():
    """
    Ruta principal (Cartelera / Home).
    Consume exclusivamente el catálogo real del Backend.
    Si el backend responde vacío o falla, refleja el estado real sin inventar datos.
    El filtro por género se resuelve en el servidor con ?id_genero=.
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
        generos=_cargar_generos(),
        genero_activo=filtros.get("id_genero"),
        hay_filtro=bool(filtros),
    )
