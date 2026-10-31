from src.db import ejecutar_consulta, ejecutar_mutacion


def buscar_usuario_por_email_db(email: str) -> dict | None:
    """Busca un usuario en la tabla usuarios por su email."""
    query = """
        SELECT id_usuario, nombre, email, numero_socio, contrasena_hash, rol,
               fecha_registro, activo
        FROM usuarios
        WHERE email = %(email)s
    """
    resultados = ejecutar_consulta(query, {"email": email})
    return resultados[0] if resultados else None


def buscar_usuario_por_id_db(id_usuario: int) -> dict | None:
    """Busca un usuario por su id_usuario."""
    query = """
        SELECT id_usuario, nombre, email, numero_socio, rol, fecha_registro, activo
        FROM usuarios
        WHERE id_usuario = %(id_usuario)s
    """
    resultados = ejecutar_consulta(query, {"id_usuario": id_usuario})
    return resultados[0] if resultados else None


def insertar_usuario_db(datos: dict) -> int:
    """Inserta un nuevo usuario y retorna el id_usuario autoincremental."""
    query = """
        INSERT INTO usuarios (nombre, email, numero_socio, contrasena_hash, rol)
        VALUES (%(nombre)s, %(email)s, %(numero_socio)s, %(contrasena_hash)s, %(rol)s)
    """
    return ejecutar_mutacion(query, datos)


def actualizar_usuario_db(id_usuario: int, datos: dict) -> int:
    """Actualiza datos del usuario por su id_usuario."""
    columnas_permitidas = ("nombre", "contrasena_hash")
    campos_actualizables = [
        campo for campo in columnas_permitidas if campo in datos
    ]
    if not campos_actualizables:
        return 0

    asignaciones = ", ".join(
        f"{campo} = %({campo})s" for campo in campos_actualizables
    )
    query = f"""
        UPDATE usuarios
        SET {asignaciones}
        WHERE id_usuario = %(id_usuario)s
    """
    parametros = {campo: datos[campo] for campo in campos_actualizables}
    parametros["id_usuario"] = id_usuario
    return ejecutar_mutacion(query, parametros)
