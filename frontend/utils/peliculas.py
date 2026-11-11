"""Prepara los datos de películas del backend para los templates (agrupa funciones y mapea géneros)."""
from datetime import datetime
import unicodedata

from utils.formatos import formatear_fecha_corta, formatear_hora


# Géneros de OMDb (normalizados sin acentos y en minúsculas) -> nombre local.
MAPEO_GENEROS_OMDB = {
    "action": "Acción",
    "adventure": "Aventura",
    "animation": "Animación",
    "comedy": "Comedia",
    "drama": "Drama",
    "horror": "Terror",
    "sci-fi": "Ciencia Ficción",
    "science fiction": "Ciencia Ficción",
    "thriller": "Suspenso",
    "mystery": "Suspenso",
    "crime": "Suspenso",
}


def _normalizar_genero(nombre: str) -> str:
    """Quita acentos, espacios sobrantes y mayúsculas para comparar nombres de género."""
    sin_acentos = unicodedata.normalize("NFKD", str(nombre or ""))
    return "".join(
        letra for letra in sin_acentos if not unicodedata.combining(letra)
    ).strip().lower()


def mapear_generos_externos(
    nombres_externos: list[str], generos_disponibles: list[dict]
) -> tuple[list[int], list[str]]:
    """
    Traduce los géneros de OMDb a ids locales.
    Devuelve (ids_sugeridos, nombres_sin_equivalente). No falla si falta un género.
    """
    ids_por_nombre = {
        _normalizar_genero(genero.get("nombre")): genero.get("id_genero")
        for genero in generos_disponibles
        if isinstance(genero, dict)
    }
    ids_sugeridos = []
    sin_equivalente = []

    for nombre_externo in nombres_externos or []:
        clave = _normalizar_genero(nombre_externo)
        nombre_local = MAPEO_GENEROS_OMDB.get(clave) or nombre_externo
        id_genero = ids_por_nombre.get(_normalizar_genero(nombre_local))

        if id_genero is None:
            if nombre_externo not in sin_equivalente:
                sin_equivalente.append(nombre_externo)
            continue
        if id_genero not in ids_sugeridos:
            ids_sugeridos.append(id_genero)

    return ids_sugeridos, sin_equivalente


def agrupar_funciones(funciones: list[dict]) -> list[dict]:
    """
    Convierte la lista plana `funciones_vigentes` del detalle en:
    [{"nombre_local": ..., "fechas": [{"etiqueta": "Dom 15 Nov", "funciones": [...]}]}]
    Los complejos salen ordenados por nombre, y los días y las funciones por fecha de inicio.
    Se agrupa por nombre_local porque el endpoint no devuelve el id del local.
    """
    ordenadas = sorted(
        ((datetime.fromisoformat(f["inicio"]), f) for f in funciones),
        key=lambda par: par[0],
    )

    por_local = {}
    for inicio, funcion in ordenadas:
        dias = por_local.setdefault(funcion["nombre_local"], {})
        dias.setdefault(inicio.date(), []).append(
            {
                "id_funcion": funcion["id_funcion"],
                "hora": formatear_hora(inicio),
                "numero_sala": funcion["numero_sala"],
                "formato": funcion["formato"],
                "idioma": funcion["idioma"],
                "subtitulada": funcion["subtitulada"],
                "precio_entrada": funcion["precio_entrada"],
            }
        )

    return [
        {
            "nombre_local": nombre_local,
            "fechas": [
                {"etiqueta": formatear_fecha_corta(dia), "funciones": lista}
                for dia, lista in dias.items()
            ],
        }
        for nombre_local, dias in sorted(por_local.items())
    ]
