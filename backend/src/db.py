import pymysql
from pymysql.cursors import DictCursor
from .constants import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def obtener_conexion():
    """Crea y retorna una nueva conexión MySQL nativa usando DictCursor."""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )


def ejecutar_consulta(sql: str, parametros: dict = None) -> list[dict]:
    """
    Ejecuta una consulta SELECT con sentencias SQL nativas explícitas
    y devuelve todas las filas como una lista de diccionarios.
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros or {})
            return cursor.fetchall()
    finally:
        conexion.close()


def ejecutar_mutacion(sql: str, parametros: dict = None) -> int:
    """
    Ejecuta un INSERT, UPDATE o DELETE con sentencias SQL nativas explícitas.
    Realiza commit y retorna el ID autoincremental generado (o 0 si no aplica).
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros or {})
            ultimo_id = cursor.lastrowid or 0
        conexion.commit()
        return ultimo_id
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
