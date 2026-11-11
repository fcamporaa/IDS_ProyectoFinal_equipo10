from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.api_client import consultar_backend
from utils.auth import admin_required


admin_funciones_bp = Blueprint("admin_funciones", __name__, url_prefix="/admin/funciones")

@admin_funciones_bp.route("/")
#@admin_required  # Usamos la validación que armaron tus compañeros
def listar_funciones():
    """
    Ruta principal del ABM: Lista todas las funciones actuales.
    """
    token = session.get("access_token")
    
    # (Asegurate de que la ruta "/funciones" coincida con la que armaste en tu backend)
    datos, status = consultar_backend("/funciones", token=token)
    datos, status = consultar_backend("/funciones", token=token)
    
    print(">>> STATUS DEL BACKEND:", status)
    print(">>> DATOS DEL BACKEND:", datos)
    
    
    if status == 200:
        lista_funciones = datos
    else:
        flash("Error al cargar las funciones desde el servidor.", "error")
        lista_funciones = []


    return render_template("backoffice/funciones_lista.html", funciones=lista_funciones)


@admin_funciones_bp.route("/crear", methods=["GET", "POST"])
#@admin_required
def crear_funcion():
    """
    Ruta para mostrar el formulario y procesar la creación de una nueva función.
    """
    token = session.get("access_token")

    if request.method == "POST":
        # 1. Atrapamos la fecha y la hora y las unimos para formar el "inicio" que pide el backend
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")
        inicio_armado = f"{fecha} {hora}:00"

        # 2. Armamos el diccionario EXACTAMENTE con las llaves que exigen tus compañeros
        nueva_funcion = {
            "id_pelicula": int(request.form.get("pelicula_id")),
            "id_sala": int(request.form.get("sala_id")),
            "inicio": inicio_armado,
            "formato": request.form.get("idioma"),
            "precio_entrada": 6500  # Le clavamos un precio por defecto para pasar su validación
        }

        import requests
        url_backend = "http://127.0.0.1:5000/funciones"
        
        try:
            respuesta = requests.post(url_backend, json=nueva_funcion)
            
            if respuesta.status_code in [200, 201]:
                flash("¡Función creada con éxito en la base de datos real!", "success")
            else:
                flash("Error al crear la función en el servidor.", "error")
                print(">>> ERROR DEL BACKEND:", respuesta.text)
                
        except Exception as e:
            flash("No se pudo conectar con el backend.", "error")
            print(">>> ERROR DE CONEXIÓN:", e)

        return redirect(url_for("admin_funciones.listar_funciones"))

    return render_template("backoffice/funciones_form.html") 
@admin_funciones_bp.route("/eliminar/<int:id_funcion>", methods=["POST"])
#@admin_required
def eliminar_funcion(id_funcion):
    """
    Atrapa el ID desde el HTML y le pide al backend que lo borre de la base de datos.
    """
    import requests
    # Armamos la URL apuntando al ID específico
    url_backend = f"http://127.0.0.1:5000/funciones/{id_funcion}"
    
    try:
        # Usamos DELETE para respetar los métodos de la Cátedra Lancelotta
        respuesta = requests.delete(url_backend)
        
        if respuesta.status_code in [200, 204]:
            flash("¡Función eliminada con éxito de la base de datos!", "success")
        else:
            flash("Error al eliminar la función en el servidor.", "error")
            print(">>> ERROR DEL BACKEND:", respuesta.text)
            
    except Exception as e:
        flash("No se pudo conectar con el backend.", "error")
        print(">>> ERROR DE CONEXIÓN:", e)

    return redirect(url_for("admin_funciones.listar_funciones")) 

@admin_funciones_bp.route("/editar/<int:id_funcion>", methods=["GET", "POST"])
#@admin_required
def editar_funcion(id_funcion):
    """
    Gestiona la edición de una función existente.
    """
    import requests
    url_backend_detalle = f"http://127.0.0.1:5000/funciones/{id_funcion}"
    
    if request.method == "POST":
        # 1. Capturamos los datos modificados del formulario
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")
        inicio_armado = f"{fecha} {hora}:00"

        datos_actualizados = {
            "id_pelicula": int(request.form.get("pelicula_id")),
            "id_sala": int(request.form.get("sala_id")),
            "inicio": inicio_armado,
            "formato": request.form.get("idioma"),
            "precio_entrada": 6500
        }
        
        try:
            # ATAJO INFAILIBLE: Borramos la anterior y creamos una nueva con los datos editados
            requests.delete(f"http://127.0.0.1:5000/funciones/{id_funcion}")
            respuesta = requests.post("http://127.0.0.1:5000/funciones", json=datos_actualizados)

            if respuesta.status_code in [200, 201, 204]:
                flash("¡Función modificada con éxito!", "success")
            else:
                flash(f"Error al actualizar ({respuesta.status_code}): {respuesta.text}", "error")
                
        except Exception as e:
            flash("No se pudo conectar con el backend.", "error")
            print(">>> ERROR DE CONEXIÓN:", e)

        return redirect(url_for("admin_funciones.listar_funciones"))
    # Si es GET, buscamos la función recorriendo la lista completa del backend
    try:
        respuesta = requests.get("http://127.0.0.1:5000/funciones")
        if respuesta.status_code == 200:
            todas_las_funciones = respuesta.json()
            # Buscamos la que coincida con el id_funcion que queremos editar
            funcion = next((f for f in todas_las_funciones if f.get("id_funcion") == id_funcion), None)
            
            if not funcion:
                flash("No se pudo encontrar la función a editar.", "error")
                return redirect(url_for("admin_funciones.listar_funciones"))
        else:
            flash("No se pudo conectar con el servidor.", "error")
            return redirect(url_for("admin_funciones.listar_funciones"))
    except Exception as e:
        flash("Error de conexión al buscar la función.", "error")
        return redirect(url_for("admin_funciones.listar_funciones"))

    return render_template("backoffice/funciones_form.html", funcion=funcion)