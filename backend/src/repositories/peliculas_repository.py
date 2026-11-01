from src.db import ejecutar_consulta, ejecutar_mutacion

# Una función es vigente si está programada o en curso y todavía no terminó
CONDICION_FUNCION_VIGENTE = (
    "f.estado IN ('PROGRAMADA', 'EN_CURSO') AND f.fin > NOW()"
)







def obtener_cartelera_vigente_db(filtros: dict = None) -> list[dict]:
    """
    Consulta las películas activas que tienen funciones vigentes.
    Admite los filtros opcionales id_genero, titulo (parcial) y clasificacion.
    """
    filtros = filtros or {}
    condiciones = [
        "p.activa = 1",
        "EXISTS (SELECT 1 FROM funciones f "
        f"WHERE f.id_pelicula = p.id_pelicula AND {CONDICION_FUNCION_VIGENTE})",
    ]
    parametros = []

    if "id_genero" in filtros:
        condiciones.append(
            "EXISTS (SELECT 1 FROM pelicula_generos pg "
            "WHERE pg.id_pelicula = p.id_pelicula AND pg.id_genero = %s)"
        )
        parametros.append(filtros["id_genero"])

    if "titulo" in filtros:
        condiciones.append("p.titulo LIKE %s")
        parametros.append(f"%{filtros['titulo']}%")

    if "clasificacion" in filtros:
        condiciones.append("p.clasificacion = %s")
        parametros.append(filtros["clasificacion"])

    # Solo se concatenan fragmentos fijos; todos los valores viajan como parámetros
    query = f"""
        SELECT p.id_pelicula, p.titulo, p.sinopsis, p.poster_url, p.trailer_url,
               p.duracion_min, p.clasificacion, p.anio_estreno, p.activa
        FROM peliculas p
        WHERE {" AND ".join(condiciones)}
        ORDER BY p.titulo;
    """
    return ejecutar_consulta(query, tuple(parametros))






def buscar_pelicula_por_id_db(id_pelicula: int) -> dict | None:
    """Obtiene datos de una película (activa o no) por su id_pelicula."""
    query = """
        SELECT id_pelicula, titulo, sinopsis, poster_url, trailer_url,
               duracion_min, clasificacion, anio_estreno, activa,
               origen_api, id_api
        FROM peliculas
        WHERE id_pelicula = %s;
    """
    resultados = ejecutar_consulta(query, (id_pelicula,))
    if resultados:
        return resultados[0]
    return None


def buscar_pelicula_por_api_db(origen_api: str, id_api: str) -> dict | None:
    """Busca una película (activa o no) por su origen externo y su id en esa API."""
    query = """
        SELECT id_pelicula, activa
        FROM peliculas
        WHERE origen_api = %s AND id_api = %s;
    """
    resultados = ejecutar_consulta(query, (origen_api, id_api))
    if resultados:
        return resultados[0]
    return None


def obtener_funciones_vigentes_por_pelicula_db(id_pelicula: int) -> list[dict]:
    """
    Obtiene las funciones vigentes de una película, ordenadas por inicio,
    con el título de la película, el número de sala y el nombre del local.
    """
    query = f"""
        SELECT f.id_funcion, f.id_pelicula, p.titulo AS titulo_pelicula,
               f.id_sala, s.numero AS numero_sala, l.nombre AS nombre_local,
               f.inicio, f.fin, f.formato, f.idioma, f.subtitulada,
               f.precio_entrada, f.estado
        FROM funciones f
        JOIN peliculas p ON p.id_pelicula = f.id_pelicula
        JOIN salas s ON s.id_sala = f.id_sala
        JOIN locales l ON l.id_local = s.id_local
        WHERE f.id_pelicula = %s AND {CONDICION_FUNCION_VIGENTE}
        ORDER BY f.inicio;
    """
    return ejecutar_consulta(query, (id_pelicula,))


def insertar_pelicula_db(datos: dict) -> int:
    """Inserta una película y devuelve su id autoincremental."""
    query = """
        INSERT INTO peliculas (origen_api, id_api, titulo, sinopsis, poster_url,
                               trailer_url, duracion_min, clasificacion, anio_estreno)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    valores = (
        datos["origen_api"],
        datos["id_api"],
        datos["titulo"],
        datos["sinopsis"],
        datos["poster_url"],
        datos["trailer_url"],
        datos["duracion_min"],
        datos["clasificacion"],
        datos["anio_estreno"],
    )
    return ejecutar_mutacion(query, valores)


def actualizar_pelicula_db(id_pelicula: int, datos: dict) -> int:
    """Actualiza los campos editables de una película (incluida activa) en la BD."""
    query = """
        UPDATE peliculas
        SET titulo = %s, sinopsis = %s, poster_url = %s, trailer_url = %s,
            duracion_min = %s, clasificacion = %s, anio_estreno = %s, activa = %s
        WHERE id_pelicula = %s;
    """
    valores = (
        datos["titulo"],
        datos["sinopsis"],
        datos["poster_url"],
        datos["trailer_url"],
        datos["duracion_min"],
        datos["clasificacion"],
        datos["anio_estreno"],
        int(datos["activa"]),
        id_pelicula,
    )
    return ejecutar_mutacion(query, valores)


def dar_de_baja_pelicula_db(id_pelicula: int) -> int:
    """Marca la película como inactiva (activa = 0)."""
    query = "UPDATE peliculas SET activa = 0 WHERE id_pelicula = %s;"
    return ejecutar_mutacion(query, (id_pelicula,))


def obtener_generos_db() -> list[dict]:
    """Obtiene todos los registros de la tabla generos."""
    query = "SELECT id_genero, nombre FROM generos ORDER BY nombre;"
    return ejecutar_consulta(query)


def obtener_generos_de_peliculas_db(ids_peliculas: list[int]) -> list[dict]:
    """
    Obtiene los géneros asociados a las películas indicadas.
    Cada fila trae id_pelicula, id_genero y nombre.
    """
    if not ids_peliculas:
        return []

    # Un %s por cada id; los valores viajan parametrizados, nunca concatenados
    marcadores = ", ".join(["%s"] * len(ids_peliculas))
    query = f"""
        SELECT pg.id_pelicula, g.id_genero, g.nombre
        FROM pelicula_generos pg
        JOIN generos g ON g.id_genero = pg.id_genero
        WHERE pg.id_pelicula IN ({marcadores})
        ORDER BY g.nombre;
    """
    return ejecutar_consulta(query, tuple(ids_peliculas))


def asociar_genero_a_pelicula_db(id_pelicula: int, id_genero: int) -> int:
    """Inserta en la tabla intermedia pelicula_generos."""
    query = "INSERT INTO pelicula_generos (id_pelicula, id_genero) VALUES (%s, %s);"
    return ejecutar_mutacion(query, (id_pelicula, id_genero))


def quitar_genero_de_pelicula_db(id_pelicula: int, id_genero: int) -> int:
    """Elimina una asociación de la tabla intermedia pelicula_generos."""
    query = "DELETE FROM pelicula_generos WHERE id_pelicula = %s AND id_genero = %s;"
    return ejecutar_mutacion(query, (id_pelicula, id_genero))

