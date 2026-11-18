from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from services.compras_service import (
    enviar_compra_al_backend, obtener_compra_del_backend,
    reenviar_comprobante_al_backend)
from utils.csrf import crear_token_csrf, validar_token_csrf
from validators.compras_validators import validar_formulario_compra
from services.peliculas_service import obtener_detalle_pelicula
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
from services.compras_service import (
    enviar_compra_al_backend,
    obtener_compra_del_backend,
    reenviar_comprobante_al_backend,
    cancelar_compra_al_backend)
import base64
import io
import qrcode
from utils.temporizador_compra import (
    limpiar_compra_temporal,
    redirigir_compra_expirada,
    temporizador_compra_vencido,
)

compras_bp = Blueprint("compras", __name__)

@compras_bp.route("/compra/confirmar", methods=["POST"])
def confirmar_compra():
    if temporizador_compra_vencido():
        return redirigir_compra_expirada()
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        return "Formulario vencido o CSRF inválido.", 400
    token = session.get("access_token")
    if not token:
        flash("Necesitás iniciar sesión antes de comprar. El login web pertenece a US-02.", "error")
        return redirect(url_for("home.index"))
    try:
        datos = validar_formulario_compra(
        request.form,
        session.get("compra", {}).get("servicios", [])
        )
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("compra.seleccion_checkout"))
    compra, estado = enviar_compra_al_backend(datos, token)
    if estado == 201 and isinstance(compra, dict) and type(compra.get("id_compra")) is int:
        limpiar_compra_temporal()
        return redirect(url_for("compras.compra_exitosa", id_compra=compra["id_compra"]))
    flash("No se pudo confirmar la compra. Revisá la función, las butacas y la sesión.", "error")
    return redirect(url_for("compra.seleccion_checkout"))


@compras_bp.route("/compras/<int:id_compra>/confirmacion", methods=["GET"])
def compra_exitosa(id_compra: int):

    token = session.get("access_token")

    if not token:
        flash("Debés iniciar sesión.", "error")
        return redirect(url_for("auth.login"))

    # Obtener la compra real desde MySQL
    compra, estado = obtener_compra_del_backend(id_compra, token)

    if estado != 200 or not isinstance(compra, dict):
        flash("No se pudo obtener el comprobante.", "error")
        return redirect(url_for("home.index"))

    funcion = compra["funcion"]
    entradas = compra.get("entradas", [])
    servicios = compra.get("servicios", [])

    # Formatear importes
    def formatear_precio(valor):
        numero = float(valor or 0)
        entero, centavos = f"{numero:,.2f}".split(".")
        resultado = f"${entero.replace(',', '.')}"

        if centavos != "00":
            resultado += f",{centavos}"

        return resultado

    # Obtener información adicional de la película
    pelicula = obtener_detalle_pelicula(funcion["id_pelicula"]) or {}

    # Interpretar fecha y horario de la función
    inicio_texto = str(funcion.get("inicio") or "")
    fecha_funcion = None

    try:
        fecha_funcion = datetime.fromisoformat(
            inicio_texto.replace("Z", "+00:00")
        )
    except ValueError:
        try:
            fecha_funcion = parsedate_to_datetime(inicio_texto)
        except (ValueError, TypeError):
            pass

    fecha = (
        fecha_funcion.strftime("%d/%m/%Y")
        if fecha_funcion else inicio_texto
    )

    horario = (
        fecha_funcion.strftime("%H:%M hs")
        if fecha_funcion else ""
    )

    limite_cancelacion = (
        (fecha_funcion - timedelta(hours=24)).strftime("%d/%m/%Y %H:%M")
        if fecha_funcion else "24 horas antes de la función"
    )

    puede_cancelar = (
    compra.get("estado") == "PAGADA"
    and not compra.get("qr_validado_en")
    and fecha_funcion is not None
    and fecha_funcion > (
        datetime.now(fecha_funcion.tzinfo)
        + timedelta(hours=24)
    )
    )

    # Construir descripción de las butacas
    butacas = ", ".join(
        f"{entrada['fila']}-{entrada['numero']}"
        for entrada in entradas
    )

    # Construir el detalle de la compra
    items = [
        {
            "descripcion": f"{len(entradas)}x Entrada ({butacas})",
            "monto": formatear_precio(compra["subtotal_entradas"]),
        }
    ]

    for servicio in servicios:
        items.append({
            "descripcion": (
                f"{servicio['cantidad']}x "
                f"{servicio['nombre_servicio']}"
            ),
            "monto": formatear_precio(servicio["subtotal"]),
        })

    # Servicios adicionales para las tarjetas del voucher
    adicionales = [
        {
            "tipo": "combo",
            "nombre": (
                f"{servicio['cantidad']}x "
                f"{servicio['nombre_servicio']}"
            ),
            "detalle": (
                "Precio unitario: "
                + formatear_precio(servicio["precio_unitario"])
            ),
            "subdetalle": None,
            "estado": "Incluido",
            "icono": "combo",
        }
        for servicio in servicios
    ]

    # Crear imagen del QR usando el token real
    qr_base64 = None

    if (
        compra.get("estado") == "PAGADA"
        and compra.get("qr_token")
        and not compra.get("qr_validado_en")
    ):
        imagen = qrcode.make(compra["qr_token"])
        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")

        qr_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

    duracion = pelicula.get("duracion_min")

    datos_confirmacion = {

        "id_compra": id_compra,
        "id_transaccion": compra["codigo_reserva"],
        "estado": compra["estado"],
        "email_comprador": compra["email_comprobante"],
        "codigo_qr": compra["codigo_reserva"],
        "qr_base64": qr_base64,

        "pelicula": {
            "id_pelicula": funcion["id_pelicula"],
            "titulo": funcion["titulo_pelicula"],
            "poster_url": pelicula.get("poster_url") or "",
            "badge_poster": funcion.get("formato") or "",
            "clasificacion": pelicula.get("clasificacion") or "",
            "duracion": f"{duracion} MIN" if duracion else "",
            "formato_sala": funcion.get("formato") or "",
            "idioma": funcion.get("idioma") or "",
            "direccion_sonido": "",
            "fecha": fecha,
            "horario": horario,
            "complejo": funcion["nombre_local"],
            "sala_nombre": f"Sala {funcion['numero_sala']}",
            "butacas": butacas,
            "badge_butacas": funcion.get("formato") or "",
        },

        "facturacion": {
            "tipo": "COMPRA SIMULADA",
            "items": items,
            "cargo_servicio": "100% BONIFICADO",
            "cargo_servicio_monto": formatear_precio(
                compra.get("cargo_servicio", 0)
            ),
            "total": formatear_precio(compra["total"]),
            "iva_discriminado": None,
            "tarjeta_info": "Pago simulado",
            "cuotas_info": "Sin transacción bancaria",
            "cae": None,
            "vto_cae": None,
        },

        "adicionales": adicionales,

        "cancelacion": {
            "limite_texto": limite_cancelacion,
            "habilitada": puede_cancelar,
        },
    }

    return render_template(
        "confirmacion_compra.html",
        c=datos_confirmacion,
        csrf_token=crear_token_csrf()
    )


