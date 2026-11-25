"""Formateadores de presentación compartidos: convierten duración, fecha y hora en texto legible para la pantalla."""
from datetime import date, datetime
from decimal import Decimal
from email.utils import parsedate_to_datetime

# strftime depende del idioma del servidor y daría "Sun Nov": por eso los nombres van fijos en castellano
DIAS_SEMANA = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")
MESES = ("Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic")


def parsear_datetime_seguro(valor: str | datetime | None) -> datetime | None:
    """Convierte un texto ISO, RFC 2822 o datetime a un objeto datetime de forma tolerante."""
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime.combine(valor, datetime.min.time())
    if not isinstance(valor, str):
        return None

    texto = valor.strip()
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        pass

    try:
        return parsedate_to_datetime(texto)
    except (ValueError, TypeError):
        return None


def formatear_duracion(minutos: int | None) -> str:
    """166 -> '2h 46m', 120 -> '2h', 45 -> '45m'. Sin duración (None o 0) devuelve texto vacío."""
    if not minutos:
        return ""
    horas, resto = divmod(minutos, 60)
    if not horas:
        return f"{resto}m"
    if not resto:
        return f"{horas}h"
    return f"{horas}h {resto}m"


def formatear_fecha_corta(dia: date | datetime | str | None) -> str:
    """2026-11-15 -> 'Dom 15 Nov'."""
    if dia is None:
        return ""
    if isinstance(dia, str):
        dt = parsear_datetime_seguro(dia)
        if not dt:
            return dia
        dia = dt.date()
    elif isinstance(dia, datetime):
        dia = dia.date()
    return f"{DIAS_SEMANA[dia.weekday()]} {dia.day} {MESES[dia.month - 1]}"


def formatear_hora(momento: datetime | str | None) -> str:
    """2026-11-15 20:00 -> '20:00 hs'."""
    if momento is None:
        return ""
    if isinstance(momento, str):
        dt = parsear_datetime_seguro(momento)
        if not dt:
            return momento
        momento = dt
    return f"{momento:%H:%M} hs"


def formatear_hora_simple(momento: datetime | str | None) -> str:
    """2026-11-15 20:00 -> '20:00' (sin sufijo hs, útil para inputs type=time o selectores)."""
    if momento is None:
        return ""
    if isinstance(momento, str):
        dt = parsear_datetime_seguro(momento)
        if not dt:
            return momento
        momento = dt
    return f"{momento:%H:%M}"


def formatear_fecha_hora(
    momento: datetime | str | None, separador: str = " · "
) -> str:
    """Convierte un datetime o cadena ISO en formato uniforme: 'Dom 15 Nov · 20:00 hs'."""
    if momento is None:
        return ""
    if isinstance(momento, str):
        dt = parsear_datetime_seguro(momento)
        if not dt:
            return momento
        momento = dt
    fecha = formatear_fecha_corta(momento.date())
    hora = formatear_hora(momento)
    return f"{fecha}{separador}{hora}"


def formatear_precio(valor: int | float | str | Decimal) -> str:
    """Formatea importes: 12500 -> '$12.500'; 8500.5 -> '$8.500,50'."""

    monto = Decimal(str(valor))

    texto = (
        f"{monto:,.0f}"
        if monto == monto.to_integral_value()
        else f"{monto:,.2f}"
    )

    return "$" + texto.replace(",", "X").replace(".", ",").replace("X", ".")
