from datetime import timedelta

from src.constants import DURACION_FUNCION_POR_DEFECTO_MIN, ESTADOS_FUNCION_TERMINALES
from src.repositories.funciones_repository import (
    actualizar_funcion_db,
    buscar_funcion_por_id_db,
    buscar_pelicula_para_funcion_db,
    buscar_sala_para_funcion_db,
    cancelar_funcion_db,
    hay_solapamiento_horario_db,
    insertar_funcion_db,
    obtener_estado_butacas_funcion_db,
    obtener_funciones_db,
    tiene_entradas_activas_db,
)
from src.utils import (
    ahora_local,
    error_conflicto,
    error_no_encontrado,
    error_validacion,
    formatear_datetime_iso,
)


def _formatear_funcion(fila: dict) -> dict:
    """Adapta tipos de MySQL (datetime, Decimal, tinyint) al contrato del swagger."""
    return {
        **fila,
        "inicio": formatear_datetime_iso(fila["inicio"]),
        "fin": formatear_datetime_iso(fila["fin"]),
        "precio_entrada": float(fila["precio_entrada"]),
        "subtitulada": bool(fila["subtitulada"]),
    }


def _obtener_funcion_o_404(id_funcion: int) -> dict:
    funcion = buscar_funcion_por_id_db(id_funcion)
    if funcion is None:
        raise error_no_encontrado(f"No existe la función con id {id_funcion}.")
    return funcion


def _verificar_sala_libre(id_sala: int, inicio, fin, id_excluir: int | None = None) -> None:
    if hay_solapamiento_horario_db(id_sala, inicio, fin, id_excluir):
        raise error_conflicto("La sala ya tiene una función asignada en esa franja horaria.")


def listar_funciones(filtros: dict) -> list[dict]:
    """Lista las funciones vigentes aplicando los filtros ya validados."""
    funciones = obtener_funciones_db({**filtros, "vigentes_desde": ahora_local()})
    return [_formatear_funcion(funcion) for funcion in funciones]


def crear_funcion(datos: dict) -> dict:
    """Programa una función: fin = inicio + duración de la película, sin solapar la sala."""
    pelicula = buscar_pelicula_para_funcion_db(datos["id_pelicula"])
    if pelicula is None or not pelicula["activa"]:
        raise error_validacion("La película indicada no existe o está dada de baja.")
    sala = buscar_sala_para_funcion_db(datos["id_sala"])
    if sala is None or not sala["activa"]:
        raise error_validacion("La sala indicada no existe o está deshabilitada.")

    duracion_min = pelicula["duracion_min"] or DURACION_FUNCION_POR_DEFECTO_MIN
    fin = datos["inicio"] + timedelta(minutes=duracion_min)
    _verificar_sala_libre(datos["id_sala"], datos["inicio"], fin)

    id_funcion = insertar_funcion_db({**datos, "fin": fin})
    return _formatear_funcion(buscar_funcion_por_id_db(id_funcion))


def actualizar_funcion(id_funcion: int, cambios: dict) -> dict:
    """Modifica inicio, precio o estado conservando los datos no enviados."""
    actual = _obtener_funcion_o_404(id_funcion)
    if actual["estado"] in ESTADOS_FUNCION_TERMINALES:
        raise error_conflicto(f"No se puede modificar una función {actual['estado']}.")

    cancela = cambios.get("estado") == "CANCELADA"
    mueve_horario = "inicio" in cambios and cambios["inicio"] != actual["inicio"]
    if (cancela or mueve_horario) and tiene_entradas_activas_db(id_funcion):
        raise error_conflicto("La función tiene entradas vendidas o reservadas.")

    inicio = cambios.get("inicio", actual["inicio"])
    fin = actual["fin"]
    if mueve_horario:
        fin = inicio + (actual["fin"] - actual["inicio"])
        _verificar_sala_libre(actual["id_sala"], inicio, fin, id_funcion)

    actualizar_funcion_db(
        id_funcion,
        {
            "inicio": inicio,
            "fin": fin,
            "precio_entrada": cambios.get("precio_entrada", actual["precio_entrada"]),
            "estado": cambios.get("estado", actual["estado"]),
        },
    )
    return _formatear_funcion(buscar_funcion_por_id_db(id_funcion))


def eliminar_funcion(id_funcion: int) -> dict:
    """Cancela la función si no tiene entradas activas. Repetir la baja no falla."""
    funcion = _obtener_funcion_o_404(id_funcion)
    if funcion["estado"] != "CANCELADA":
        if funcion["estado"] == "FINALIZADA":
            raise error_validacion("No es posible dar de baja una función finalizada.")
        if tiene_entradas_activas_db(id_funcion):
            raise error_validacion(
                "No es posible dar de baja una función con entradas ya vendidas."
            )
        cancelar_funcion_db(id_funcion)
    return {"mensaje": "Función dada de baja con éxito."}


def obtener_mapa_butacas_funcion(id_funcion: int) -> dict:
    """Devuelve el mapa de butacas de la sala con totales de libres y ocupadas."""
    funcion = _obtener_funcion_o_404(id_funcion)
    butacas = obtener_estado_butacas_funcion_db(id_funcion)
    libres = sum(1 for butaca in butacas if butaca["estado"] == "DISPONIBLE")
    return {
        "id_funcion": id_funcion,
        "id_sala": funcion["id_sala"],
        "total_butacas": len(butacas),
        "libres": libres,
        "ocupadas": len(butacas) - libres,
        "butacas": butacas,
    }
