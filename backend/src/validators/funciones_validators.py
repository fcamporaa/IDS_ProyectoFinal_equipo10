from datetime import datetime

from src.constants import ESTADOS_FUNCION, FORMATO_FECHA_CORTO, FORMATOS_SALA
from src.utils import (
    ahora_local,
    error_validacion,
    parsear_datetime,
    validar_booleano,
    validar_decimal_positivo,
    validar_entero_positivo,
    validar_objeto_json,
    validar_opcion,
    validar_texto,
)


def validar_id_funcion(id_funcion) -> int:
    """Valida que id_funcion sea un entero positivo."""
    return validar_entero_positivo(id_funcion, "id")


def validar_filtros_funciones(args) -> dict:
    """Valida los query params de GET /funciones (id_pelicula, id_local, fecha, formato)."""
    filtros = {}
    if "id_pelicula" in args:
        filtros["id_pelicula"] = validar_entero_positivo(args["id_pelicula"], "id_pelicula")
    if "id_local" in args:
        filtros["id_local"] = validar_entero_positivo(args["id_local"], "id_local")
    if "formato" in args:
        filtros["formato"] = validar_opcion(args["formato"], FORMATOS_SALA, "formato")
    if "fecha" in args:
        try:
            filtros["fecha"] = datetime.strptime(args["fecha"], FORMATO_FECHA_CORTO).date()
        except ValueError:
            raise error_validacion("El campo fecha debe respetar el formato YYYY-MM-DD.")
    return filtros


def _validar_inicio_futuro(valor) -> datetime:
    inicio = parsear_datetime(valor, "inicio")
    if inicio <= ahora_local():
        raise error_validacion("El campo inicio debe ser una fecha y hora futura.")
    return inicio


def validar_crear_funcion(datos) -> dict:
    """Valida el body de POST /funciones y devuelve los datos ya normalizados."""
    datos = validar_objeto_json(datos)
    obligatorios = ("id_pelicula", "id_sala", "inicio", "formato", "precio_entrada")
    faltantes = [campo for campo in obligatorios if campo not in datos]
    if faltantes:
        raise error_validacion(f"Faltan campos obligatorios: {', '.join(faltantes)}.")

    idioma = datos.get("idioma")
    return {
        "id_pelicula": validar_entero_positivo(datos["id_pelicula"], "id_pelicula"),
        "id_sala": validar_entero_positivo(datos["id_sala"], "id_sala"),
        "inicio": _validar_inicio_futuro(datos["inicio"]),
        "formato": validar_opcion(datos["formato"], FORMATOS_SALA, "formato"),
        "idioma": None if idioma is None else validar_texto(idioma, "idioma", 50),
        "subtitulada": validar_booleano(datos.get("subtitulada", False), "subtitulada"),
        "precio_entrada": validar_decimal_positivo(datos["precio_entrada"], "precio_entrada"),
    }


def validar_actualizar_funcion(datos) -> dict:
    """Valida el body de PUT /funciones/{id}; devuelve solo los campos enviados."""
    datos = validar_objeto_json(datos)
    cambios = {}
    if "inicio" in datos:
        cambios["inicio"] = _validar_inicio_futuro(datos["inicio"])
    if "precio_entrada" in datos:
        cambios["precio_entrada"] = validar_decimal_positivo(
            datos["precio_entrada"], "precio_entrada"
        )
    if "estado" in datos:
        cambios["estado"] = validar_opcion(datos["estado"], ESTADOS_FUNCION, "estado")
    if not cambios:
        raise error_validacion("Debe enviar al menos uno de: inicio, precio_entrada, estado.")
    return cambios
