import requests

from src.constants import (
    OMDB_API_KEY,
    OMDB_URL,
    OMDB_TIMEOUT_SEGUNDOS,
    OMDB_ERRORES_SIN_RESULTADOS,
)
from src.repositories.peliculas_repository import (
    obtener_cartelera_vigente_db,
    buscar_pelicula_por_id_db,
    buscar_pelicula_por_api_db,
    obtener_funciones_vigentes_por_pelicula_db,
    insertar_pelicula_db,
    actualizar_pelicula_db,
    dar_de_baja_pelicula_db,
    obtener_generos_db,
    obtener_generos_de_peliculas_db,
)
from src.utils import (
    ahora_local,
    crear_error_http,
    error_no_encontrado,
    formatear_funcion,
)


def _formatear_peliculas(peliculas: list[dict]) -> list[dict]:
    """
    Deja cada película con el formato del contrato: `activa` como booleano
    y `generos` como lista de objetos {id_genero, nombre}.
    """
    generos_por_pelicula = {p["id_pelicula"]: [] for p in peliculas}
    for fila in obtener_generos_de_peliculas_db(list(generos_por_pelicula)):
        generos_por_pelicula[fila["id_pelicula"]].append(
            {"id_genero": fila["id_genero"], "nombre": fila["nombre"]}
        )

    for pelicula in peliculas:
        pelicula["activa"] = bool(pelicula["activa"])
        pelicula["generos"] = generos_por_pelicula[pelicula["id_pelicula"]]
    return peliculas


def listar_cartelera(filtros: dict) -> list[dict]:
    """Lista las películas actualmente en cartelera con sus géneros."""
    peliculas = obtener_cartelera_vigente_db({**filtros, "vigentes_desde": ahora_local()})
    return _formatear_peliculas(peliculas)


def _obtener_pelicula_o_404(id_pelicula: int) -> dict:
    """Devuelve la película (activa o no) o lanza el error 404 estándar si no existe."""
    pelicula = buscar_pelicula_por_id_db(id_pelicula)
    if pelicula is None:
        raise error_no_encontrado(f"No existe una película con id {id_pelicula}.")
    return pelicula


def obtener_detalle_pelicula(id_pelicula: int) -> dict:
    """Obtiene el detalle completo de una película y sus funciones vigentes."""
    pelicula = _formatear_peliculas([_obtener_pelicula_o_404(id_pelicula)])[0]
    funciones = obtener_funciones_vigentes_por_pelicula_db(id_pelicula, ahora_local())
    pelicula["funciones_vigentes"] = [formatear_funcion(f) for f in funciones]
    return pelicula


def _verificar_pelicula_no_duplicada(origen_api: str, id_api: str | None) -> None:
    """Lanza 400 si ya hay una película con ese origen externo e id (las CUSTOM no se comparan)."""
    if origen_api == "CUSTOM" or id_api is None:
        return
    existente = buscar_pelicula_por_api_db(origen_api, id_api)
    if existente is None:
        return

    id_existente = existente["id_pelicula"]
    descripcion = (
        f"Ya existe una película con origen_api {origen_api} "
        f"e id_api {id_api} (id {id_existente})."
    )
    if not existente["activa"]:
        descripcion += f" Está dada de baja: reactivala con PUT /peliculas/{id_existente}."
    raise crear_error_http(
        "error.validacion.pelicula_duplicada", "Dato inválido", descripcion, 400
    )


def _verificar_generos_existentes(ids_generos: list[int]) -> None:
    """Lanza 400 si alguno de los ids de género no existe en la base."""
    existentes = {g["id_genero"] for g in obtener_generos_db()}
    faltantes = [i for i in ids_generos if i not in existentes]
    if faltantes:
        raise crear_error_http(
            "error.validacion.generos_inexistentes",
            "Dato inválido",
            f"No existen los géneros con id: {faltantes}.",
            400,
        )


