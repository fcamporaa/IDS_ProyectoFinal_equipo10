from src.db import ejecutar_consulta, ejecutar_mutacion


def obtener_funciones_db(filtros: dict = None) -> list[dict]:
    """Obtiene las funciones con JOIN a peliculas y salas."""
    query = "SELECT * FROM funciones;"
    return ejecutar_consulta(query)


def buscar_funcion_por_id_db(id_funcion: int) -> dict | None:
    """Busca una función por su id_funcion."""
    query = "SELECT * FROM funciones WHERE id_funcion = %s;"
    # Le pasamos el ID como una tupla (id_funcion,) por seguridad
    resultados = ejecutar_consulta(query, (id_funcion,))
    
    # Si la lista tiene algo, devolvemos el primer diccionario. Si está vacía, devolvemos None.
    if resultados:
        return resultados[0]
    return None


def hay_solapamiento_horario_db(id_sala: int, inicio: str, fin: str, id_excluir: int = None) -> bool:
    """
    Verifica si existe alguna función programada o en curso en la misma sala
    que se solape con el intervalo [inicio, fin].
    """
    
    if id_excluir:
        # Se usa cuando estamos EDITANDO una función (no queremos que choque con otras, pero sí puede "chocar" consigo misma)
        query = """
            SELECT COUNT(*) as cantidad FROM funciones 
            WHERE id_sala = %s AND estado != 'CANCELADA' AND id_funcion != %s
            AND inicio < %s AND fin > %s;
        """
        resultados = ejecutar_consulta(query, (id_sala, id_excluir, fin, inicio))
    else:
        # Se usa cuando estamos CREANDO una función nueva
        query = """
            SELECT COUNT(*) as cantidad FROM funciones 
            WHERE id_sala = %s AND estado != 'CANCELADA'
            AND inicio < %s AND fin > %s;
        """
        resultados = ejecutar_consulta(query, (id_sala, fin, inicio))
        
    # Si la cantidad de choques es mayor a 0, devuelve True 
    return resultados[0]['cantidad'] > 0


def insertar_funcion_db(datos: dict) -> int:
    """Inserta una nueva función en la tabla funciones."""
    query = """
        INSERT INTO funciones (id_pelicula, id_sala, inicio, fin, formato, idioma, subtitulada, precio_entrada, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    valores = (
        datos['id_pelicula'],
        datos['id_sala'],
        datos['inicio'],
        datos['fin'],
        datos['formato'],
        datos['idioma'],
        datos['subtitulada'],
        datos['precio_entrada'],
        'PROGRAMADA'
    )
    return ejecutar_mutacion(query, valores)

def actualizar_funcion_db(id_funcion: int, datos: dict) -> int:
    """Actualiza una función existente."""
    query = """
        UPDATE funciones 
        SET id_pelicula = %s, id_sala = %s, inicio = %s, fin = %s, 
            formato = %s, idioma = %s, subtitulada = %s, precio_entrada = %s, estado = %s
        WHERE id_funcion = %s;
    """
    valores = (
        datos['id_pelicula'],
        datos['id_sala'],
        datos['inicio'],
        datos['fin'],
        datos['formato'],
        datos['idioma'],
        datos['subtitulada'],
        datos['precio_entrada'],
        datos.get('estado', 'PROGRAMADA'), # Por si en el JSON no mandan el estado
        id_funcion
    )
    return ejecutar_mutacion(query, valores)


def tiene_entradas_activas_db(id_funcion: int) -> bool:
    """Verifica si la función tiene entradas vendidas o reservadas."""
    query = """
        SELECT COUNT(*) as cantidad FROM entradas 
        WHERE id_funcion = %s AND estado IN ('VENDIDA', 'RESERVADA');
    """
    resultados = ejecutar_consulta(query, (id_funcion,))
    return resultados[0]['cantidad'] > 0


def cancelar_funcion_db(id_funcion: int) -> int:
    """Cambia el estado de la función a CANCELADA."""
    query = "UPDATE funciones SET estado = 'CANCELADA' WHERE id_funcion = %s;"
    return ejecutar_mutacion(query, (id_funcion,)) 


def obtener_estado_butacas_funcion_db(id_funcion: int) -> list[dict]:
    """
    Obtiene todas las butacas de la sala de la función con indicación
    de su estado (ocupada/reservada/libre) para esa función.
    """
    query = """
        SELECT b.id_butaca, b.fila, b.numero, 
               IF(e.id_entrada IS NULL, 'LIBRE', 'OCUPADA') as estado
        FROM funciones f
        JOIN butacas b ON f.id_sala = b.id_sala
        LEFT JOIN entradas e ON f.id_funcion = e.id_funcion AND b.id_butaca = e.id_butaca
        WHERE f.id_funcion = %s;
    """
    return ejecutar_consulta(query, (id_funcion,))