@compras_bp.route("/compras/<int:id_compra>/reenviar-email", methods=["POST"])
def reenviar_email(id_compra: int):
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida.", 400
    token = session.get("access_token")
    if not token:
        flash("Necesitás iniciar sesión antes de comprar. El login web pertenece a US-02.", "error")
        return redirect(url_for("home.index"))
    respuesta, estado = reenviar_comprobante_al_backend(id_compra, token)
    if estado == 200:
        flash("Solicitud de reenvío procesada.", "success")
    else:
        flash("No se pudo enviar el comprobante.", "error")
    return redirect(url_for("compras.compra_exitosa", id_compra=id_compra))


@compras_bp.route("/compras/<int:id_compra>/cancelar", methods=["POST"])
def cancelar_compra_web(id_compra: int):
    """
    Recibe la solicitud de cancelación del usuario
    y la envía al backend mediante PUT.
    """

    # 1. Validar el token CSRF
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        flash("Formulario vencido o inválido.", "error")
        return redirect(
            url_for("compras.compra_exitosa", id_compra=id_compra)
        )

    # 2. Verificar autenticación
    token = session.get("access_token")

    if not token:
        flash("Debés iniciar sesión para cancelar la compra.", "error")
        return redirect(url_for("auth.login"))

    # 3. Solicitar la cancelación al backend
    respuesta, estado = cancelar_compra_al_backend(id_compra, token)

    # 4. Procesar el resultado
    if (
        estado == 200
        and isinstance(respuesta, dict)
        and respuesta.get("estado") == "CANCELADA"
    ):
        flash("La compra fue cancelada correctamente.", "success")

    else:
        mensaje = "No se pudo cancelar la compra."

        if isinstance(respuesta, dict):
            errores = respuesta.get("errors", [])

            if errores:
                mensaje = (
                    errores[0].get("description")
                    or errores[0].get("message")
                    or mensaje
                )

        flash(mensaje, "error")

    # 5. Volver al comprobante actualizado
    return redirect(
        url_for("compras.compra_exitosa", id_compra=id_compra)
    )