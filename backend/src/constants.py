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
ESTADOS_COMPRA = {"PENDIENTE", "PAGADA", "CANCELADA"}
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


# ==========================================
# Dominio - Dashboard administrativo
# ==========================================
# Una butaca reservada también reduce la disponibilidad real de la sala.
ESTADOS_ENTRADA_OCUPACION = ("OCUPADA", "RESERVADA")
ESTADOS_ENTRADA_VENDIDA = ("OCUPADA",)
# Las compras PENDIENTES todavía no representan una venta ni una cancelación.
ESTADOS_COMPRA_DASHBOARD = ("PAGADA", "CANCELADA")
ESTADO_COMPRA_VENDIDA = "PAGADA"
ESTADO_COMPRA_CANCELADA = "CANCELADA"
ESTADO_FUNCION_CANCELADA = "CANCELADA"
FRANJAS_HORARIAS_DASHBOARD = (
    {"turno": "Mañana (06:00 - 11:59)", "horas": (6, 7, 8, 9, 10, 11)},
    {"turno": "Tarde (12:00 - 18:59)", "horas": (12, 13, 14, 15, 16, 17, 18)},
    {"turno": "Noche (19:00 - 22:59)", "horas": (19, 20, 21, 22)},
    {"turno": "Trasnoche (23:00 - 05:59)", "horas": (23, 0, 1, 2, 3, 4, 5)},
)

