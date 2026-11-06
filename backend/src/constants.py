import os
from dotenv import load_dotenv
from datetime import timedelta, timezone

load_dotenv()

# ==========================================
# Configuración de Base de Datos MySQL
# ==========================================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "proyecto_integrador")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ACCESS_TOKEN_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "60"))

# ==========================================
# Formatos de Fecha y Hora
# ==========================================
FORMATO_FECHA_ISO = "%Y-%m-%dT%H:%M:%S.%f-03:00"
FORMATO_FECHA_CORTO = "%Y-%m-%d"
FORMATO_DATETIME_SQL = "%Y-%m-%d %H:%M:%S"

# ==========================================
# Expresiones Regulares de Validación
# ==========================================
PATRON_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PATRON_HORA_PUNTO = r"^([01]\d|2[0-3]):00:00$"
PATRON_FECHA_HORA_ISO = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(-03:00|Z)?$"

# ==========================================
# Constantes de Dominio - Cine Paradiso
# ==========================================
ROLES_USUARIOS = {"CLIENTE", "ADMINISTRADOR"}
ROL_ADMINISTRADOR = "ADMINISTRADOR"
ESTADOS_COMPRA = {"PENDIENTE", "PAGADA", "CANCELADA"}
PUNTUACION_RESENA_MIN = 1
PUNTUACION_RESENA_MAX = 5
LARGO_MAX_COMENTARIO_RESENA = 1000
ESTADOS_ENTRADA = {"DISPONIBLE", "RESERVADA", "OCUPADA", "CANCELADA"}
ESTADOS_FUNCION = {"PROGRAMADA", "EN_CURSO", "CANCELADA", "FINALIZADA"}
FORMATOS_SALA = {"2D", "3D", "4D"}
TIPOS_SERVICIO = {"COMIDA", "BEBIDA"}
ORIGENES_API_PELICULAS = {"OMDB", "TMDB", "CUSTOM"}
RESULTADOS_VALIDACION_QR = {"EXITO", "FALLIDO", "REUTILIZADO"}

# ==========================================
# API externa de películas (OMDb)
# ==========================================
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")
OMDB_URL = "https://www.omdbapi.com/"
OMDB_TIMEOUT_SEGUNDOS = 10
# Respuestas de OMDb que significan "sin resultados" y no un error del servicio
OMDB_ERRORES_SIN_RESULTADOS = {"Movie not found!", "Too many results."}
# """ OJITO, NO OLVIDEN DE PONER UNA KEY DE OMDb. SI NO SALTA 500 """


# ==========================================
# Dominio - Funciones
# ==========================================
ZONA_HORARIA_LOCAL = timezone(timedelta(hours=-3))
DURACION_FUNCION_POR_DEFECTO_MIN = 120
ESTADOS_FUNCION_TERMINALES = {"CANCELADA", "FINALIZADA"}

