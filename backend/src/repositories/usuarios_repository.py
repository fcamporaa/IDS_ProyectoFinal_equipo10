from src.db import ejecutar_consulta, ejecutar_mutacion


def buscar_usuario_por_email_db(email: str) -> dict | None:
    """Busca un usuario en la tabla usuarios por su email."""
    # query = "SELECT id_usuario, nombre, email, contrasena_hash, rol, activo FROM usuarios WHERE email = :email"
    pass


def buscar_usuario_por_id_db(id_usuario: int) -> dict | None:
    """Busca un usuario por su id_usuario."""
    # query = "SELECT id_usuario, nombre, email, numero_socio, rol, fecha_registro, activo FROM usuarios WHERE id_usuario = :id"
    pass


def insertar_usuario_db(datos: dict) -> int:
    """Inserta un nuevo usuario y retorna el id_usuario autoincremental."""
    # query = "INSERT INTO usuarios (nombre, email, contrasena_hash, rol) VALUES (:nombre, :email, :contrasena_hash, :rol)"
    pass


def actualizar_usuario_db(id_usuario: int, datos: dict) -> int:
    """Actualiza datos del usuario por su id_usuario."""
    pass
