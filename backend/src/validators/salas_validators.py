from src.utils import construir_error_api
from src.validators.auth_validators import validar_autorizacion
from src.repositories.usuarios_repository import buscar_usuario_por_id_db


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


def validar_autorizacion_admin(encabezado: str | None) -> dict:
    """
    Valida el encabezado Bearer y verifica que el usuario tenga rol ADMINISTRADOR.
    Retorna un dict con 'errors' y 'status' si no está autorizado.
    """
    # Validar token Bearer
    autorizacion = validar_autorizacion(encabezado)
    if "errors" in autorizacion:
        return {**autorizacion, "status": 401}

    # Verificar que el usuario exista y esté activo
    usuario = buscar_usuario_por_id_db(autorizacion["usuario_id"])
    if not usuario or not usuario["activo"]:
        return {
            **construir_error_api(
                "error.auth.token_invalido",
                "Token inválido",
                "El usuario asociado al token no existe o está inactivo.",
            ),
            "status": 401,
        }

    # Verificar que tenga rol de administrador
    if usuario["rol"] != "ADMINISTRADOR":
        return {
            **construir_error_api(
                "error.auth.prohibido",
                "Acceso denegado",
                "El usuario no tiene rol ADMINISTRADOR para ejecutar esta acción.",
            ),
            "status": 403,
        }

    return autorizacion


