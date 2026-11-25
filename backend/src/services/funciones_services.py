from datetime import timedelta

from src.constants import DURACION_FUNCION_POR_DEFECTO_MIN, ESTADOS_FUNCION_NO_EDITABLES
from src.repositories.funciones_repository import (
    actualizar_funcion_db,
    buscar_funcion_por_id_db,
    buscar_pelicula_para_funcion_db,
    buscar_sala_para_funcion_db,
    cancelar_funcion_db,
    reactivar_funcion_db,
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


def _obtener_sala_activa(id_sala: int, id_local: int | None = None) -> dict:
    sala = buscar_sala_para_funcion_db(id_sala)
    if sala is None or not sala["activa"]:
        raise error_validacion("La sala indicada no existe o está deshabilitada.")
    if not sala["local_activo"]:
        raise error_validacion("El complejo de la sala indicada está deshabilitado.")
    if id_local is not None and sala["id_local"] != id_local:
        raise error_validacion("La sala indicada no pertenece al complejo seleccionado.")
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
    """Lista todas las funciones del ABM y marca las canceladas que pueden reactivarse."""
    sincronizar_estados_funciones_db()
    ahora = ahora_local()
    funciones = []
    for funcion in obtener_funciones_admin_db():
        datos = formatear_funcion(funcion)
        datos["puede_reactivar"] = (
            datos["estado"] == "CANCELADA" and funcion["inicio"] > ahora
        )
        funciones.append(datos)
    return funciones


def crear_funcion(datos: dict) -> dict:
    """Programa una función: fin = inicio + duración de la película, sin solapar la sala."""
    pelicula = _obtener_pelicula_activa(datos["id_pelicula"])
    _obtener_sala_activa(datos["id_sala"], datos.get("id_local"))
    fin = _calcular_fin(datos["inicio"], pelicula["duracion_min"])
    _verificar_sala_libre(datos["id_sala"], datos["inicio"], fin)

    id_funcion = insertar_funcion_db({**datos, "fin": fin})
    return formatear_funcion(buscar_funcion_por_id_db(id_funcion))


def actualizar_funcion(id_funcion: int, cambios: dict) -> dict:
    """Modifica película, sala, horario, formato, idioma, subtítulos, precio o estado."""
    actual = _obtener_funcion_o_404(id_funcion)
    if actual["estado"] in ESTADOS_FUNCION_NO_EDITABLES:
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

    if sala_cambio or "id_local" in cambios:
        _obtener_sala_activa(id_sala, cambios.get("id_local"))

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


def reactivar_funcion(id_funcion: int) -> dict:
    """Reactiva una función cancelada que aún no comenzó y mantiene su sala libre."""
    actual = _obtener_funcion_o_404(id_funcion)
    if actual["estado"] == "FINALIZADA":
        raise error_conflicto("No se puede reactivar una función finalizada.")
    if actual["estado"] != "CANCELADA":
        return {"mensaje": "La función ya se encuentra activa."}

    if actual["inicio"] <= ahora_local():
        raise error_conflicto(
            "No se puede reactivar una función que ya comenzó o finalizó."
        )

    _obtener_pelicula_activa(actual["id_pelicula"])
    _obtener_sala_activa(actual["id_sala"], actual["id_local"])
    if tiene_entradas_activas_db(id_funcion):
        raise error_conflicto(
            "No es posible reactivar una función con entradas vendidas o reservadas."
        )
    if hay_solapamiento_horario_db(
        actual["id_sala"], actual["inicio"], actual["fin"], id_funcion
    ):
        raise error_conflicto(
            "Otra función ocupa la sala en esa franja horaria; no se puede reactivar."
        )

    reactivar_funcion_db(id_funcion)
    return {"mensaje": "Función reactivada con éxito."}


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
