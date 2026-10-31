"""Configuración de ejecución consultada en funciones: sin estado mutable global."""
import os


def pagos_simulados_habilitados() -> bool:
    return os.getenv("ALLOW_SIMULATED_PAYMENTS", "false").lower() == "true"


def obtener_auth_secret() -> str:
    clave = os.getenv("AUTH_SECRET_KEY", "")
    if len(clave) < 32:
        raise RuntimeError("Falta configurar AUTH_SECRET_KEY (mínimo 32 caracteres).")
    return clave


def obtener_config_email() -> dict:
    return {
        "modo": os.getenv("EMAIL_MODE", "console").lower(),
        "host": os.getenv("SMTP_HOST", ""),
        "puerto": int(os.getenv("SMTP_PORT", "587")),
        "usuario": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "remitente": os.getenv("SMTP_FROM", ""),
        "starttls": os.getenv("SMTP_STARTTLS", "true").lower() == "true",
    }
