from src.db import ejecutar_consulta, ejecutar_mutacion, ejecutar_transaccion

# Una función es vigente si está programada o en curso y todavía no terminó.
# El %s recibe la hora local actual (así coincide con el resto de la API, no con la del servidor MySQL)
CONDICION_FUNCION_VIGENTE = (
    "f.estado IN ('PROGRAMADA', 'EN_CURSO') AND f.fin > %s"
)

SQL_INSERTAR_PELICULA = """
    INSERT INTO peliculas (origen_api, id_api, titulo, sinopsis, poster_url,
                           trailer_url, duracion_min, clasificacion, anio_estreno)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

SQL_ACTUALIZAR_PELICULA = """
    UPDATE peliculas
    SET titulo = %s, sinopsis = %s, poster_url = %s, trailer_url = %s,
        duracion_min = %s, clasificacion = %s, anio_estreno = %s, activa = %s
    WHERE id_pelicula = %s;
"""

SQL_ASOCIAR_GENERO = "INSERT INTO pelicula_generos (id_pelicula, id_genero) VALUES (%s, %s);"

SQL_QUITAR_GENEROS = "DELETE FROM pelicula_generos WHERE id_pelicula = %s;"

SQL_INSERTAR_RESENA = """
    INSERT INTO resenas (id_usuario, id_pelicula, id_compra, puntuacion, comentario, creada_en)
    VALUES (%s, %s, %s, %s, %s, %s);
"""

# Columnas que devuelve cada reseña según el contrato del swagger (ResenaItem)
SQL_SELECCIONAR_RESENAS = """
    SELECT r.id_resena, r.id_usuario, u.nombre AS nombre_usuario,
           r.puntuacion, r.comentario, r.creada_en
    FROM resenas r
    JOIN usuarios u ON u.id_usuario = r.id_usuario
"""


def obtener_cartelera_vigente_db(filtros: dict) -> list[dict]:
    """
    Consulta las películas activas que tienen funciones vigentes a la hora
    filtros["vigentes_desde"]. Admite los filtros opcionales id_genero,
    titulo (parcial) y clasificacion.
    """
    condiciones = [
        "p.activa = 1",
        "EXISTS (SELECT 1 FROM funciones f "
        f"WHERE f.id_pelicula = p.id_pelicula AND {CONDICION_FUNCION_VIGENTE})",
    ]
    parametros = [filtros["vigentes_desde"]]

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


def obtener_funciones_vigentes_por_pelicula_db(id_pelicula: int, vigentes_desde) -> list[dict]:
    """
    Obtiene las funciones de una película vigentes a la hora vigentes_desde,
    ordenadas por inicio, con el título de la película, el número de sala
    y el nombre del local.
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
    return ejecutar_consulta(query, (id_pelicula, vigentes_desde))


def insertar_pelicula_db(datos: dict, ids_generos: list[int]) -> int:
    """
    Inserta una película y asocia sus géneros en una sola transacción:
    si algo falla no queda una película guardada a medias. Devuelve su id.
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

    def operacion(cursor):
        cursor.execute(SQL_INSERTAR_PELICULA, valores)
        id_pelicula = cursor.lastrowid
        cursor.executemany(
            SQL_ASOCIAR_GENERO, [(id_pelicula, id_genero) for id_genero in ids_generos]
        )
        return id_pelicula

    return ejecutar_transaccion(operacion)


def actualizar_pelicula_db(id_pelicula: int, datos: dict, ids_generos: list[int] | None = None) -> None:
    """
    Actualiza los campos editables de una película (incluida activa) y, si se
    indican ids_generos, reemplaza sus géneros, todo en una sola transacción.
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

    def operacion(cursor):
        cursor.execute(SQL_ACTUALIZAR_PELICULA, valores)
        if ids_generos is not None:
            cursor.execute(SQL_QUITAR_GENEROS, (id_pelicula,))
            cursor.executemany(
                SQL_ASOCIAR_GENERO, [(id_pelicula, id_genero) for id_genero in ids_generos]
            )

    ejecutar_transaccion(operacion)


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


def obtener_resenas_por_pelicula_db(id_pelicula: int) -> list[dict]:
    """Obtiene las reseñas de una película, de la más reciente a la más antigua."""
    query = f"""
        {SQL_SELECCIONAR_RESENAS}
        WHERE r.id_pelicula = %s
        ORDER BY r.creada_en DESC, r.id_resena DESC;
    """
    return ejecutar_consulta(query, (id_pelicula,))


def buscar_resena_por_id_db(id_resena: int) -> dict | None:
    """Obtiene una reseña (con el nombre de su autor) por su id_resena."""
    query = f"""
        {SQL_SELECCIONAR_RESENAS}
        WHERE r.id_resena = %s;
    """
    resultados = ejecutar_consulta(query, (id_resena,))
    if resultados:
        return resultados[0]
    return None


def buscar_compra_para_resena_db(id_compra: int) -> dict | None:
    """
    Obtiene los datos de una compra necesarios para saber si habilita una reseña:
    a quién pertenece, su estado, si su QR fue validado en puerta y de qué película es.
    """
    query = """
        SELECT c.id_compra, c.id_usuario, c.estado, c.qr_validado_en, f.id_pelicula
        FROM compras c
        JOIN funciones f ON f.id_funcion = c.id_funcion
        WHERE c.id_compra = %s;
    """
    resultados = ejecutar_consulta(query, (id_compra,))
    if resultados:
        return resultados[0]
    return None


def existe_resena_de_compra_db(id_compra: int) -> bool:
    """Indica si la compra ya tiene una reseña registrada."""
    query = "SELECT id_resena FROM resenas WHERE id_compra = %s LIMIT 1;"
    return len(ejecutar_consulta(query, (id_compra,))) > 0


def insertar_resena_db(datos: dict) -> int:
    """
    Inserta una reseña y retorna su id_resena. Espera id_usuario, id_pelicula,
    id_compra, puntuacion, comentario (puede ser None) y creada_en (datetime).
    """
    return ejecutar_mutacion(
        SQL_INSERTAR_RESENA,
        (
            datos["id_usuario"],
            datos["id_pelicula"],
            datos["id_compra"],
            datos["puntuacion"],
            datos["comentario"],
            datos["creada_en"],
        ),
    )
