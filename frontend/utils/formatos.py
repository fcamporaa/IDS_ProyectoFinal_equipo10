"""Formateadores de presentación compartidos: convierten duración, fecha y hora en texto legible para la pantalla."""
from datetime import date, datetime

# strftime depende del idioma del servidor y daría "Sun Nov": por eso los nombres van fijos en castellano
DIAS_SEMANA = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")
MESES = ("Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic")


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


def formatear_fecha_corta(dia: date) -> str:
    """2026-11-15 -> 'Dom 15 Nov'."""
    return f"{DIAS_SEMANA[dia.weekday()]} {dia.day} {MESES[dia.month - 1]}"


def formatear_hora(momento: datetime) -> str:
    """2026-11-15 20:00 -> '20:00 hs'."""
    return f"{momento:%H:%M} hs"


def formatear_precio(valor: float) -> str:
    """12500 -> '$12.500'; 8500.5 -> '$8.500,50'."""
    texto = f"{valor:,.0f}" if valor == int(valor) else f"{valor:,.2f}"
    return "$" + texto.replace(",", "X").replace(".", ",").replace("X", ".")
