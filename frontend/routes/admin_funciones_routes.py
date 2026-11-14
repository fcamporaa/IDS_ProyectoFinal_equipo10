from flask import Blueprint, render_template, request, redirect, url_for, session
from utils.validaciones import validar_entero_positivo
from utils.auth import admin_required

# Importamos TODA la lógica desde nuestro nuevo archivo service
from services.funciones_service import (
    obtener_funciones, 
    obtener_funcion_por_id, 
    crear_funcion_service, 
    actualizar_funcion_service, 
    eliminar_funcion_service
)

admin_funciones_bp = Blueprint('admin_funciones', __name__, url_prefix='/admin/funciones')

@admin_funciones_bp.route('/')
@admin_required
def listar_funciones():
    token = session.get("access_token")
    # Delegamos el trabajo al service
    funciones = obtener_funciones(token)
    return render_template('backoffice/funciones_lista.html', funciones=funciones)

@admin_funciones_bp.route('/crear', methods=['GET', 'POST'])
@admin_required
def crear_funcion():
    if request.method == 'POST':
        token = session.get("access_token")
        datos = {
            "id_pelicula": validar_entero_positivo(request.form.get('id_pelicula')),
            "id_sala": validar_entero_positivo(request.form.get('id_sala')),
            "inicio": request.form.get('inicio'),
            "formato": request.form.get('formato'),
            "precio_entrada": validar_entero_positivo(request.form.get('precio_entrada', 6500))
        }
        
        # Le pasamos los datos al service y si sale bien, redirigimos
        if crear_funcion_service(datos, token):
            return redirect(url_for('admin_funciones.listar_funciones'))
        
    return render_template('backoffice/funciones_form.html')

@admin_funciones_bp.route('/editar/<int:id_funcion>', methods=['GET', 'POST'])
@admin_required
def editar_funcion(id_funcion):
    token = session.get("access_token")
    if request.method == 'POST':
        datos = {
            "inicio": request.form.get('inicio'),
            "precio_entrada": validar_entero_positivo(request.form.get('precio_entrada')),
            "estado": request.form.get('estado', 'ACTIVA')
        }
        
        if actualizar_funcion_service(id_funcion, datos, token):
            return redirect(url_for('admin_funciones.listar_funciones'))
        
    # Si es GET, buscamos la función para llenar el formulario
    funcion = obtener_funcion_por_id(id_funcion, token)
    return render_template('backoffice/funciones_form.html', funcion=funcion)

@admin_funciones_bp.route('/eliminar/<int:id_funcion>', methods=['POST'])
@admin_required
def eliminar_funcion(id_funcion):
    token = session.get("access_token")
    eliminar_funcion_service(id_funcion, token)
    return redirect(url_for('admin_funciones.listar_funciones'))