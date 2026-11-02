from decimal import Decimal, InvalidOperation

from src.constants import TIPOS_SERVICIO
from src.utils import construir_error_api


def validar_id_servicio(id_servicio: int) -> int:
    """Valida que id_servicio sea un entero positivo."""
    if isinstance(id_servicio, bool) or not isinstance(id_servicio, int) or id_servicio <= 0:
        return construir_error_api(
            "error.validacion.id_servicio",
            "ID de servicio inválido",
            "El ID del servicio debe ser un entero positivo.",
        )
    return id_servicio


def validar_precio_servicio(precio) -> Decimal | dict:
    if isinstance(precio, bool) or not isinstance(precio, (int, float)):
        return construir_error_api(
            "error.validacion.precio",
            "Precio inválido",
            "El precio debe ser un número positivo con hasta dos decimales y un máximo de 99999999.99.",
        )

    try:
        precio_decimal = Decimal(str(precio))
    except (InvalidOperation, ValueError):
        return construir_error_api(
            "error.validacion.precio",
            "Precio inválido",
            "El precio debe ser un número positivo con hasta dos decimales y un máximo de 99999999.99.",
        )

    if (
        not precio_decimal.is_finite()
        or precio_decimal <= 0
        or precio_decimal.as_tuple().exponent < -2
        or precio_decimal > Decimal("99999999.99")
    ):
        return construir_error_api(
            "error.validacion.precio",
            "Precio inválido",
            "El precio debe ser un número positivo con hasta dos decimales y un máximo de 99999999.99.",
        )
    return precio_decimal


def validar_crear_servicio(datos: dict) -> dict:
    """Valida los datos obligatorios para crear un servicio."""
    if not isinstance(datos, dict):
        return construir_error_api(
            "error.validacion.cuerpo",
            "Cuerpo de solicitud inválido",
            "Se esperaba un objeto JSON con los datos del servicio.",
        )

    campos_permitidos = {"nombre", "tipo", "precio"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        return construir_error_api(
            "error.validacion.campo_no_permitido",
            "Campo no permitido",
            f"Los campos no están permitidos: {', '.join(sorted(campos_desconocidos))}.",
        )

    campos_faltantes = campos_permitidos - set(datos)
    if campos_faltantes:
        return construir_error_api(
            "error.validacion.campos_requeridos",
            "Campos requeridos faltantes",
            f"Faltan campos obligatorios: {', '.join(sorted(campos_faltantes))}.",
        )

    nombre = datos.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip() or len(nombre.strip()) > 50:
        return construir_error_api(
            "error.validacion.nombre",
            "Nombre inválido",
            "El nombre debe tener entre 1 y 50 caracteres.",
        )

    tipo = datos.get("tipo")
    if not isinstance(tipo, str) or tipo not in TIPOS_SERVICIO:
        return construir_error_api(
            "error.validacion.tipo_servicio",
            "Tipo de servicio inválido",
            "El tipo debe ser COMIDA o BEBIDA.",
        )

    precio = validar_precio_servicio(datos.get("precio"))
    if isinstance(precio, dict):
        return precio

    return {"nombre": nombre.strip(), "tipo": tipo, "precio": precio, "activo": 1}


def validar_actualizar_servicio(datos: dict) -> dict:
    """Valida campos permitidos para actualizar un servicio."""
    if not isinstance(datos, dict):
        return construir_error_api(
            "error.validacion.cuerpo",
            "Cuerpo de solicitud inválido",
            "Se esperaba un objeto JSON con los datos del servicio.",
        )

    campos_permitidos = {"nombre", "tipo", "precio", "activo"}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        return construir_error_api(
            "error.validacion.campo_no_permitido",
            "Campo no permitido",
            f"Los campos no están permitidos: {', '.join(sorted(campos_desconocidos))}.",
        )

    if not datos:
        return construir_error_api(
            "error.validacion.servicio_vacio",
            "Datos de actualización requeridos",
            "Debe proporcionar al menos un campo para actualizar el servicio.",
        )

    datos_validados = {}
    if "nombre" in datos:
        nombre = datos["nombre"]
        if not isinstance(nombre, str) or not nombre.strip() or len(nombre.strip()) > 50:
            return construir_error_api(
                "error.validacion.nombre",
                "Nombre inválido",
                "El nombre debe tener entre 1 y 50 caracteres.",
            )
        datos_validados["nombre"] = nombre.strip()

    if "tipo" in datos:
        tipo = datos["tipo"]
        if not isinstance(tipo, str) or tipo not in TIPOS_SERVICIO:
            return construir_error_api(
                "error.validacion.tipo_servicio",
                "Tipo de servicio inválido",
                "El tipo debe ser COMIDA o BEBIDA.",
            )
        datos_validados["tipo"] = tipo

    if "precio" in datos:
        precio = validar_precio_servicio(datos["precio"])
        if isinstance(precio, dict):
            return precio
        datos_validados["precio"] = precio

    if "activo" in datos:
        activo = datos["activo"]
        if not isinstance(activo, bool):
            return construir_error_api(
                "error.validacion.activo",
                "Estado activo inválido",
                "El campo activo debe ser verdadero o falso.",
            )
        datos_validados["activo"] = 1 if activo else 0

    return datos_validados
