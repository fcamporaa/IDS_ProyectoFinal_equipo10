from src.utils import construir_error_api
from datetime import datetime


def validar_id_funcion(id_funcion: int) -> int:
    """Valida que id_funcion sea un entero positivo."""
    if not isinstance(id_funcion, int) or id_funcion <= 0:
        raise ValueError("El id_funcion debe ser un entero positivo.")
    return id_funcion


def validar_filtros_funciones(args) -> dict:
    """Valida filtros para consultar funciones (por película, sala, fecha)."""
    filtros = {}
    if args.get("pelicula_id"): filtros["pelicula_id"] = int(args.get("pelicula_id"))
    if args.get("local_id"): filtros["local_id"] = int(args.get("local_id"))
    if args.get("fecha"): filtros["fecha"] = args.get("fecha")
    return filtros


def validar_crear_funcion(datos: dict) -> dict:
    """
    Valida campos obligatorios para programar función:
    - id_pelicula: int positivo
    - id_sala: int positivo
    - inicio: datetime formato único ISO
    - fin: datetime formato único ISO posterior a inicio
    - formato: 2D, 3D, o 4D
    - precio_entrada: decimal positivo
    """
    if not isinstance(datos.get("id_pelicula"), int) or datos["id_pelicula"] <= 0:
        raise ValueError("id_pelicula debe ser un entero positivo.")
    if not isinstance(datos.get("id_sala"), int) or datos["id_sala"] <= 0:
        raise ValueError("id_sala debe ser un entero positivo.")
        
    try:
        inicio = datetime.fromisoformat(str(datos.get("inicio")))
        fin = datetime.fromisoformat(str(datos.get("fin")))
    except ValueError:
        raise ValueError("inicio y fin deben tener formato ISO válido.")
        
    if fin <= inicio:
        raise ValueError("fin debe ser posterior a inicio.")
        
    if datos.get("formato") not in ["2D", "3D", "4D"]:
        raise ValueError("formato debe ser 2D, 3D, o 4D.")
        
    if float(datos.get("precio_entrada", 0)) <= 0:
        raise ValueError("precio_entrada debe ser un decimal positivo.")
        
    return datos


def validar_actualizar_funcion(datos: dict) -> dict:
    """Valida modificaciones de horario, precio o estado de función."""
    if not datos:
        raise ValueError("No se enviaron datos para actualizar.")
    # Si envían precio, validamos que sea positivo
    if "precio_entrada" in datos and float(datos["precio_entrada"]) <= 0:
        raise ValueError("precio_entrada debe ser un decimal positivo.")
    return datos