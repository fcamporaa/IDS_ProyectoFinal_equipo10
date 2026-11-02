from src.constants import ORIGENES_API_PELICULAS
from src.utils import (
    ahora_local,
    error_validacion,
    es_entero,
    validar_booleano,
    validar_entero_en_rango,
    validar_entero_positivo,
    validar_objeto_json,
    validar_texto,
    validar_texto_opcional,
)

# Textos opcionales de una película y su largo máximo (según las columnas de la tabla)
TEXTOS_OPCIONALES_PELICULA = {
    "sinopsis": 10000,
    "poster_url": 1000,
    "trailer_url": 1000,
    "clasificacion": 20,
}


def _validar_generos_ids(valor) -> list[int]:
    """Valida la lista de ids de género: no vacía, enteros positivos, sin repetidos."""
    if not isinstance(valor, list) or not valor:
        raise error_validacion(
            "El campo generos_ids debe ser una lista con al menos un id de género."
        )
    if not all(es_entero(g) and g > 0 for g in valor):
        raise error_validacion(
            "El campo generos_ids debe contener solo enteros positivos."
        )
    return list(dict.fromkeys(valor))


def _validar_titulo(valor) -> str:
    """Valida el título: obligatorio, texto no vacío de hasta 250 caracteres."""
    if valor is None:
        raise error_validacion("El campo titulo es obligatorio.")
    return validar_texto(valor, "titulo", 250)


def _validar_duracion_min(valor) -> int:
    """Valida la duración: obligatoria, entero positivo (columna smallint)."""
    if valor is None:
        raise error_validacion("El campo duracion_min es obligatorio.")
    return validar_entero_en_rango(valor, "duracion_min", 1, 32767)


def _validar_anio_estreno(valor) -> int | None:
    """Valida el año de estreno (opcional): desde 1888 hasta el año actual + 5."""
    if valor is None:
        return None
    return validar_entero_en_rango(valor, "anio_estreno", 1888, ahora_local().year + 5)


def _validar_textos_opcionales(datos: dict) -> dict:
    """Valida los textos opcionales (sinopsis, URLs, clasificación) que vengan en el cuerpo."""
    return {
        nombre: validar_texto_opcional(datos[nombre], nombre, largo_max)
        for nombre, largo_max in TEXTOS_OPCIONALES_PELICULA.items()
        if nombre in datos
    }


def validar_id_pelicula(id_pelicula: int) -> int:
    """Valida que el id_pelicula sea un entero positivo."""
    return validar_entero_positivo(id_pelicula, "id")


def validar_filtros_cartelera(args) -> dict:
    """
    Valida los filtros opcionales de la cartelera pública:
    - id_genero: entero positivo
    - titulo: texto (máx. 250), búsqueda parcial
    - clasificacion: texto (máx. 20)
    Devuelve solo los filtros que vinieron con valor.
    """
    filtros = {}

    id_genero = (args.get("id_genero") or "").strip()
    if id_genero:
        filtros["id_genero"] = validar_entero_positivo(id_genero, "id_genero")

    for nombre, largo_max in (("titulo", 250), ("clasificacion", 20)):
        valor = validar_texto_opcional(args.get(nombre), nombre, largo_max)
        if valor:
            filtros[nombre] = valor

    return filtros


def validar_crear_pelicula(datos: dict) -> dict:
    """
    Valida el alta de una película.
    Obligatorios:
    - titulo: str no vacío (máx. 250)
    - origen_api: OMDB, TMDB o CUSTOM
    - id_api: str (máx. 50), obligatorio si origen_api no es CUSTOM
    - duracion_min: entero positivo
    - generos_ids: lista no vacía de ids de género
    Opcionales: sinopsis, poster_url, trailer_url, clasificacion, anio_estreno.
    Devuelve el diccionario normalizado con todos los campos.
    """
    datos = validar_objeto_json(datos)

    titulo = _validar_titulo(datos.get("titulo"))

    origen_api = datos.get("origen_api")
    if not isinstance(origen_api, str) or origen_api not in ORIGENES_API_PELICULAS:
        raise error_validacion(
            "El campo origen_api debe ser uno de: "
            f"{', '.join(sorted(ORIGENES_API_PELICULAS))}."
        )

    id_api = validar_texto_opcional(datos.get("id_api"), "id_api", 50)
    if origen_api != "CUSTOM" and id_api is None:
        raise error_validacion(
            "El campo id_api es obligatorio cuando origen_api no es CUSTOM."
        )

    pelicula = {nombre: None for nombre in TEXTOS_OPCIONALES_PELICULA}
    pelicula.update(_validar_textos_opcionales(datos))
    pelicula.update(
        {
            "titulo": titulo,
            "origen_api": origen_api,
            "id_api": id_api,
            "duracion_min": _validar_duracion_min(datos.get("duracion_min")),
            "anio_estreno": _validar_anio_estreno(datos.get("anio_estreno")),
            "generos_ids": _validar_generos_ids(datos.get("generos_ids")),
        }
    )
    return pelicula


def validar_actualizar_pelicula(datos: dict) -> dict:
    """
    Valida una modificación parcial de película. Todos los campos son opcionales
    pero debe venir al menos uno: titulo, duracion_min, anio_estreno, sinopsis,
    poster_url, trailer_url, clasificacion, activa (booleano) o generos_ids.
    Los campos desconocidos (por ejemplo origen_api o id_api) se ignoran.
    Devuelve solo los campos recibidos, ya validados.
    """
    datos = validar_objeto_json(datos)

    validados = _validar_textos_opcionales(datos)
    if "titulo" in datos:
        validados["titulo"] = _validar_titulo(datos["titulo"])
    if "duracion_min" in datos:
        validados["duracion_min"] = _validar_duracion_min(datos["duracion_min"])
    if "anio_estreno" in datos:
        validados["anio_estreno"] = _validar_anio_estreno(datos["anio_estreno"])
    if "activa" in datos:
        validados["activa"] = validar_booleano(datos["activa"], "activa")
    if "generos_ids" in datos:
        validados["generos_ids"] = _validar_generos_ids(datos["generos_ids"])

    if not validados:
        raise error_validacion(
            "No se envió ningún campo modificable: titulo, duracion_min, anio_estreno, "
            "sinopsis, poster_url, trailer_url, clasificacion, activa o generos_ids."
        )
    return validados


def validar_busqueda_externa(args) -> dict:
    """Valida el parámetro obligatorio 'query' (texto de hasta 100 caracteres) de la búsqueda externa."""
    query = validar_texto_opcional(args.get("query"), "query", 100)
    if query is None:
        raise error_validacion("El parámetro query es obligatorio.")
    return {"query": query}
