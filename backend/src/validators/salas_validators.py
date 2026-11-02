from src.utils import construir_error_api


def _validar_entero_positivo(valor, nombre_campo: str) -> int:
    """Verifica que el valor sea un entero positivo."""
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError(
            construir_error_api(
                "error.validacion.parametro",
                "Dato inválido",
                f"El campo '{nombre_campo}' debe ser un número entero positivo.",
            ),
            400,
        )
    return valor


def validar_id_local(id_local: int) -> int:
    """Valida el id del local."""
    return _validar_entero_positivo(id_local, "id_local")


def validar_id_sala(id_sala: int) -> int:
    """Valida el id de la sala."""
    return _validar_entero_positivo(id_sala, "id_sala")


def validar_actualizar_sala(datos: dict) -> dict:
    """Valida los campos para actualizar una sala (numero o activa)."""
    if not isinstance(datos, dict) or not datos:
        raise ValueError(
            construir_error_api(
                "error.validacion.cuerpo",
                "Cuerpo de solicitud inválido",
                "El cuerpo de la solicitud no puede estar vacío.",
            ),
            400,
        )

    # Verificar que solo vengan los campos permitidos
    campos_permitidos = {"numero", "activa"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        raise ValueError(
            construir_error_api(
                "error.validacion.campo_no_permitido",
                "Campo no permitido",
                f"Los campos no están permitidos: {', '.join(sorted(campos_desconocidos))}.",
            ),
            400,
        )

    datos_validados = {}

    # Validar numero si viene en el body
    if "numero" in datos:
        datos_validados["numero"] = _validar_entero_positivo(datos["numero"], "numero")

    # Validar activa si viene en el body
    if "activa" in datos:
        if not isinstance(datos["activa"], bool):
            raise ValueError(
                construir_error_api(
                    "error.validacion.parametro",
                    "Dato inválido",
                    "El campo 'activa' debe ser un booleano (true o false).",
                ),
                400,
            )
        datos_validados["activa"] = datos["activa"]

    # Debe enviar al menos un campo para actualizar
    if not datos_validados:
        raise ValueError(
            construir_error_api(
                "error.validacion.cuerpo",
                "Datos de actualización requeridos",
                "Debe proporcionar al menos 'numero' o 'activa' para actualizar la sala.",
            ),
            400,
        )

    return datos_validados


