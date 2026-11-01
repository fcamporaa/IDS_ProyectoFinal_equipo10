from src.db import ejecutar_consulta, ejecutar_mutacion


def obtener_funciones_db(filtros: dict = None) -> list[dict]:
    """Obtiene las funciones con JOIN a peliculas y salas."""
    pass


def buscar_funcion_por_id_db(id_funcion: int) -> dict | None:
    """Busca una función por su id_funcion."""
    pass


def hay_solapamiento_horario_db(id_sala: int, inicio: str, fin: str, id_excluir: int = None) -> bool:
    """
    Verifica si existe alguna función programada o en curso en la misma sala
    que se solape con el intervalo [inicio, fin].
    """
    pass


def insertar_funcion_db(datos: dict) -> int:
    """Inserta una nueva función en la tabla funciones."""
    pass


def actualizar_funcion_db(id_funcion: int, datos: dict) -> int:
    """Actualiza una función existente."""
    pass


def tiene_entradas_activas_db(id_funcion: int) -> bool:
    """Verifica si la función tiene entradas vendidas o reservadas."""
    pass


def cancelar_funcion_db(id_funcion: int) -> int:
    """Cambia el estado de la función a CANCELADA."""
    pass


def obtener_estado_butacas_funcion_db(id_funcion: int) -> list[dict]:
    """
    Obtiene todas las butacas de la sala de la función con indicación
    de su estado (ocupada/reservada/libre) para esa función.
    """
    pass
