"""Prepara los datos de películas del backend para los templates (agrupa las funciones por complejo y día)."""
from datetime import datetime

from utils.formatos import formatear_fecha_corta, formatear_hora


def agrupar_funciones(funciones: list[dict]) -> list[dict]:
    """
    Convierte la lista plana `funciones_vigentes` del detalle en:
    [{"nombre_local": ..., "fechas": [{"etiqueta": "Dom 15 Nov", "funciones": [...]}]}]
    Los complejos salen ordenados por nombre, y los días y las funciones por fecha de inicio.
    Se agrupa por nombre_local porque el endpoint no devuelve el id del local.
    """
    ordenadas = sorted(
        ((datetime.fromisoformat(f["inicio"]), f) for f in funciones),
        key=lambda par: par[0],
    )

    por_local = {}
    for inicio, funcion in ordenadas:
        dias = por_local.setdefault(funcion["nombre_local"], {})
        dias.setdefault(inicio.date(), []).append(
            {
                "id_funcion": funcion["id_funcion"],
                "hora": formatear_hora(inicio),
                "numero_sala": funcion["numero_sala"],
                "formato": funcion["formato"],
                "idioma": funcion["idioma"],
                "subtitulada": funcion["subtitulada"],
                "precio_entrada": funcion["precio_entrada"],
            }
        )

    return [
        {
            "nombre_local": nombre_local,
            "fechas": [
                {"etiqueta": formatear_fecha_corta(dia), "funciones": lista}
                for dia, lista in dias.items()
            ],
        }
        for nombre_local, dias in sorted(por_local.items())
    ]
