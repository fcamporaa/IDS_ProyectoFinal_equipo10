"""Utilidades de presentación y armado de formulario para funciones en el backoffice."""
from datetime import datetime

from utils.formatos import formatear_fecha_corta, formatear_hora, formatear_precio

ESTADOS_FUNCION_NO_EDITABLES = {"CANCELADA", "FINALIZADA"}


def combinar_salas(locales: list[dict], salas_por_local: dict) -> list[dict]:
    """Aplana las salas y les agrega el nombre del complejo para el select."""
    salas_totales = []
    for local in locales or []:
        id_local = local.get("id_local")
        nombre_local = local.get("nombre", "")
        salas = salas_por_local.get(id_local, [])
        if isinstance(salas, list):
            for sala in salas:
                s_copy = dict(sala)
                s_copy["id_local"] = id_local
                s_copy["nombre_local"] = nombre_local
                salas_totales.append(s_copy)
    return salas_totales


def preparar_funcion_para_tabla(funcion: dict) -> dict:
    """Agrega fecha, hora, precio legibles, clase de estado y permisos de acción."""
    f_copy = dict(funcion)
    estado = (f_copy.get("estado") or "PROGRAMADA").upper()
    f_copy["estado"] = estado
    f_copy["puede_editar"] = estado not in ESTADOS_FUNCION_NO_EDITABLES
    f_copy["puede_baja"] = estado not in ESTADOS_FUNCION_NO_EDITABLES
    f_copy["puede_reactivar"] = bool(funcion.get("puede_reactivar", False))

    inicio_raw = f_copy.get("inicio")
    fin_raw = f_copy.get("fin")

    if inicio_raw:
        try:
            dt_inicio = datetime.fromisoformat(inicio_raw)
            f_copy["fecha_legible"] = formatear_fecha_corta(dt_inicio.date())
            f_copy["hora_inicio"] = formatear_hora(dt_inicio)
        except (ValueError, TypeError):
            f_copy["fecha_legible"] = inicio_raw
            f_copy["hora_inicio"] = ""
    else:
        f_copy["fecha_legible"] = ""
        f_copy["hora_inicio"] = ""

    if fin_raw:
        try:
            dt_fin = datetime.fromisoformat(fin_raw)
            f_copy["hora_fin"] = formatear_hora(dt_fin)
        except (ValueError, TypeError):
            f_copy["hora_fin"] = fin_raw
    else:
        f_copy["hora_fin"] = ""

    precio = f_copy.get("precio_entrada")
    if precio is not None:
        try:
            f_copy["precio_legible"] = formatear_precio(float(precio))
        except (ValueError, TypeError):
            f_copy["precio_legible"] = str(precio)
    else:
        f_copy["precio_legible"] = ""

    return f_copy


def preparar_funciones_para_tabla(funciones: list[dict]) -> list[dict]:
    """Prepara una lista de funciones para la tabla del backoffice."""
    if not isinstance(funciones, list):
        return []
    return [preparar_funcion_para_tabla(f) for f in funciones]


def borrador_desde_funcion(funcion: dict) -> dict:
    """Convierte una función del backend en valores crudos para el formulario."""
    inicio_raw = funcion.get("inicio", "")
    fecha = ""
    hora = ""
    if inicio_raw:
        try:
            dt = datetime.fromisoformat(inicio_raw)
            fecha = dt.strftime("%Y-%m-%d")
            hora = dt.strftime("%H:%M")
        except (ValueError, TypeError):
            pass

    return {
        "id_pelicula": funcion.get("id_pelicula", ""),
        "id_sala": funcion.get("id_sala", ""),
        "id_local": funcion.get("id_local", ""),
        "fecha": fecha,
        "hora": hora,
        "formato": funcion.get("formato", "2D"),
        "idioma": funcion.get("idioma", "") or "",
        "subtitulada": bool(funcion.get("subtitulada", False)),
        "precio_entrada": funcion.get("precio_entrada", ""),
    }


def armar_inicio_iso(fecha: str, hora: str) -> str:
    """Valida fecha y hora del formulario y devuelve 'YYYY-MM-DDTHH:MM:SS'."""
    f = (fecha or "").strip()
    h = (hora or "").strip()
    if not f or not h:
        raise ValueError("La fecha y la hora de inicio son obligatorias.")

    if len(h.split(":")) == 2:
        h = h + ":00"

    try:
        dt_str = f"{f}T{h}"
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValueError("El formato de fecha u hora no es válido.") from None
