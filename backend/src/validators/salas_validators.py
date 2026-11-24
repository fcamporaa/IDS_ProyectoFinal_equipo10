from src.constants import MAX_ASIENTOS_POR_FILA, MAX_FILAS_SALA, MAX_NUMERO_SALA
from src.utils import (
    error_validacion,
    validar_booleano,
    validar_entero_en_rango,
    validar_entero_positivo,
    validar_objeto_json,
)


def validar_id_local(id_local: int) -> int:
    """Valida el id del local."""
    return validar_entero_positivo(id_local, "id_local")


def validar_id_sala(id_sala: int) -> int:
    """Valida el id de la sala."""
    return validar_entero_positivo(id_sala, "id_sala")


def _validar_layout_butacas(datos: dict) -> dict:
    """Valida filas y asientos_por_fila para armar la grilla física."""
    if "filas" not in datos or "asientos_por_fila" not in datos:
        raise error_validacion(
            "Debe indicar 'filas' y 'asientos_por_fila' para generar las butacas."
        )

    return {
        "filas": validar_entero_en_rango(datos["filas"], "filas", 1, MAX_FILAS_SALA),
        "asientos_por_fila": validar_entero_en_rango(
            datos["asientos_por_fila"],
            "asientos_por_fila",
            1,
            MAX_ASIENTOS_POR_FILA,
        ),
    }


def validar_crear_sala(datos: dict) -> dict:
    """Valida el alta de una sala con su layout de butacas."""
    datos = validar_objeto_json(datos)

    campos_permitidos = {"numero", "filas", "asientos_por_fila", "activa"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        raise error_validacion(
            f"Los campos no están permitidos: {', '.join(sorted(campos_desconocidos))}."
        )

    if "numero" not in datos:
        raise error_validacion("El campo 'numero' es obligatorio.")

    numero = validar_entero_positivo(datos["numero"], "numero")
    datos_validados = {
        "numero": validar_entero_en_rango(numero, "numero", 1, MAX_NUMERO_SALA),
        **_validar_layout_butacas(datos),
    }

    if "activa" in datos:
        datos_validados["activa"] = validar_booleano(datos["activa"], "activa")
    else:
        datos_validados["activa"] = True

    return datos_validados


def validar_generar_butacas(datos: dict) -> dict:
    """Valida el body para generar butacas en una sala existente."""
    datos = validar_objeto_json(datos)

    campos_permitidos = {"filas", "asientos_por_fila"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        raise error_validacion(
            f"Los campos no están permitidos: {', '.join(sorted(campos_desconocidos))}."
        )

    return _validar_layout_butacas(datos)


def validar_actualizar_sala(datos: dict) -> dict:
    """Valida los campos para actualizar una sala (numero o activa)."""
    datos = validar_objeto_json(datos)
    if not datos:
        raise error_validacion("El cuerpo de la solicitud no puede estar vacío.")

    # Verificar que solo vengan los campos permitidos
    campos_permitidos = {"numero", "activa"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        raise error_validacion(
            f"Los campos no están permitidos: {', '.join(sorted(campos_desconocidos))}."
        )

    datos_validados = {}

    # Validar numero si viene en el body
    if "numero" in datos:
        numero = validar_entero_positivo(datos["numero"], "numero")
        datos_validados["numero"] = validar_entero_en_rango(
            numero, "numero", 1, MAX_NUMERO_SALA
        )

    # Validar activa si viene en el body
    if "activa" in datos:
        datos_validados["activa"] = validar_booleano(datos["activa"], "activa")

    # Debe enviar al menos un campo para actualizar
    if not datos_validados:
        raise error_validacion(
            "Debe proporcionar al menos 'numero' o 'activa' para actualizar la sala."
        )

    return datos_validados
