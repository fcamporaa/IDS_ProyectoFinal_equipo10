from decimal import Decimal

import pymysql

from src.repositories.servicios_repository import (
    obtener_servicios_activos_db,
    buscar_servicio_por_id_db,
    buscar_servicio_por_nombre_db,
    insertar_servicio_db,
    actualizar_servicio_db,
    dar_de_baja_servicio_db,
)
from src.utils import construir_error_api


def _serializar_servicio(servicio: dict) -> dict:
    servicio_serializado = servicio.copy()
    precio = servicio_serializado.get("precio")
    if isinstance(precio, Decimal):
        servicio_serializado["precio"] = float(precio)
    if "activo" in servicio_serializado:
        servicio_serializado["activo"] = bool(servicio_serializado["activo"])
    return servicio_serializado


def _error_nombre_duplicado() -> dict:
    return construir_error_api(
        "error.servicio.nombre_existente",
        "Servicio ya existente",
        "Ya existe un servicio con ese nombre.",
    )


def listar_servicios() -> list[dict]:
    """Lista todos los servicios adicionales activos."""
    return [_serializar_servicio(servicio) for servicio in obtener_servicios_activos_db()]


def crear_servicio(datos: dict) -> dict:
    """Crea un nuevo servicio adicional."""
    datos_existentes = buscar_servicio_por_nombre_db(datos["nombre"])
    if datos_existentes:
        return _error_nombre_duplicado()

    try:
        id_servicio = insertar_servicio_db(datos)
    except pymysql.err.IntegrityError as error:
        if error.args and error.args[0] == 1062:
            return _error_nombre_duplicado()
        raise

    servicio = buscar_servicio_por_id_db(id_servicio)
    if servicio is None:
        servicio = datos | {"id_servicio": id_servicio}
    return _serializar_servicio(servicio)


def actualizar_servicio(id_servicio: int, datos: dict) -> dict | None:
    """Modifica datos o precio de un servicio, incluida su reactivación."""
    servicio = buscar_servicio_por_id_db(id_servicio)
    if servicio is None:
        return None

    if "nombre" in datos:
        existente = buscar_servicio_por_nombre_db(datos["nombre"])
        if existente and existente["id_servicio"] != id_servicio:
            return _error_nombre_duplicado()

    try:
        actualizar_servicio_db(id_servicio, datos)
    except pymysql.err.IntegrityError as error:
        if error.args and error.args[0] == 1062:
            return _error_nombre_duplicado()
        raise

    servicio_actualizado = buscar_servicio_por_id_db(id_servicio)
    return _serializar_servicio(servicio_actualizado) if servicio_actualizado else None


def eliminar_servicio(id_servicio: int) -> bool:
    """Da de baja lógica un servicio; es seguro repetir la operación."""
    servicio = buscar_servicio_por_id_db(id_servicio)
    if servicio is None:
        return False
    if not servicio["activo"]:
        return True
    return dar_de_baja_servicio_db(id_servicio)
