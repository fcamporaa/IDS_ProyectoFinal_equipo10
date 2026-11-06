from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.api_client import consultar_backend
from utils.auth import admin_required


admin_funciones_bp = Blueprint("admin_funciones", __name__, url_prefix="/admin/funciones")

@admin_funciones_bp.route("/")
@admin_required  # Usamos la validación que armaron tus compañeros
def listar_funciones():
    """
    Ruta principal del ABM: Lista todas las funciones actuales.
    """
    token = session.get("access_token")
    
    # (Asegurate de que la ruta "/funciones" coincida con la que armaste en tu backend)
    datos, status = consultar_backend("/funciones", token=token)
    
    if status == 200:
        lista_funciones = datos
    else:
        flash("Error al cargar las funciones desde el servidor.", "error")
        lista_funciones = []


    return render_template("backoffice/funciones_lista.html", funciones=lista_funciones)


@admin_funciones_bp.route("/crear", methods=["GET", "POST"])
@admin_required
def crear_funcion():
    """
    Ruta para mostrar el formulario y procesar la creación de una nueva función.
    """
    token = session.get("access_token")
    
    if request.method == "POST":
        # Acá capturamos lo que el admin escribió en el formulario HTML
        # Por ejemplo: request.form.get("id_pelicula")
        
        # TODO: Enviar estos datos a tu backend con un POST para guardar la función.
        flash("Función creada con éxito (simulado).", "success")
        return redirect(url_for("admin_funciones.listar_funciones"))
        
    # Si es GET, mostramos el formulario vacío
    return render_template("backoffice/funciones_form.html")