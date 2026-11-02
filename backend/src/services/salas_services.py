from src.repositories.salas_repository import (
    obtener_locales_db,
    buscar_local_por_id_db,
    obtener_salas_por_local_db,
    buscar_sala_por_id_db,
    obtener_butacas_por_sala_db,
    actualizar_sala_db,
)
from src.utils import construir_error_api


def _error_no_encontrado(mensaje: str) -> ValueError:
    """Helper para lanzar error 404."""
    return ValueError(
        construir_error_api("error.recurso.no_encontrado", "Recurso no encontrado", mensaje),
        404,
    )


def listar_locales() -> list[dict]:
    """Lista los locales de cine disponibles."""
    locales = obtener_locales_db()
    return [
        {
            "id_local": l["id_local"],
            "nombre": l["nombre"],
            "direccion": l["direccion"],
            "activo": bool(l["activo"]),
        }
        for l in locales
    ]


def listar_salas_por_local(id_local: int) -> list[dict]:
    """Lista las salas de un complejo y su capacidad total."""
    # Verificar que el local exista
    local = buscar_local_por_id_db(id_local)
    if not local:
        raise _error_no_encontrado(f"No existe el complejo con ID {id_local}.")

    # Traer las salas del local con su capacidad calculada
    salas = obtener_salas_por_local_db(id_local)
    return [
        {
            "id_sala": s["id_sala"],
            "id_local": s["id_local"],
            "numero": s["numero"],
            "capacidad": int(s["capacidad"] or 0),
            "activa": bool(s["activa"]),
        }
        for s in salas
    ]


def obtener_detalle_sala(id_sala: int) -> dict:
    """Obtiene la sala y la grilla o distribución física de sus butacas."""
    # Verificar que la sala exista
    sala = buscar_sala_por_id_db(id_sala)
    if not sala:
        raise _error_no_encontrado(f"No existe la sala con ID {id_sala}.")

    # Obtener la distribución de butacas
    butacas_db = obtener_butacas_por_sala_db(id_sala)
    butacas = [
        {
            "id_butaca": b["id_butaca"],
            "id_sala": b["id_sala"],
            "fila": b["fila"],
            "numero": b["numero"],
            "activa": bool(b["activa"]),
        }
        for b in butacas_db
    ]

    return {
        "id_sala": sala["id_sala"],
        "id_local": sala["id_local"],
        "numero": sala["numero"],
        "capacidad": int(sala["capacidad"] or 0),
        "activa": bool(sala["activa"]),
        "butacas": butacas,
    }


def actualizar_configuracion_sala(id_sala: int, datos: dict) -> dict:
    """Actualiza configuración de la sala (activa / inactiva)."""
    # Verificar que la sala exista antes de actualizar
    sala = buscar_sala_por_id_db(id_sala)
    if not sala:
        raise _error_no_encontrado(f"No existe la sala con ID {id_sala}.")

    # Guardar cambios y devolver los datos actualizados
    actualizar_sala_db(id_sala, datos)
    sala_actualizada = buscar_sala_por_id_db(id_sala)

    return {
        "id_sala": sala_actualizada["id_sala"],
        "id_local": sala_actualizada["id_local"],
        "numero": sala_actualizada["numero"],
        "capacidad": int(sala_actualizada["capacidad"] or 0),
        "activa": bool(sala_actualizada["activa"]),
    }


