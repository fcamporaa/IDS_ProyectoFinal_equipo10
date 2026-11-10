def extraer_mensaje_error(
    respuesta_backend: dict | list | str | None,
    mensaje_por_defecto: str = "Ocurrió un error inesperado.",
) -> str:
    """
    Normaliza y extrae un mensaje de error legible para el usuario (usado en flash() de Flask).
    Soporta:
    1. Errores estructurados del backend (formato construir_error_api con lista 'errors').
    2. Errores de transporte del cliente HTTP (campo 'error').
    3. Respuestas con campo 'mensaje' o texto plano.
    """
    if isinstance(respuesta_backend, dict):
        # 1. Caso: error oficial del backend (construir_error_api)
        errores = respuesta_backend.get("errors")
        if isinstance(errores, list) and len(errores) > 0 and isinstance(errores[0], dict):
            primer_error = errores[0]
            return (
                primer_error.get("description")
                or primer_error.get("message")
                or mensaje_por_defecto
            )

        # 2. Caso: error de red o 502 de api_client
        if "error" in respuesta_backend and isinstance(respuesta_backend["error"], str):
            return respuesta_backend["error"]

        # 3. Caso: mensaje genérico del backend
        if "mensaje" in respuesta_backend and isinstance(respuesta_backend["mensaje"], str):
            return respuesta_backend["mensaje"]

    elif isinstance(respuesta_backend, str) and respuesta_backend.strip():
        return respuesta_backend.strip()

    return mensaje_por_defecto

