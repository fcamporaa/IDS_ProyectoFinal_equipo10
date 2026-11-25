from datetime import datetime

from utils.validaciones import validar_entero_positivo, validar_texto_maximo

CAMPOS_FILTRO_PERMITIDOS = {"desde", "hasta", "id_local"}
FORMATO_FECHA = "%Y-%m-%d"
LARGO_MAX_TITULO = 250
LARGO_MAX_CLASIFICACION = 20


def _validar_fecha(valor: str, nombre: str) -> str:
    try:
        datetime.strptime(valor, FORMATO_FECHA)
    except ValueError:
        raise ValueError(
            f"El filtro '{nombre}' debe tener el formato YYYY-MM-DD."
        ) from None
    return valor


def validar_filtros_dashboard(args) -> dict:
    """Valida y normaliza los filtros enviados desde el formulario del dashboard."""
    campos_desconocidos = set(args.keys()) - CAMPOS_FILTRO_PERMITIDOS
    if campos_desconocidos:
        raise ValueError(
            "Los filtros no permitidos son: "
            f"{', '.join(sorted(campos_desconocidos))}."
        )

    filtros = {}
    if args.get("desde", "").strip():
        filtros["desde"] = _validar_fecha(args["desde"].strip(), "desde")
    if args.get("hasta", "").strip():
        filtros["hasta"] = _validar_fecha(args["hasta"].strip(), "hasta")

    if "desde" in filtros and "hasta" in filtros:
        if filtros["desde"] > filtros["hasta"]:
            raise ValueError("'Desde' no puede ser posterior a 'Hasta'.")

    if args.get("id_local", "").strip():
        id_local = args["id_local"].strip()
        if not id_local.isascii() or not id_local.isdigit() or int(id_local) <= 0:
            raise ValueError("El filtro 'Complejo' debe ser un número válido.")
        filtros["id_local"] = int(id_local)

    return filtros


def validar_filtros_cartelera(args) -> dict:
    """
    Valida los filtros de la cartelera (id_genero, titulo y clasificacion) y devuelve
    solo los que vinieron con valor. Cualquier otro parámetro de la URL se ignora:
    el diccionario se arma solo con las claves conocidas, así nada extra llega al backend.
    """
    filtros = {}

    id_genero = args.get("id_genero", "")
    if id_genero.strip():
        filtros["id_genero"] = validar_entero_positivo(id_genero, "Género")

    titulo = validar_texto_maximo(args.get("titulo", ""), "Título", LARGO_MAX_TITULO)
    if titulo:
        filtros["titulo"] = titulo

    clasificacion = validar_texto_maximo(
        args.get("clasificacion", ""), "Clasificación", LARGO_MAX_CLASIFICACION
    )
    if clasificacion:
        filtros["clasificacion"] = clasificacion

    return filtros
