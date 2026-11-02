from datetime import datetime

CAMPOS_FILTRO_PERMITIDOS = {"desde", "hasta", "id_local"}
FORMATO_FECHA = "%Y-%m-%d"


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
