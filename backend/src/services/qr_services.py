import io
import secrets


def crear_token_qr() -> str:
    """Token de 256 bits; el QR contiene un identificador opaco, no datos del cliente."""
    return secrets.token_urlsafe(32)


def crear_imagen_qr(token: str) -> bytes:
    """Requiere el paquete opcional qrcode; no se agregó a requirements.txt."""
    try:
        import qrcode
    except ImportError as error:
        raise RuntimeError(
            "Falta la dependencia qrcode: obtener autorización antes de agregarla a requirements.txt."
        ) from error
    imagen = qrcode.make(token)
    salida = io.BytesIO()
    imagen.save(salida, format="PNG")
    return salida.getvalue()
