from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from services.compras_service import (
    enviar_compra_al_backend, obtener_compra_del_backend,
    reenviar_comprobante_al_backend,
)
from utils.csrf import crear_token_csrf, validar_token_csrf
from validators.compras_validators import validar_formulario_compra

compras_bp = Blueprint("compras", __name__)


@compras_bp.route("/compra/checkout", methods=["GET"])
def checkout():
    return render_template("client/checkout.html", csrf_token=crear_token_csrf())


@compras_bp.route("/compra/confirmar", methods=["POST"])
def confirmar_compra():
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        return "Formulario vencido o CSRF inválido.", 400
    token = session.get("access_token")
    if not token:
        return "Falta iniciar sesión: integración con US-02 pendiente.", 401
    try:
        datos = validar_formulario_compra(request.form)
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("compras.checkout"))
    compra, estado = enviar_compra_al_backend(datos, token)
    if estado == 201 and isinstance(compra, dict) and type(compra.get("id_compra")) is int:
        return redirect(url_for("compras.compra_exitosa", id_compra=compra["id_compra"]))
    flash("No se pudo confirmar la compra. Revisá la función, las butacas y la sesión.", "error")
    return redirect(url_for("compras.checkout"))


@compras_bp.route("/compras/<int:id_compra>/confirmacion", methods=["GET"])
def compra_exitosa(id_compra: int):
    token = session.get("access_token")
    if not token:
        return "Debés iniciar sesión.", 401
    compra, estado = obtener_compra_del_backend(id_compra, token)
    if estado != 200 or not isinstance(compra, dict):
        return "Compra inexistente o no autorizada.", 404 if estado in (403, 404) else estado
    return render_template(
        "client/compra_exitosa.html",
        compra=compra,
        csrf_token=crear_token_csrf(),
    )


@compras_bp.route("/compras/<int:id_compra>/reenviar-email", methods=["POST"])
def reenviar_email(id_compra: int):
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida.", 400
    token = session.get("access_token")
    if not token:
        return "Debés iniciar sesión.", 401
    respuesta, estado = reenviar_comprobante_al_backend(id_compra, token)
    if estado == 200:
        flash("Solicitud de reenvío procesada.", "success")
    else:
        flash("No se pudo enviar el comprobante.", "error")
    return redirect(url_for("compras.compra_exitosa", id_compra=id_compra))
