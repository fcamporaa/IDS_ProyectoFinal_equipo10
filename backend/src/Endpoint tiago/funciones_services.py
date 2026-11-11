from src.repositories.funciones_repository import (
    obtener_funciones_db,
    buscar_funcion_por_id_db,
    hay_solapamiento_horario_db,
    insertar_funcion_db,
    actualizar_funcion_db,
    tiene_entradas_activas_db,
    cancelar_funcion_db,
    obtener_estado_butacas_funcion_db,
)
from src.utils import construir_error_api 
from datetime import datetime, timedelta
from src.validators.funciones_validators import validar_crear_funcion, validar_actualizar_funcion

def listar_funciones(filtros: dict) -> list[dict]:
    """Lista las funciones programadas filtradas."""
    # Llamamos a tu función del repositorio y devolvemos la lista directamente
    return obtener_funciones_db(filtros)


def crear_funcion(datos: dict) -> dict:
    """Programa una nueva función validando que la sala esté libre."""
    
    # 1. Calculamos el horario de fin sumando 2 horas al inicio (requerido por tu DB)
    inicio_dt = datetime.strptime(datos["fecha_hora_funcion"], "%Y-%m-%d %H:%M:%S")
    fin_str = (inicio_dt + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")

    # 2. Armamos el diccionario con los 8 campos que pide tu base de datos
    datos_db = {
        "id_pelicula": datos["pelicula_id"],
        "id_sala": datos["sala_id"],
        "inicio": datos["fecha_hora_funcion"],
        "fin": fin_str,
        "formato": "2D",
        "idioma": "ESP",
        "subtitulada": False,
        "precio_entrada": datos["precio_base"]
    }
    validar_crear_funcion(datos_db)
    # 3. Validación real contra la base de datos
    if hay_solapamiento_horario_db(datos_db["id_sala"], datos_db["inicio"], datos_db["fin"]):
        raise ValueError("Conflicto - la sala ya se encuentra ocupada en ese horario")

    insertar_funcion_db(datos_db)
    
    # Devolvemos un dict vacío para cumplir con el Swagger (sin JSON extra)
    return {}

def actualizar_funcion(id_funcion: int, datos: dict) -> None:
    """Modifica horario, precio o estado de la función."""
    # Acá también armamos los datos para la DB
    datos_db = {
        "id_pelicula": datos.get("pelicula_id"),
        "id_sala": datos.get("sala_id"),
        "inicio": datos.get("fecha_hora_funcion"),
        "fin": "2026-10-25 23:00:00", # TODO: Calcular dinámicamente si se actualiza la fecha
        "formato": "2D",
        "idioma": "ESP",
        "subtitulada": False,
        "precio_entrada": datos.get("precio_base")
    }
    validar_actualizar_funcion(datos_db)
    actualizar_funcion_db(id_funcion, datos_db)

def eliminar_funcion(id_funcion: int) -> None:
    """Cancela o da de baja una función programada sin entradas activas."""
    # Validación real: si hay entradas, explota y frena la eliminación
    if tiene_entradas_activas_db(id_funcion):
        raise ValueError("No se puede cancelar: hay entradas vendidas")
        
    cancelar_funcion_db(id_funcion)

def obtener_mapa_butacas_funcion(id_funcion: int) -> dict:
    """Devuelve el mapa de butacas de la sala indicando libres y ocupadas."""
    return obtener_estado_butacas_funcion_db(id_funcion)