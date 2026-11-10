from flask import Blueprint, render_template
from services.peliculas_service import obtener_cartelera_vigente

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    """
    Ruta principal (Cartelera / Home).
    Consume exclusivamente el catálogo real del Backend.
    Si el backend responde vacío o falla, refleja el estado real sin inventar datos.
    """
    peliculas = obtener_cartelera_vigente()
    backend_disponible = peliculas is not None
    return render_template(
        "index.html",
        peliculas=peliculas or [],
        backend_disponible=backend_disponible,
    )
