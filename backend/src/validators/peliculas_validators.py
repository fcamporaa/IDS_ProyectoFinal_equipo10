from datetime import datetime

from src.constants import ORIGENES_API_PELICULAS
from src.utils import construir_error_api


def _error_validacion(descripcion: str) -> ValueError:
    """Arma el ValueError (400) con el payload de error estándar de validación."""
    return ValueError(
        construir_error_api(
            "error.validacion.parametro", "Dato inválido", descripcion
        ),
        400,
    )


def _texto_filtro(args, nombre: str, largo_max: int) -> str | None:
    """Devuelve el parámetro de texto sin espacios sobrantes, o None si no vino o está vacío."""
    valor = (args.get(nombre) or "").strip()
    if not valor:
        return None
    if len(valor) > largo_max:
        raise _error_validacion(
            f"El parámetro {nombre} no puede superar los {largo_max} caracteres."
        )
    return valor


def _es_entero(valor) -> bool:
    """True si es un entero real (en JSON, true/false llegan como bool y no cuentan)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def _validar_texto_campo(valor, nombre: str, largo_max: int) -> str | None:
    """Valida un texto del cuerpo: sin espacios sobrantes; vacío o null devuelve None."""
    if valor is None:
        return None
    if not isinstance(valor, str):
        raise _error_validacion(f"El campo {nombre} debe ser texto.")
    valor = valor.strip()
    if len(valor) > largo_max:
        raise _error_validacion(
            f"El campo {nombre} no puede superar los {largo_max} caracteres."
        )
    return valor or None


def _validar_entero_campo(valor, nombre: str, minimo: int, maximo: int) -> int:
    """Valida un entero del cuerpo dentro de un rango."""
    if not _es_entero(valor) or not minimo <= valor <= maximo:
        raise _error_validacion(
            f"El campo {nombre} debe ser un entero entre {minimo} y {maximo}."
        )
    return valor


def _validar_generos_ids(valor) -> list[int]:
    """Valida la lista de ids de género: no vacía, enteros positivos, sin repetidos."""
    if not isinstance(valor, list) or not valor:
        raise _error_validacion(
            "El campo generos_ids debe ser una lista con al menos un id de género."
        )
    if not all(_es_entero(g) and g > 0 for g in valor):
        raise _error_validacion(
            "El campo generos_ids debe contener solo enteros positivos."
        )
    return list(dict.fromkeys(valor))


# Textos opcionales de una película y su largo máximo (según las columnas de la tabla)
TEXTOS_OPCIONALES_PELICULA = {
    "sinopsis": 10000,
    "poster_url": 1000,
    "trailer_url": 1000,
    "clasificacion": 20,
}


def _exigir_cuerpo_objeto(datos) -> None:
    """Lanza 400 si el cuerpo de la petición no es un objeto JSON."""
    if not isinstance(datos, dict):
        raise _error_validacion("El cuerpo de la petición debe ser un objeto JSON.")


def _validar_titulo(valor) -> str:
    """Valida el título: texto no vacío de hasta 250 caracteres."""
    titulo = _validar_texto_campo(valor, "titulo", 250)
    if titulo is None:
        raise _error_validacion("El campo titulo es obligatorio y no puede estar vacío.")
    return titulo


def _validar_duracion_min(valor) -> int:
    """Valida la duración: entero positivo (columna smallint)."""
    if valor is None:
        raise _error_validacion("El campo duracion_min es obligatorio.")
    return _validar_entero_campo(valor, "duracion_min", 1, 32767)


def _validar_anio_estreno(valor) -> int | None:
    """Valida el año de estreno (opcional): desde 1888 hasta el año actual + 5."""
    if valor is None:
        return None
    return _validar_entero_campo(valor, "anio_estreno", 1888, datetime.now().year + 5)


def _validar_textos_opcionales(datos: dict) -> dict:
    """Valida los textos opcionales (sinopsis, URLs, clasificación) que vengan en el cuerpo."""
    return {
        nombre: _validar_texto_campo(datos[nombre], nombre, largo_max)
        for nombre, largo_max in TEXTOS_OPCIONALES_PELICULA.items()
        if nombre in datos
    }


def validar_id_pelicula(id_pelicula: int) -> int:
    """Valida que el id_pelicula sea un entero positivo."""
    if not isinstance(id_pelicula, int) or id_pelicula <= 0:
        raise _error_validacion("El parámetro id debe ser un entero positivo.")
    return id_pelicula


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
        if not (id_genero.isascii() and id_genero.isdigit()) or int(id_genero) <= 0:
            raise _error_validacion("El parámetro id_genero debe ser un entero positivo.")
        filtros["id_genero"] = int(id_genero)

    for nombre, largo_max in (("titulo", 250), ("clasificacion", 20)):
        valor = _texto_filtro(args, nombre, largo_max)
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
    _exigir_cuerpo_objeto(datos)

    titulo = _validar_titulo(datos.get("titulo"))

    origen_api = datos.get("origen_api")
    if not isinstance(origen_api, str) or origen_api not in ORIGENES_API_PELICULAS:
        raise _error_validacion(
            "El campo origen_api debe ser uno de: "
            f"{', '.join(sorted(ORIGENES_API_PELICULAS))}."
        )

    id_api = _validar_texto_campo(datos.get("id_api"), "id_api", 50)
    if origen_api != "CUSTOM" and id_api is None:
        raise _error_validacion(
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
    _exigir_cuerpo_objeto(datos)

    validados = _validar_textos_opcionales(datos)
    if "titulo" in datos:
        validados["titulo"] = _validar_titulo(datos["titulo"])
    if "duracion_min" in datos:
        validados["duracion_min"] = _validar_duracion_min(datos["duracion_min"])
    if "anio_estreno" in datos:
        validados["anio_estreno"] = _validar_anio_estreno(datos["anio_estreno"])
    if "activa" in datos:
        if not isinstance(datos["activa"], bool):
            raise _error_validacion("El campo activa debe ser true o false.")
        validados["activa"] = datos["activa"]
    if "generos_ids" in datos:
        validados["generos_ids"] = _validar_generos_ids(datos["generos_ids"])

    if not validados:
        raise _error_validacion(
            "No se envió ningún campo modificable: titulo, duracion_min, anio_estreno, "
            "sinopsis, poster_url, trailer_url, clasificacion, activa o generos_ids."
        )
    return validados


def validar_busqueda_externa(args) -> dict:
    """Valida el parámetro obligatorio 'query' (texto de hasta 100 caracteres) de la búsqueda externa."""
    query = _texto_filtro(args, "query", 100)
    if query is None:
        raise _error_validacion("El parámetro query es obligatorio.")
    return {"query": query}


