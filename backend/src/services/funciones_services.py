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
    obtener_funciones_admin_db,
    obtener_funciones_db,
    sincronizar_estados_funciones_db,
    tiene_entradas_activas_db,
)
from src.utils import (
    ahora_local,
    error_conflicto,
    error_no_encontrado,
    error_validacion,
    formatear_funcion,
)


def _obtener_funcion_o_404(id_funcion: int) -> dict:
    funcion = buscar_funcion_por_id_db(id_funcion)
    if funcion is None:
        raise error_no_encontrado("La función seleccionada ya no está disponible.")
    return funcion


def _obtener_pelicula_activa(id_pelicula: int) -> dict:
    pelicula = buscar_pelicula_para_funcion_db(id_pelicula)
    if pelicula is None or not pelicula["activa"]:
        raise error_validacion("La película indicada no existe o está dada de baja.")
    return pelicula


def _obtener_sala_activa(id_sala: int) -> dict:
    sala = buscar_sala_para_funcion_db(id_sala)
    if sala is None or not sala["activa"]:
        raise error_validacion("La sala indicada no existe o está deshabilitada.")
    return sala


def _calcular_fin(inicio, duracion_min: int | None):
    duracion = duracion_min or DURACION_FUNCION_POR_DEFECTO_MIN
    return inicio + timedelta(minutes=duracion)


def _verificar_sala_libre(id_sala: int, inicio, fin, id_excluir: int | None = None) -> None:
    if hay_solapamiento_horario_db(id_sala, inicio, fin, id_excluir):
        raise error_conflicto("La sala ya tiene una función asignada en esa franja horaria.")


def listar_funciones(filtros: dict) -> list[dict]:
    """Lista las funciones vigentes aplicando los filtros ya validados."""
    sincronizar_estados_funciones_db()
    funciones = obtener_funciones_db({**filtros, "vigentes_desde": ahora_local()})
    return [formatear_funcion(funcion) for funcion in funciones]


def listar_funciones_admin() -> list[dict]:
    """Lista todas las funciones para el ABM, sin filtrar por estado ni vigencia."""
    sincronizar_estados_funciones_db()
    return [formatear_funcion(f) for f in obtener_funciones_admin_db()]


def crear_funcion(datos: dict) -> dict:
    """Programa una función: fin = inicio + duración de la película, sin solapar la sala."""
    pelicula = _obtener_pelicula_activa(datos["id_pelicula"])
    _obtener_sala_activa(datos["id_sala"])
    fin = _calcular_fin(datos["inicio"], pelicula["duracion_min"])
    _verificar_sala_libre(datos["id_sala"], datos["inicio"], fin)

    id_funcion = insertar_funcion_db({**datos, "fin": fin})
    return formatear_funcion(buscar_funcion_por_id_db(id_funcion))


def actualizar_funcion(id_funcion: int, cambios: dict) -> dict:
    """Modifica película, sala, horario, formato, idioma, subtítulos, precio o estado."""
    actual = _obtener_funcion_o_404(id_funcion)
    if actual["estado"] in ESTADOS_FUNCION_TERMINALES:
        raise error_conflicto(f"No se puede modificar una función {actual['estado']}.")

    id_pelicula = cambios.get("id_pelicula", actual["id_pelicula"])
    id_sala = cambios.get("id_sala", actual["id_sala"])
    inicio = cambios.get("inicio", actual["inicio"])
    formato = cambios.get("formato", actual["formato"])
    idioma = cambios.get("idioma", actual["idioma"])
    subtitulada = cambios.get("subtitulada", actual["subtitulada"])
    precio_entrada = cambios.get("precio_entrada", actual["precio_entrada"])
    estado = cambios.get("estado", actual["estado"])

    cambia_programacion = (
        id_pelicula != actual["id_pelicula"]
        or id_sala != actual["id_sala"]
        or inicio != actual["inicio"]
        or formato != actual["formato"]
        or idioma != actual["idioma"]
        or subtitulada != actual["subtitulada"]
    )
    cancela = estado == "CANCELADA" and actual["estado"] != "CANCELADA"

    if (cambia_programacion or cancela) and tiene_entradas_activas_db(id_funcion):
        raise error_conflicto("La función tiene entradas vendidas o reservadas.")

    fin = actual["fin"]
    pelicula_cambio = id_pelicula != actual["id_pelicula"]
    sala_cambio = id_sala != actual["id_sala"]
    inicio_cambio = inicio != actual["inicio"]

    if pelicula_cambio or inicio_cambio:
        pelicula = _obtener_pelicula_activa(id_pelicula)
        fin = (
            _calcular_fin(inicio, pelicula["duracion_min"])
            if pelicula_cambio
            else inicio + (actual["fin"] - actual["inicio"])
        )

    if sala_cambio:
        _obtener_sala_activa(id_sala)

    if cambia_programacion:
        _verificar_sala_libre(id_sala, inicio, fin, id_funcion)

    actualizar_funcion_db(
        id_funcion,
        {
            "id_pelicula": id_pelicula,
            "id_sala": id_sala,
            "inicio": inicio,
            "fin": fin,
            "formato": formato,
            "idioma": idioma,
            "subtitulada": subtitulada,
            "precio_entrada": precio_entrada,
            "estado": estado,
        },
    )
    return formatear_funcion(buscar_funcion_por_id_db(id_funcion))


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
    """Devuelve el mapa de butacas solo mientras la función siga disponible para compra."""
    funcion = _obtener_funcion_o_404(id_funcion)
    if funcion["estado"] != "PROGRAMADA" or funcion["inicio"] <= ahora_local():
        raise error_conflicto("La función ya comenzó y no permite comprar butacas.")
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
