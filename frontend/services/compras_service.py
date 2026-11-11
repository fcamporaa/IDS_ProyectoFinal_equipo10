from services.api_client import consultar_backend


def enviar_compra_al_backend(datos: dict, token: str):
    """Envía la transacción de compra al endpoint POST /compras del backend."""
    return consultar_backend("/compras", token=token, metodo="POST", datos=datos)


def obtener_compra_del_backend(id_compra: int, token: str):
    """Obtiene el comprobante y detalle de una compra por su identificador."""
    return consultar_backend(f"/compras/{id_compra}", token=token, metodo="GET")


def obtener_mis_compras(token: str):
    """Obtiene el historial de compras del usuario autenticado."""
    return consultar_backend("/compras/mis-compras", token=token, metodo="GET")


def cancelar_compra_al_backend(id_compra: int, token: str):
    """Solicita la cancelación de una compra y la liberación de sus butacas."""
    return consultar_backend(
        f"/compras/{id_compra}/cancelar", token=token, metodo="PUT", datos={}
    )


def reenviar_comprobante_al_backend(id_compra: int, token: str):
    """Solicita el reenvío por correo del comprobante con código QR."""
    return consultar_backend(
        f"/compras/{id_compra}/reenviar-comprobante", token=token, metodo="POST"
    )
