from flask import Blueprint, render_template, request

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    mensaje_pendiente = (
        "El inicio de sesión todavía no está conectado."
        if request.method == "POST"
        else None
    )
    return render_template(
        "auth/login.html",
        mensaje_pendiente=mensaje_pendiente,
        ocultar_acceso_login=True,
    )


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    mensaje_pendiente = (
        "El registro todavía no está conectado."
        if request.method == "POST"
        else None
    )
    return render_template("auth/registro.html", mensaje_pendiente=mensaje_pendiente)