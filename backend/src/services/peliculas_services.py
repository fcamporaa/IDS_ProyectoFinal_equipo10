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
    asociar_genero_a_pelicula_db,
    quitar_genero_de_pelicula_db,
)
import requests

from src.constants import (
    OMDB_API_KEY,
    OMDB_URL,
    OMDB_TIMEOUT_SEGUNDOS,
    OMDB_ERRORES_SIN_RESULTADOS,
)
from src.utils import construir_error_api


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
    peliculas = obtener_cartelera_vigente_db(filtros)
    return _formatear_peliculas(peliculas)


def _crear_error(codigo: str, mensaje: str, descripcion: str, estado: int) -> ValueError:
    """Arma el ValueError con el payload de error estándar y el código HTTP."""
    return ValueError(construir_error_api(codigo, mensaje, descripcion), estado)


def _obtener_pelicula_o_404(id_pelicula: int) -> dict:
    """Devuelve la película (activa o no) o lanza el error 404 estándar si no existe."""
    pelicula = buscar_pelicula_por_id_db(id_pelicula)
    if pelicula is None:
        raise _crear_error(
            "error.recurso.no_encontrado",
            "Recurso no encontrado",
            f"No existe una película con id {id_pelicula}.",
            404,
        )
    return pelicula


def _formatear_funcion(funcion: dict) -> dict:
    """Deja la función con el formato del contrato: fechas ISO, precio numérico y booleano."""
    funcion["inicio"] = funcion["inicio"].isoformat()
    funcion["fin"] = funcion["fin"].isoformat()
    funcion["precio_entrada"] = float(funcion["precio_entrada"])
    funcion["subtitulada"] = bool(funcion["subtitulada"])
    return funcion


def obtener_detalle_pelicula(id_pelicula: int) -> dict:
    """Obtiene el detalle completo de una película y sus funciones vigentes."""
    pelicula = _formatear_peliculas([_obtener_pelicula_o_404(id_pelicula)])[0]
    funciones = obtener_funciones_vigentes_por_pelicula_db(id_pelicula)
    pelicula["funciones_vigentes"] = [_formatear_funcion(f) for f in funciones]
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
    raise _crear_error(
        "error.validacion.pelicula_duplicada", "Dato inválido", descripcion, 400
    )


def _verificar_generos_existentes(ids_generos: list[int]) -> None:
    """Lanza 400 si alguno de los ids de género no existe en la base."""
    existentes = {g["id_genero"] for g in obtener_generos_db()}
    faltantes = [i for i in ids_generos if i not in existentes]
    if faltantes:
        raise _crear_error(
            "error.validacion.generos_inexistentes",
            "Dato inválido",
            f"No existen los géneros con id: {faltantes}.",
            400,
        )


def crear_pelicula(datos: dict) -> dict:
    """Crea una nueva película y asocia sus géneros en BD."""
    _verificar_pelicula_no_duplicada(datos["origen_api"], datos["id_api"])
    _verificar_generos_existentes(datos["generos_ids"])

    id_pelicula = insertar_pelicula_db(datos)
    try:
        for id_genero in datos["generos_ids"]:
            asociar_genero_a_pelicula_db(id_pelicula, id_genero)
    except Exception:
        # db.py confirma cada sentencia por separado, así que la película ya quedó
        # guardada: se da de baja para que no circule incompleta (sin todos sus géneros).
        dar_de_baja_pelicula_db(id_pelicula)
        raise

    return _formatear_peliculas([_obtener_pelicula_o_404(id_pelicula)])[0]


def _reemplazar_generos(id_pelicula: int, ids_nuevos: list[int]) -> None:
    """
    Deja la película con exactamente los géneros indicados. Primero agrega los que
    faltan y recién después quita los que sobran: así nunca queda sin géneros, y
    repetir el pedido tras una falla completa lo que faltó.
    """
    filas = obtener_generos_de_peliculas_db([id_pelicula])
    ids_actuales = [fila["id_genero"] for fila in filas]

    for id_genero in ids_nuevos:
        if id_genero not in ids_actuales:
            asociar_genero_a_pelicula_db(id_pelicula, id_genero)
    for id_genero in ids_actuales:
        if id_genero not in ids_nuevos:
            quitar_genero_de_pelicula_db(id_pelicula, id_genero)


def actualizar_pelicula(id_pelicula: int, datos: dict) -> dict:
    """Actualiza datos de la película y devuelve la película ya modificada."""
    existente = _obtener_pelicula_o_404(id_pelicula)
    if "generos_ids" in datos:
        _verificar_generos_existentes(datos["generos_ids"])

    # actualizar_pelicula_db hace un UPDATE completo: se parte de lo ya guardado
    campos = {k: v for k, v in datos.items() if k != "generos_ids"}
    if campos:
        actualizar_pelicula_db(id_pelicula, {**existente, **campos})
    if "generos_ids" in datos:
        _reemplazar_generos(id_pelicula, datos["generos_ids"])

    return _formatear_peliculas([_obtener_pelicula_o_404(id_pelicula)])[0]


def eliminar_pelicula(id_pelicula: int) -> None:
    """Da de baja lógica una película de la cartelera (si ya estaba de baja, no hace nada)."""
    pelicula = _obtener_pelicula_o_404(id_pelicula)
    if pelicula["activa"]:
        dar_de_baja_pelicula_db(id_pelicula)


def _api_externa_no_disponible(descripcion: str) -> ValueError:
    """Arma el error 502 estándar para fallas de la API externa."""
    return _crear_error(
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
        raise _crear_error(
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
    return obtener_generos_db()



