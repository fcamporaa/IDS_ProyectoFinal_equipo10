from datetime import date, datetime

from src.constants import FORMATO_FECHA_CORTO
from src.utils import error_validacion, validar_entero_positivo


CAMPOS_FILTRO_PERMITIDOS = {"desde", "hasta", "id_local"}


def _validar_fecha(valor: str, nombre: str) -> date:
    """Valida una fecha de filtro con el formato YYYY-MM-DD."""
    try:
        return datetime.strptime(valor, FORMATO_FECHA_CORTO).date()
    except (TypeError, ValueError):
        raise error_validacion(
            f"El campo '{nombre}' debe tener el formato YYYY-MM-DD."
        ) from None


def validar_filtros_dashboard(args) -> dict:
    """
    Valida los filtros comunes de los reportes del dashboard:
    - desde: fecha YYYY-MM-DD (opcional)
    - hasta: fecha YYYY-MM-DD (opcional)
    - id_local: entero positivo (opcional)
    """
    campos_desconocidos = set(args.keys()) - CAMPOS_FILTRO_PERMITIDOS
    if campos_desconocidos:
        raise error_validacion(
            "Los filtros no permitidos son: "
            f"{', '.join(sorted(campos_desconocidos))}."
        )

    filtros = {}
    if args.get("desde", "").strip():
        filtros["desde"] = _validar_fecha(args["desde"].strip(), "desde")
    if args.get("hasta", "").strip():
        filtros["hasta"] = _validar_fecha(args["hasta"].strip(), "hasta")
    if args.get("id_local", "").strip():
        filtros["id_local"] = validar_entero_positivo(
            args["id_local"].strip(), "id_local"
        )

    if (
        "desde" in filtros
        and "hasta" in filtros
        and filtros["desde"] > filtros["hasta"]
    ):
        raise error_validacion(
            "El campo 'desde' no puede ser posterior al campo 'hasta'."
        )

    return {
        clave: valor.isoformat() if hasattr(valor, "isoformat") else valor
        for clave, valor in filtros.items()
    }
