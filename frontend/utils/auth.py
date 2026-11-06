from functools import wraps

from flask import flash, redirect, session, url_for

from services.auth_service import obtener_perfil


def admin_required(vista):
    """Exige una sesión válida con rol ADMINISTRADOR para acceder a la vista."""

    @wraps(vista)
    def envoltura(*args, **kwargs):
        token = session.get("access_token")
        if not token:
            flash("Necesitás iniciar sesión como administrador.", "error")
            return redirect(url_for("home.index"))

        perfil, estado = obtener_perfil(token)
        if estado == 200 and isinstance(perfil, dict):
            if perfil.get("rol") == "ADMINISTRADOR":
                session["usuario"] = perfil
                return vista(*args, **kwargs)

        session.pop("access_token", None)
        session.pop("usuario", None)
        if estado == 200:
            flash("Acceso denegado. Se requiere una cuenta de administrador.", "error")
        else:
            flash("La sesión no es válida o el backend no está disponible.", "error")
        return redirect(url_for("home.index"))

    return envoltura
