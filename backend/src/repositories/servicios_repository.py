from src.db import ejecutar_consulta, ejecutar_mutacion


def obtener_servicios_activos_db() -> list[dict]:
    """Obtiene todos los servicios donde activo = 1."""
    query = """
        SELECT id_servicio, nombre, tipo, precio, activo
        FROM servicios
        WHERE activo = 1
        ORDER BY nombre
    """
    return ejecutar_consulta(query)


def obtener_servicios_admin_db() -> list[dict]:
    """Obtiene todos los servicios, activos e inactivos, para el ABM."""
    query = """
        SELECT id_servicio, nombre, tipo, precio, activo
        FROM servicios
        ORDER BY activo DESC, nombre
    """
    return ejecutar_consulta(query)


def buscar_servicio_por_id_db(id_servicio: int) -> dict | None:
    """Busca un servicio por su id_servicio."""
    query = """
        SELECT id_servicio, nombre, tipo, precio, activo
        FROM servicios
        WHERE id_servicio = %(id_servicio)s
    """
    resultados = ejecutar_consulta(query, {"id_servicio": id_servicio})
    return resultados[0] if resultados else None


def buscar_servicio_por_nombre_db(nombre: str) -> dict | None:
    """Busca un servicio por su nombre."""
    query = """
        SELECT id_servicio, nombre, tipo, precio, activo
        FROM servicios
        WHERE nombre = %(nombre)s
        LIMIT 1
    """
    resultados = ejecutar_consulta(query, {"nombre": nombre})
    return resultados[0] if resultados else None


def insertar_servicio_db(datos: dict) -> int:
    """Inserta un nuevo servicio en la tabla servicios."""
    query = """
        INSERT INTO servicios (nombre, tipo, precio, activo)
        VALUES (%(nombre)s, %(tipo)s, %(precio)s, %(activo)s)
    """
    if "activo" not in datos:
        datos = dict(datos, activo=1)
    return ejecutar_mutacion(query, datos)


def actualizar_servicio_db(id_servicio: int, datos: dict) -> int:
    """Actualiza un servicio existente."""
    columnas_permitidas = ("nombre", "tipo", "precio", "activo")
    campos_actualizables = [campo for campo in columnas_permitidas if campo in datos]
    if not campos_actualizables:
        return 0

    asignaciones = ", ".join(
        f"{campo} = %({campo})s" for campo in campos_actualizables
    )
    query = f"""
        UPDATE servicios
        SET {asignaciones}
        WHERE id_servicio = %(id_servicio)s
    """
    parametros = {campo: datos[campo] for campo in campos_actualizables}
    parametros["id_servicio"] = id_servicio
    return ejecutar_mutacion(query, parametros)


def dar_de_baja_servicio_db(id_servicio: int) -> bool:
    """Marca el servicio como inactivo y confirma su estado persistido."""
    query = """
        UPDATE servicios
        SET activo = 0
        WHERE id_servicio = %(id_servicio)s
          AND activo = 1
    """
    ejecutar_mutacion(query, {"id_servicio": id_servicio})

    servicio = buscar_servicio_por_id_db(id_servicio)
    return servicio is not None and not servicio["activo"]
