from src.db import ejecutar_consulta, ejecutar_mutacion

SELECT_FUNCION_DETALLE = """
    SELECT f.id_funcion, f.id_pelicula, p.titulo AS titulo_pelicula,
           f.id_sala, s.numero AS numero_sala, l.nombre AS nombre_local,
           f.inicio, f.fin, f.formato, f.idioma, f.subtitulada,
           f.precio_entrada, f.estado
    FROM funciones f
    JOIN peliculas p ON p.id_pelicula = f.id_pelicula
    JOIN salas s ON s.id_sala = f.id_sala
    JOIN locales l ON l.id_local = s.id_local
"""


def obtener_funciones_db(filtros: dict) -> list[dict]:
    """
    Lista funciones vigentes (no canceladas ni finalizadas, que no terminaron aún)
    con título de película, número de sala y nombre del local.
    Los filtros se agregan como condiciones fijas con valores parametrizados.
    """
    condiciones = ["f.estado IN ('PROGRAMADA', 'EN_CURSO')", "f.fin > %s"]
    parametros = [filtros["vigentes_desde"]]

    if "id_pelicula" in filtros:
        condiciones.append("f.id_pelicula = %s")
        parametros.append(filtros["id_pelicula"])
    if "id_local" in filtros:
        condiciones.append("s.id_local = %s")
        parametros.append(filtros["id_local"])
    if "formato" in filtros:
        condiciones.append("f.formato = %s")
        parametros.append(filtros["formato"])
    if "fecha" in filtros:
        condiciones.append("DATE(f.inicio) = %s")
        parametros.append(filtros["fecha"])

    query = SELECT_FUNCION_DETALLE + " WHERE " + " AND ".join(condiciones) + " ORDER BY f.inicio;"
    return ejecutar_consulta(query, tuple(parametros))


def buscar_funcion_por_id_db(id_funcion: int) -> dict | None:
    """Busca una función por id con los mismos datos que el listado."""
    resultados = ejecutar_consulta(
        SELECT_FUNCION_DETALLE + " WHERE f.id_funcion = %s;", (id_funcion,)
    )
    return resultados[0] if resultados else None


def buscar_pelicula_para_funcion_db(id_pelicula: int) -> dict | None:
    """Devuelve duracion_min y activa de la película, o None si no existe."""
    query = "SELECT duracion_min, activa FROM peliculas WHERE id_pelicula = %s;"
    resultados = ejecutar_consulta(query, (id_pelicula,))
    return resultados[0] if resultados else None


def buscar_sala_para_funcion_db(id_sala: int) -> dict | None:
    """Devuelve el campo activa de la sala, o None si no existe."""
    resultados = ejecutar_consulta("SELECT activa FROM salas WHERE id_sala = %s;", (id_sala,))
    return resultados[0] if resultados else None


def hay_solapamiento_horario_db(
    id_sala: int, inicio, fin, id_excluir: int | None = None
) -> bool:
    """
    Verifica si hay otra función no cancelada ni finalizada en la sala que se
    solape con [inicio, fin). Con id_excluir se ignora esa función (al editarla).
    """
    query = """
        SELECT COUNT(*) AS cantidad FROM funciones
        WHERE id_sala = %s AND estado NOT IN ('CANCELADA', 'FINALIZADA')
          AND inicio < %s AND fin > %s
          AND (%s IS NULL OR id_funcion != %s);
    """
    resultados = ejecutar_consulta(query, (id_sala, fin, inicio, id_excluir, id_excluir))
    return resultados[0]["cantidad"] > 0


def insertar_funcion_db(datos: dict) -> int:
    """Inserta una función en estado PROGRAMADA y devuelve su id."""
    query = """
        INSERT INTO funciones (id_pelicula, id_sala, inicio, fin, formato, idioma,
                               subtitulada, precio_entrada, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'PROGRAMADA');
    """
    valores = (
        datos["id_pelicula"],
        datos["id_sala"],
        datos["inicio"],
        datos["fin"],
        datos["formato"],
        datos["idioma"],
        datos["subtitulada"],
        datos["precio_entrada"],
    )
    return ejecutar_mutacion(query, valores)


def actualizar_funcion_db(id_funcion: int, datos: dict) -> int:
    """Actualiza inicio, fin, precio y estado (los únicos campos editables)."""
    query = """
        UPDATE funciones
        SET inicio = %s, fin = %s, precio_entrada = %s, estado = %s
        WHERE id_funcion = %s;
    """
    valores = (
        datos["inicio"],
        datos["fin"],
        datos["precio_entrada"],
        datos["estado"],
        id_funcion,
    )
    return ejecutar_mutacion(query, valores)


def tiene_entradas_activas_db(id_funcion: int) -> bool:
    """Verifica si la función tiene entradas vendidas o reservadas."""
    query = """
        SELECT COUNT(*) AS cantidad FROM entradas
        WHERE id_funcion = %s AND estado IN ('OCUPADA', 'RESERVADA');
    """
    resultados = ejecutar_consulta(query, (id_funcion,))
    return resultados[0]["cantidad"] > 0


def cancelar_funcion_db(id_funcion: int) -> int:
    """Cambia el estado de la función a CANCELADA."""
    query = "UPDATE funciones SET estado = 'CANCELADA' WHERE id_funcion = %s;"
    return ejecutar_mutacion(query, (id_funcion,))


def obtener_estado_butacas_funcion_db(id_funcion: int) -> list[dict]:
    """
    Butacas activas de la sala de la función con su estado para esa función.
    Solo cuentan entradas RESERVADA u OCUPADA: sin ellas la butaca está DISPONIBLE
    (las entradas canceladas o ya liberadas no la bloquean ni duplican filas).
    """
    query = """
        SELECT b.id_butaca, b.fila, b.numero,
               COALESCE(e.estado, 'DISPONIBLE') AS estado,
               e.id_entrada
        FROM funciones f
        JOIN butacas b ON b.id_sala = f.id_sala AND b.activa = 1
        LEFT JOIN entradas e ON e.id_funcion = f.id_funcion
                            AND e.id_butaca = b.id_butaca
                            AND e.estado IN ('RESERVADA', 'OCUPADA')
        WHERE f.id_funcion = %s
        ORDER BY b.fila, b.numero;
    """
    return ejecutar_consulta(query, (id_funcion,))
