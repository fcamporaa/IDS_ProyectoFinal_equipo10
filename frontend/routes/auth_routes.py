from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from services.auth_service import iniciar_sesion, registrar_usuario
from utils.errores import extraer_mensaje_error

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Procesa el inicio de sesión contra el backend y almacena la sesión."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        contrasena = request.form.get("contrasena", "").strip()

        if not email or not contrasena:
            flash("Por favor completá todos los campos.", "error")
            return render_template("auth/login.html", ocultar_acceso_login=True)

        respuesta, status = iniciar_sesion(email, contrasena)

        if status == 200 and isinstance(respuesta, dict) and "token" in respuesta:
            session["access_token"] = respuesta["token"]
            session["usuario"] = respuesta.get("usuario", {})
            usuario_nombre = respuesta.get("usuario", {}).get("nombre", "Usuario")
            flash(f"¡Bienvenido, {usuario_nombre}!", "success")

            # Si es admin, redirigir al Dashboard de métricas
            if respuesta.get("usuario", {}).get("rol") == "ADMINISTRADOR":
                return redirect(url_for("dashboard.index"))
            return redirect(url_for("home.index"))

        mensaje_error = extraer_mensaje_error(respuesta, "Credenciales inválidas.")
        flash(mensaje_error, "error")

    return render_template("auth/login.html", ocultar_acceso_login=True)


@auth_bp.route("/logout")
def logout():
    """Cierra la sesión activa y elimina las credenciales locales."""
    session.pop("access_token", None)
    session.pop("usuario", None)
    flash("Cerraste sesión correctamente.", "info")
    return redirect(url_for("home.index"))


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    mensaje_pendiente = None

    if request.method == "POST":
        contrasena = request.form.get("contrasena", "")
        confirmar_contrasena = request.form.get("confirmar_contrasena", "")

        if contrasena != confirmar_contrasena:
            mensaje_pendiente = "Las contraseñas no coinciden."
        else:
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "email": request.form.get("email", "").strip(),
                "contrasena": contrasena,
            }
            respuesta, estado = registrar_usuario(datos)

            if estado == 201:
                return redirect(url_for("auth.login"))

            errores = respuesta.get("errors", [])
            mensaje_pendiente = (
                errores[0].get("description")
                if errores
                else respuesta.get("error", "No se pudo completar el registro.")
            )

    return render_template(
        "auth/registro.html",
        mensaje_pendiente=mensaje_pendiente,
    )

