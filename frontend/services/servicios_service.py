from services.api_client import consultar_backend


def formatear_monto(monto: float) -> str:
    """Formatea importes enteros para mostrarlos con separador argentino."""
    return f"${monto:,.0f}".replace(",", ".")


def _adaptar_servicio(servicio: dict) -> dict | None:
    """Convierte el contrato de la API al contexto esperado por la tarjeta."""
    if not isinstance(servicio, dict):
        return None

    id_servicio = servicio.get("id_servicio")
    nombre = servicio.get("nombre")
    tipo = servicio.get("tipo")
    precio = servicio.get("precio")
    if (
        type(id_servicio) is not int
        or id_servicio <= 0
        or not isinstance(nombre, str)
        or not nombre.strip()
        or tipo not in ("COMIDA", "BEBIDA")
        or isinstance(precio, bool)
        or not isinstance(precio, (int, float))
        or precio < 0
    ):
        return None

    precio = float(precio)
    return {
        "id_servicio": id_servicio,
        "nombre": nombre,
        "tipo": tipo,
        "categoria": tipo.lower(),
        "descripcion": tipo,
        "precio": precio,
        "precio_formato": formatear_monto(precio),
        "imagen_url": None,
        "badge_top": None,
        "badge_top_tipo": None,
        "badge_image_bottom": None,
        "cantidad": 0,
    }


def obtener_servicios_disponibles() -> list[dict] | None:
    """Obtiene y adapta el catálogo activo; None indica error de comunicación."""
    respuesta, estado = consultar_backend("/servicios", metodo="GET")
    if estado != 200 or not isinstance(respuesta, list):
        return None

    servicios = [_adaptar_servicio(item) for item in respuesta]
    return [servicio for servicio in servicios if servicio is not None]
