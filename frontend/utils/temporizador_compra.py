"""Temporizador del embudo de compra, independiente de las vistas."""

import math
import time

from flask import flash, redirect, session, url_for


DURACION_COMPRA_SEGUNDOS = 10 * 60
_CLAVE_VENCIMIENTO = "compra_expira_en"
_CLAVE_PELICULA = "compra_id_pelicula"


def iniciar_temporizador_compra() -> None:
    """Inicia una única cuenta atrás; navegar o actualizar no modifica el plazo."""
    if _CLAVE_VENCIMIENTO not in session:
        session[_CLAVE_VENCIMIENTO] = time.time() + DURACION_COMPRA_SEGUNDOS


def temporizador_compra_vencido() -> bool:
    """Sin fecha límite activa tampoco se permite confirmar una compra."""
    expira_en = session.get(_CLAVE_VENCIMIENTO)
    if expira_en is None:
        return True
    try:
        return time.time() >= float(expira_en)
    except (TypeError, ValueError):
        return True


def registrar_pelicula_compra(id_pelicula: int | None) -> None:
    if id_pelicula:
        session[_CLAVE_PELICULA] = id_pelicula


def contexto_temporizador_compra() -> dict:
    """Devuelve valores para mostrar un reloj coherente en las tres vistas."""
    ahora = time.time()
    expira_en = float(session[_CLAVE_VENCIMIENTO])
    restante = max(0, math.ceil(expira_en - ahora))
    return {
        "expira_en_ms": int(expira_en * 1000),
        "ahora_servidor_ms": int(ahora * 1000),
        "tiempo_restante": f"{restante // 60:02d}:{restante % 60:02d}",
    }


def limpiar_compra_temporal() -> int | None:
    """Elimina selección y vencimiento; conserva el ID para una redirección útil."""
    compra = session.pop("compra", None) or {}
    id_pelicula = compra.get("id_pelicula") or session.get(_CLAVE_PELICULA)
    session.pop(_CLAVE_VENCIMIENTO, None)
    session.pop(_CLAVE_PELICULA, None)
    session.pop("servicios_seleccionados", None)
    return id_pelicula


def redirigir_compra_expirada():
    id_pelicula = limpiar_compra_temporal()
    flash(
        "El tiempo asignado para completar tu compra ha expirado. "
        "Por favor seleccioná tus butacas nuevamente.",
        "error",
    )
    if id_pelicula:
        return redirect(url_for("peliculas.detalle_pelicula", id_pelicula=id_pelicula))
    return redirect(url_for("home.index"))
