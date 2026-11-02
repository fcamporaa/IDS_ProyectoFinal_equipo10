from src.repositories.salas_repository import (
    obtener_locales_db,
    buscar_local_por_id_db,
    obtener_salas_por_local_db,
    buscar_sala_por_id_db,
    obtener_butacas_por_sala_db,
    actualizar_sala_db,
)
from src.utils import construir_error_api


def listar_locales() -> list[dict]:
    """Lista los locales de cine disponibles."""
    locales = obtener_locales_db()
    resultado = []
    for l in locales:
        resultado.append({
            "id_local": l["id_local"],
            "nombre": l["nombre"],
            "direccion": l["direccion"],
            "activo": bool(l["activo"]),
        })
    return resultado


def listar_salas_por_local(id_local: int) -> list[dict]:
    """Lista las salas de un complejo y su capacidad total."""
    local = buscar_local_por_id_db(id_local)
    if not local:
        raise ValueError(
            construir_error_api(
                code="local.no_encontrado",
                message="Recurso no encontrado",
                description=f"No se encontro el local con ID {id_local}.",
            ),
            404,
        )

    salas = obtener_salas_por_local_db(id_local)
    resultado = []
    for s in salas:
        resultado.append({
            "id_sala": s["id_sala"],
            "id_local": s["id_local"],
            "numero": s["numero"],
            "capacidad": int(s["capacidad"] or 0),
            "activa": bool(s["activa"]),
        })
    return resultado


def obtener_detalle_sala(id_sala: int) -> dict:
    """Obtiene la sala y la grilla o distribución física de sus butacas."""
    sala = buscar_sala_por_id_db(id_sala)
    if not sala:
        raise ValueError(
            construir_error_api(
                code="sala.no_encontrada",
                message="Recurso no encontrado",
                description=f"No se encontro la sala con ID {id_sala}.",
            ),
            404,
        )

    butacas_db = obtener_butacas_por_sala_db(id_sala)
    butacas = []
    for b in butacas_db:
        butacas.append({
            "id_butaca": b["id_butaca"],
            "id_sala": b["id_sala"],
            "fila": b["fila"],
            "numero": b["numero"],
            "activa": bool(b["activa"]),
        })

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
    sala = buscar_sala_por_id_db(id_sala)
    if not sala:
        raise ValueError(
            construir_error_api(
                code="sala.no_encontrada",
                message="Recurso no encontrado",
                description=f"No se encontro la sala con ID {id_sala}.",
            ),
            404,
        )

    actualizar_sala_db(id_sala, datos)
    sala_actualizada = buscar_sala_por_id_db(id_sala)

    return {
        "id_sala": sala_actualizada["id_sala"],
        "id_local": sala_actualizada["id_local"],
        "numero": sala_actualizada["numero"],
        "capacidad": int(sala_actualizada["capacidad"] or 0),
        "activa": bool(sala_actualizada["activa"]),
    }
