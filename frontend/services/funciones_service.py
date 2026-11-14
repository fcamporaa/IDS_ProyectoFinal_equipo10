from services.api_client import consultar_backend
from flask import flash

def obtener_funciones(token):
    datos, status = consultar_backend('/funciones', token=token)
    if status == 200:
        return datos
    flash("Error al cargar las funciones desde el servidor.", "error")
    return []

def obtener_funcion_por_id(id_funcion, token):
    datos, status = consultar_backend(f'/funciones/{id_funcion}', token=token)
    if status == 200:
        return datos
    flash("No se pudo encontrar la función a editar.", "error")
    return None

def crear_funcion_service(datos, token):
    respuesta, status = consultar_backend('/funciones', method='POST', data=datos, token=token)
    if status in [200, 201]:
        flash("¡Función creada con éxito!", "success")
        return True
    flash("Error al crear la función en el servidor.", "error")
    return False

def actualizar_funcion_service(id_funcion, datos, token):
    respuesta, status = consultar_backend(f'/funciones/{id_funcion}', method='PUT', data=datos, token=token)
    if status in [200, 204]:
        flash("¡Función modificada con éxito!", "success")
        return True
    flash("Error al actualizar la función.", "error")
    return False

def eliminar_funcion_service(id_funcion, token):
    respuesta, status = consultar_backend(f'/funciones/{id_funcion}', method='DELETE', token=token)
    if status in [200, 204]:
        flash("¡Función eliminada con éxito!", "success")
        return True
    flash("Error al eliminar la función.", "error")
    return False