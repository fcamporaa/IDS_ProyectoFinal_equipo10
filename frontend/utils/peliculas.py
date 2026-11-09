"""Prepara los datos de películas del backend para los templates (agrupa las funciones por complejo y día)."""
from datetime import datetime

from utils.formatos import (
    formatear_duracion,
    formatear_fecha_corta,
    formatear_hora,
    formatear_precio,
)


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


def adaptar_pelicula_para_card(p: dict) -> dict:
    """
    Pasa a card_pelicula.html solo lo que el backend informa en el listado.
    Lo que no viene (formato, sala, horarios) no se completa: el template lo oculta.
    """
    nombres = [g["nombre"] for g in p.get("generos", []) if g.get("nombre")]
    return {
        "id_pelicula": p["id_pelicula"],
        "titulo": p["titulo"],
        "poster_url": p.get("poster_url"),
        "clasificacion": p.get("clasificacion"),
        "duracion_min": p.get("duracion_min"),
        "genero": " / ".join(nombres),
        "genero_slug": " ".join(nombre.lower() for nombre in nombres),
    }


def _texto_idioma(funcion: dict) -> str:
    partes = [funcion["idioma"] or "", "subtitulada" if funcion["subtitulada"] else ""]
    return " ".join(filter(None, partes)).capitalize()


def armar_detalle_pelicula(pelicula: dict) -> dict:
    """
    Arma el contexto `p` de pelicula_detalle.html solo con datos del backend.
    Lo que el backend no informa (director, reparto, disponibilidad, etc.) no se completa:
    el template oculta esos campos. Cada grupo de sala lleva su complejo y su día en el nombre.
    """
    funciones = pelicula.get("funciones_vigentes", [])
    locales = agrupar_funciones(funciones)

    dias = sorted({datetime.fromisoformat(f["inicio"]).date() for f in funciones})
    fechas = [
        {"id": dia.isoformat(), "etiqueta": formatear_fecha_corta(dia), "activa": i == 0}
        for i, dia in enumerate(dias)
    ]

    complejos = [
        {
            "id": f"local-{i}",
            "nombre": local["nombre_local"],
            "badges": sorted(
                {fn["formato"] for fecha in local["fechas"] for fn in fecha["funciones"]}
            ),
            "seleccionado": i == 0,
        }
        for i, local in enumerate(locales)
    ]

    salas_funciones = []
    for local in locales:
        for fecha in local["fechas"]:
            por_sala = {}
            for fn in fecha["funciones"]:
                clave = (fn["numero_sala"], fn["formato"], fn["precio_entrada"])
                por_sala.setdefault(clave, []).append(fn)
            for (sala, formato, precio), lista in por_sala.items():
                salas_funciones.append(
                    {
                        "sala_id": sala,
                        "badge_tipo": formato,
                        "badge_clase": f"badge-{formato.lower()}",
                        "nombre": f"Sala {sala} — {local['nombre_local']} • {fecha['etiqueta']}",
                        "precio": formatear_precio(precio),
                        "funciones": [
                            {
                                "id_funcion": fn["id_funcion"],
                                "hora": fn["hora"],
                                "idioma": _texto_idioma(fn),
                                "seleccionada": False,
                            }
                            for fn in lista
                        ],
                    }
                )

    seleccion_inicial = {}
    if salas_funciones:
        primera = salas_funciones[0]
        primera["funciones"][0]["seleccionada"] = True
        seleccion_inicial = {
            "complejo": complejos[0]["nombre"],
            "fecha": fechas[0]["etiqueta"],
            "sala": f"Sala {primera['sala_id']} ({primera['badge_tipo']})",
            "hora": primera["funciones"][0]["hora"],
            "precio": primera["precio"],
            "id_funcion": primera["funciones"][0]["id_funcion"],
        }

    return {
        "id_pelicula": pelicula["id_pelicula"],
        "titulo": pelicula["titulo"],
        "poster_url": pelicula.get("poster_url"),
        "formato_destacado": " / ".join(sorted({f["formato"] for f in funciones})),
        "clasificacion": pelicula.get("clasificacion"),
        "duracion_legible": formatear_duracion(pelicula.get("duracion_min")),
        "anio": pelicula.get("anio_estreno"),
        "sinopsis": pelicula.get("sinopsis"),
        "generos": [g["nombre"] for g in pelicula.get("generos", [])],
        "trailer_url": pelicula.get("trailer_url"),
        "complejos": complejos,
        "fechas": fechas,
        "salas_funciones": salas_funciones,
        "seleccion_inicial": seleccion_inicial,
    }