def crear_pelicula(datos: dict) -> dict:
    """Crea una nueva película y asocia sus géneros en BD."""
    _verificar_pelicula_no_duplicada(datos["origen_api"], datos["id_api"])
    _verificar_generos_existentes(datos["generos_ids"])

    id_pelicula = insertar_pelicula_db(datos, datos["generos_ids"])
    return _formatear_peliculas([_obtener_pelicula_o_404(id_pelicula)])[0]


def actualizar_pelicula(id_pelicula: int, datos: dict) -> dict:
    """Actualiza datos de la película y devuelve la película ya modificada."""
    existente = _obtener_pelicula_o_404(id_pelicula)
    ids_generos = datos.get("generos_ids")
    if ids_generos is not None:
        _verificar_generos_existentes(ids_generos)

    # actualizar_pelicula_db hace un UPDATE completo: se parte de lo ya guardado
    campos = {k: v for k, v in datos.items() if k != "generos_ids"}
    actualizar_pelicula_db(id_pelicula, {**existente, **campos}, ids_generos)

    return _formatear_peliculas([_obtener_pelicula_o_404(id_pelicula)])[0]


def eliminar_pelicula(id_pelicula: int) -> None:
    """Da de baja lógica una película de la cartelera (si ya estaba de baja, no hace nada)."""
    pelicula = _obtener_pelicula_o_404(id_pelicula)
    if pelicula["activa"]:
        dar_de_baja_pelicula_db(id_pelicula)


def _api_externa_no_disponible(descripcion: str) -> ValueError:
    """Arma el error 502 estándar para fallas de la API externa."""
    return crear_error_http(
        "error.externo.api_no_disponible",
        "Servicio externo no disponible",
        descripcion,
        502,
    )


def _formatear_resultado_externo(item: dict) -> dict:
    """Pasa un resultado de OMDb (Title, Year, imdbID, Poster) al formato del contrato."""
    anio = str(item.get("Year", ""))[:4]
    poster = item.get("Poster")
    return {
        "id_api": item["imdbID"],
        "titulo": item["Title"],
        "anio": int(anio) if anio.isdigit() else None,
        "poster": None if poster in (None, "N/A") else poster,
        "origen": "OMDB",
    }


def buscar_peliculas_externas(filtros: dict) -> list[dict]:
    """Consulta la API externa (OMDb) por título y devuelve los resultados con el formato del contrato."""
    if not OMDB_API_KEY:
        raise crear_error_http(
            "error.configuracion.api_externa",
            "Configuración incompleta",
            "Falta configurar OMDB_API_KEY en el servidor.",
            500,
        )

    parametros = {"apikey": OMDB_API_KEY, "s": filtros["query"], "type": "movie"}
    try:
        datos = requests.get(OMDB_URL, params=parametros, timeout=OMDB_TIMEOUT_SEGUNDOS).json()
    except (requests.RequestException, ValueError):
        datos = None
    if not isinstance(datos, dict):
        raise _api_externa_no_disponible("No se pudo obtener una respuesta válida de OMDb.")

    if datos.get("Response") != "True":
        error = datos.get("Error")
        if error in OMDB_ERRORES_SIN_RESULTADOS:
            return []
        raise _api_externa_no_disponible(f"OMDb respondió con un error: {error}")

    return [
        _formatear_resultado_externo(item)
        for item in datos.get("Search", [])
        if item.get("imdbID") and item.get("Title")
    ]


def listar_generos() -> list[dict]:
    """Devuelve el listado de todos los géneros disponibles."""
    pass


def listar_resenas_pelicula(id_pelicula: int) -> list[dict]:
    """Lista las reseñas y puntuaciones de una película."""
    pass


def crear_resena_pelicula(id_pelicula: int, id_usuario: int, datos: dict) -> dict:
    """
    Registra una reseña validando que el usuario tenga una compra
    con QR validado efectivamente en puerta.
    """
    pass
