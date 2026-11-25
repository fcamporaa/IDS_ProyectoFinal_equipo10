from src.repositories.salas_repository import (
    obtener_locales_db,
    buscar_local_por_id_db,
    obtener_salas_por_local_db,
    obtener_salas_admin_db,
    buscar_sala_por_id_db,
    buscar_sala_por_local_y_numero_db,
    obtener_butacas_por_sala_db,
    contar_butacas_sala_db,
    existe_butaca_en_sala_db,
    insertar_sala_con_butacas_db,
    insertar_butacas_lote_db,
    actualizar_sala_db,
)
from src.utils import error_conflicto, error_no_encontrado


def _serializar_sala(sala: dict) -> dict:
    """Normaliza el diccionario de sala para la respuesta JSON."""
    return {
        "id_sala": sala["id_sala"],
        "id_local": sala["id_local"],
        "numero": sala["numero"],
        "capacidad": int(sala["capacidad"] or 0),
        "activa": bool(sala["activa"]),
    }


def _serializar_sala_admin(sala: dict) -> dict:
    """Incluye el nombre del complejo para el listado administrativo."""
    return {
        **_serializar_sala(sala),
        "nombre_local": sala["nombre_local"],
    }


def _serializar_butaca(butaca: dict) -> dict:
    return {
        "id_butaca": butaca["id_butaca"],
        "id_sala": butaca["id_sala"],
        "fila": butaca["fila"],
        "numero": butaca["numero"],
        "activa": bool(butaca["activa"]),
    }


def _generar_coordenadas_butacas(filas: int, asientos_por_fila: int) -> list[tuple[str, int]]:
    """Arma la grilla (fila letra, número) a partir del layout solicitado."""
    coordenadas = []
    for indice_fila in range(filas):
        letra = chr(ord("A") + indice_fila)
        for asiento in range(1, asientos_por_fila + 1):
            coordenadas.append((letra, asiento))
    return coordenadas


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
    local = buscar_local_por_id_db(id_local)
    if not local:
        raise error_no_encontrado("El complejo seleccionado ya no está disponible.")

    salas = obtener_salas_por_local_db(id_local)
    return [_serializar_sala(s) for s in salas]


def listar_salas_admin() -> list[dict]:
    """Lista todas las salas (activas e inactivas) para el backoffice."""
    return [_serializar_sala_admin(s) for s in obtener_salas_admin_db()]


def obtener_detalle_sala(id_sala: int) -> dict:
    """Obtiene la sala y la grilla o distribución física de sus butacas."""
    sala = buscar_sala_por_id_db(id_sala)
    if not sala:
        raise error_no_encontrado("La sala seleccionada ya no está disponible.")

    butacas_db = obtener_butacas_por_sala_db(id_sala)
    return {
        **_serializar_sala(sala),
        "butacas": [_serializar_butaca(b) for b in butacas_db],
    }


def crear_sala(id_local: int, datos: dict) -> dict:
    """Crea una sala con su grilla de butacas en una sola operación atómica."""
    local = buscar_local_por_id_db(id_local)
    if not local:
        raise error_no_encontrado("El complejo seleccionado ya no está disponible.")
    if not local["activo"]:
        raise error_conflicto("No se pueden crear salas en un complejo inactivo.")

    existente = buscar_sala_por_local_y_numero_db(id_local, datos["numero"])
    if existente:
        raise error_conflicto(
            f"Ya existe la sala número {datos['numero']} en este complejo."
        )

    butacas = _generar_coordenadas_butacas(datos["filas"], datos["asientos_por_fila"])
    id_sala = insertar_sala_con_butacas_db(
        id_local, datos["numero"], datos["activa"], butacas
    )
    return obtener_detalle_sala(id_sala)


def generar_butacas_sala(id_sala: int, datos: dict) -> dict:
    """Genera butacas para una sala que aún no tiene grilla física."""
    sala = buscar_sala_por_id_db(id_sala)
    if not sala:
        raise error_no_encontrado("La sala seleccionada ya no está disponible.")

    if contar_butacas_sala_db(id_sala) > 0:
        raise error_conflicto(
            "La sala ya tiene butacas registradas. No se puede regenerar la grilla."
        )

    butacas = _generar_coordenadas_butacas(datos["filas"], datos["asientos_por_fila"])
    for fila, numero in butacas:
        if existe_butaca_en_sala_db(id_sala, fila, numero):
            raise error_conflicto(
                f"Ya existe la butaca {fila}{numero} en esta sala."
            )

    insertar_butacas_lote_db(id_sala, butacas)
    return obtener_detalle_sala(id_sala)


def actualizar_configuracion_sala(id_sala: int, datos: dict) -> dict:
    """Actualiza configuración de la sala (activa / inactiva o número)."""
    sala = buscar_sala_por_id_db(id_sala)
    if not sala:
        raise error_no_encontrado("La sala seleccionada ya no está disponible.")

    if "numero" in datos and datos["numero"] != sala["numero"]:
        conflicto = buscar_sala_por_local_y_numero_db(sala["id_local"], datos["numero"])
        if conflicto and conflicto["id_sala"] != id_sala:
            raise error_conflicto(
                f"Ya existe la sala número {datos['numero']} en este complejo."
            )

    actualizar_sala_db(id_sala, datos)
    sala_actualizada = buscar_sala_por_id_db(id_sala)
    return _serializar_sala(sala_actualizada)
