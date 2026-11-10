from src.utils import (
    error_validacion,
    validar_booleano,
    validar_entero_positivo,
    validar_objeto_json,
)


def validar_id_local(id_local: int) -> int:
    """Valida el id del local."""
    return validar_entero_positivo(id_local, "id_local")


def validar_id_sala(id_sala: int) -> int:
    """Valida el id de la sala."""
    return validar_entero_positivo(id_sala, "id_sala")


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
        datos_validados["numero"] = validar_entero_positivo(datos["numero"], "numero")

    # Validar activa si viene en el body
    if "activa" in datos:
        datos_validados["activa"] = validar_booleano(datos["activa"], "activa")

    # Debe enviar al menos un campo para actualizar
    if not datos_validados:
        raise error_validacion(
            "Debe proporcionar al menos 'numero' o 'activa' para actualizar la sala."
        )

    return datos_validados
