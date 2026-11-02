from src.utils import construir_error_api


def validar_id_local(id_local: int) -> int:
    """Valida que id_local sea un entero positivo."""
    if not isinstance(id_local, int) or isinstance(id_local, bool) or id_local <= 0:
        raise ValueError(
            construir_error_api(
                code="error.validacion.parametro",
                message="Dato invalido",
                description="El ID del local debe ser un numero entero positivo.",
            ),
            400,
        )
    return id_local


def validar_id_sala(id_sala: int) -> int:
    """Valida que id_sala sea un entero positivo."""
    if not isinstance(id_sala, int) or isinstance(id_sala, bool) or id_sala <= 0:
        raise ValueError(
            construir_error_api(
                code="error.validacion.parametro",
                message="Dato invalido",
                description="El ID de la sala debe ser un numero entero positivo.",
            ),
            400,
        )
    return id_sala


def validar_actualizar_sala(datos: dict) -> dict:
    """Valida los campos a modificar de una sala."""
    if not datos or not isinstance(datos, dict):
        raise ValueError(
            construir_error_api(
                code="error.validacion.body",
                message="Dato invalido",
                description="El cuerpo de la solicitud debe ser un JSON no vacio.",
            ),
            400,
        )

    # Verificar que solo vengan los campos permitidos
    for campo in datos:
        if campo not in ("numero", "activa"):
            raise ValueError(
                construir_error_api(
                    code="error.validacion.campos",
                    message="Campos no permitidos",
                    description=f"El campo '{campo}' no es valido.",
                ),
                400,
            )

    # Validar tipo de numero si viene
    if "numero" in datos:
        numero = datos["numero"]
        if not isinstance(numero, int) or isinstance(numero, bool) or numero <= 0:
            raise ValueError(
                construir_error_api(
                    code="error.validacion.parametro",
                    message="Dato invalido",
                    description="El numero de sala debe ser un entero positivo.",
                ),
                400,
            )

    # Validar tipo de activa si viene
    if "activa" in datos:
        if not isinstance(datos["activa"], bool):
            raise ValueError(
                construir_error_api(
                    code="error.validacion.parametro",
                    message="Dato invalido",
                    description="El campo 'activa' debe ser un booleano (true o false).",
                ),
                400,
            )

    return datos
