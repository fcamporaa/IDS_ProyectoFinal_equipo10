from services.api_client import consultar_backend


def _adaptar_pelicula_para_vista(p: dict) -> dict:
    """Normaliza los campos del backend para el componente card_pelicula.html."""
    generos_raw = p.get("generos", [])
    if isinstance(generos_raw, list):
        nombres_genero = [
            g.get("nombre", "") if isinstance(g, dict) else str(g)
            for g in generos_raw
        ]
    else:
        nombres_genero = []

    genero_str = " / ".join(nombres_genero) if nombres_genero else "Cine"
    slug_genero = " ".join([g.lower() for g in nombres_genero])

    poster = p.get("poster_url") or "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg"
    return {
        "id_pelicula": p.get("id_pelicula"),
        "titulo": p.get("titulo", "Sin título"),
        "sinopsis": p.get("sinopsis", ""),
        "poster_url": poster,
        "backdrop_url": p.get("backdrop_url") or poster,
        "formato": p.get("formato", "2D"),
        "clasificacion": p.get("clasificacion", "ATP"),
        "duracion_min": p.get("duracion_min", 120),
        "anio_estreno": p.get("anio_estreno", 2024),
        "genero": genero_str,
        "genero_slug": slug_genero,
        "subtitulada": bool(p.get("subtitulada", True)),
        "sala_principal": p.get("sala_principal", "Sala 1"),
        "horarios": p.get("horarios", ["17:00", "20:15"]),
    }


def obtener_cartelera_vigente(filtros: dict | None = None):
    """
    Consume el endpoint GET /peliculas del Backend para obtener el catálogo
    vigente de películas con sus respectivos géneros.
    Retorna la lista de películas adaptadas o None si el backend no responde 200.
    """
    respuesta, status = consultar_backend("/peliculas", params=filtros, metodo="GET")
    if status == 200 and isinstance(respuesta, list):
        return [_adaptar_pelicula_para_vista(p) for p in respuesta]
    return None


def obtener_detalle_pelicula(id_pelicula: int):
    """
    Consume el endpoint GET /peliculas/<id> del Backend para obtener los detalles
    completos de una película y sus funciones activas.
    """
    respuesta, status = consultar_backend(f"/peliculas/{id_pelicula}", metodo="GET")
    if status == 200 and isinstance(respuesta, dict):
        return respuesta
    return None



def obtener_resenas_pelicula(id_pelicula: int, token: str):
    """Obtiene reseñas para identificar la reseña propia de un usuario."""
    return consultar_backend(
        f"/peliculas/{id_pelicula}/resenas", token=token, metodo="GET"
    )


def crear_resena_pelicula(id_pelicula: int, token: str, datos: dict):
    """Envía una reseña de compra al backend para validar asistencia y guardarla."""
    return consultar_backend(
        f"/peliculas/{id_pelicula}/resenas",
        token=token,
        metodo="POST",
        datos=datos,
    )
  
def obtener_generos():
    """Consume GET /generos y devuelve (datos, código HTTP) para que la ruta decida."""
    return consultar_backend("/generos", metodo="GET")

