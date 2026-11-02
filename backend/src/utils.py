import urllib.parse
import datetime

def construir_error_api(
    code: str, message: str, description: str, level: str = "error"
) -> dict:
    """Construye un payload de error estándar compatible con la API."""
    return {
        "errors": [
            {
                "code": code,
                "message": message,
                "level": level,
                "description": description,
            }
        ]
    }


def construir_links_hateoas(
    base_url: str,
    query_params: dict,
    limit: int,
    offset: int,
    total_registros: int,
) -> dict:
    """Construye los enlaces HATEOAS (_first, _prev, _next, _last)."""
    params_base = {
        k: v for k, v in query_params.items() if k not in ("_limit", "_offset")
    }

    def _crear_url(l, o):
        qp = params_base.copy()
        qp["_limit"] = l
        qp["_offset"] = o
        return f"{base_url}?{urllib.parse.urlencode(qp)}"

    ultimo_offset = (
        max(0, ((total_registros - 1) // limit) * limit)
        if total_registros > 0
        else 0
    )
    prev_offset = max(0, offset - limit)
    next_offset = min(ultimo_offset, offset + limit)

    return {
        "_first": {"href": _crear_url(limit, 0)},
        "_prev": {"href": _crear_url(limit, prev_offset)},
        "_next": {"href": _crear_url(limit, next_offset)},
        "_last": {"href": _crear_url(limit, ultimo_offset)},
    }


#Evito tener funciones sueltas en [los validators y repository de [Peliculas]. Como son genéricas y se repiten, las dejó en utils
# ==========================================
# Errores de negocio (ValueError con payload estándar y código HTTP)
# ==========================================
def crear_error_http(codigo: str, mensaje: str, descripcion: str, estado: int) -> ValueError:
    """Arma el ValueError que app.py convierte en respuesta JSON con ese código HTTP."""
    return ValueError(construir_error_api(codigo, mensaje, descripcion), estado)


def error_validacion(descripcion: str) -> ValueError:
    """Error 400 estándar de validación de datos de entrada."""
    return crear_error_http(
        "error.validacion.parametro", "Dato inválido", descripcion, 400
    )


def error_no_encontrado(descripcion: str) -> ValueError:
    """Error 404 estándar para un recurso inexistente."""
    return crear_error_http(
        "error.recurso.no_encontrado", "Recurso no encontrado", descripcion, 404
    )


# ==========================================
# Validaciones genéricas de datos de entrada
# ==========================================
def validar_objeto_json(datos) -> dict:
    """Lanza 400 si el cuerpo de la petición no es un objeto JSON."""
    if not isinstance(datos, dict):
        raise error_validacion("El cuerpo de la petición debe ser un objeto JSON.")
    return datos


def es_entero(valor) -> bool:
    """True si es un entero real (en JSON, true/false llegan como bool y no cuentan)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def validar_entero_positivo(valor, nombre: str) -> int:
    """Valida un entero positivo; acepta también texto numérico (query params)."""
    if isinstance(valor, str):
        valor = valor.strip()
        if valor.isascii() and valor.isdigit():
            valor = int(valor)
    if not es_entero(valor) or valor <= 0:
        raise error_validacion(f"El campo {nombre} debe ser un entero positivo.")
    return valor


def validar_entero_en_rango(valor, nombre: str, minimo: int, maximo: int) -> int:
    """Valida un entero dentro de un rango inclusivo."""
    if not es_entero(valor) or not minimo <= valor <= maximo:
        raise error_validacion(
            f"El campo {nombre} debe ser un entero entre {minimo} y {maximo}."
        )
    return valor


def validar_texto(valor, nombre: str, largo_max: int) -> str:
    """Valida un texto no vacío, sin espacios sobrantes y de hasta largo_max caracteres."""
    if not isinstance(valor, str):
        raise error_validacion(f"El campo {nombre} debe ser texto.")
    valor = valor.strip()
    if not valor:
        raise error_validacion(f"El campo {nombre} no puede estar vacío.")
    if len(valor) > largo_max:
        raise error_validacion(
            f"El campo {nombre} no puede superar los {largo_max} caracteres."
        )
    return valor


def validar_texto_opcional(valor, nombre: str, largo_max: int) -> str | None:
    """Como validar_texto, pero None o texto vacío devuelven None."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None
    return validar_texto(valor, nombre, largo_max)


def validar_booleano(valor, nombre: str) -> bool:
    """Valida que el valor sea true o false."""
    if not isinstance(valor, bool):
        raise error_validacion(f"El campo {nombre} debe ser true o false.")
    return valor


# ==========================================
# Fechas y horas
# ==========================================
def ahora_local() -> datetime:
    """Hora actual en la zona local, sin tzinfo para comparar con columnas DATETIME."""
    return datetime.now(ZONA_HORARIA_LOCAL).replace(tzinfo=None)


def formatear_datetime_iso(valor: datetime) -> str:
    """Formatea un DATETIME como ISO 8601 sin zona (ej. 2026-11-15T20:00:00), según el swagger."""
    return valor.isoformat()


# ==========================================
# Formato de respuestas (contrato del swagger)
# ==========================================
def formatear_funcion(funcion: dict) -> dict:
    """Adapta una fila de funciones (datetime, Decimal, tinyint) al contrato del swagger."""
    return {
        **funcion,
        "inicio": formatear_datetime_iso(funcion["inicio"]),
        "fin": formatear_datetime_iso(funcion["fin"]),
        "precio_entrada": float(funcion["precio_entrada"]),
        "subtitulada": bool(funcion["subtitulada"]),
    }

