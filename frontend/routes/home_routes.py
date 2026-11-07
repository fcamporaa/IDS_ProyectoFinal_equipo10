from flask import Blueprint, render_template
from services.peliculas_service import obtener_cartelera_vigente

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    """
    Ruta principal (Cartelera / Home).
    Consume el catálogo real del Backend mediante el servicio de películas.
    Si el backend responde con éxito, provee las películas dinámicas.
    Si el backend no está disponible o falla, renderiza el fallback integrado del template.
    """
    peliculas = obtener_cartelera_vigente()
    if peliculas:
        return render_template("index.html", peliculas=peliculas)
    return render_template("index.html")
