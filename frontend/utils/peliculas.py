"""Prepara los datos de películas del backend para los templates (agrupa funciones y mapea géneros)."""
from datetime import datetime
import unicodedata

from utils.formatos import (
    formatear_duracion,
    formatear_fecha_corta,
    formatear_hora,
    formatear_precio,
)


# Géneros de OMDb (normalizados sin acentos y en minúsculas) -> nombre local.
MAPEO_GENEROS_OMDB = {
    "action": "Acción",
    "adventure": "Aventura",
    "animation": "Animación",
    "comedy": "Comedia",
    "drama": "Drama",
    "horror": "Terror",
    "sci-fi": "Ciencia Ficción",
    "science fiction": "Ciencia Ficción",
    "thriller": "Suspenso",
    "mystery": "Suspenso",
    "crime": "Suspenso",
}


def _normalizar_genero(nombre: str) -> str:
    """Quita acentos, espacios sobrantes y mayúsculas para comparar nombres de género."""
    sin_acentos = unicodedata.normalize("NFKD", str(nombre or ""))
    return "".join(
        letra for letra in sin_acentos if not unicodedata.combining(letra)
    ).strip().lower()


def mapear_generos_externos(
    nombres_externos: list[str], generos_disponibles: list[dict]
) -> tuple[list[int], list[str]]:
    """
    Traduce los géneros de OMDb a ids locales.
    Devuelve (ids_sugeridos, nombres_sin_equivalente). No falla si falta un género.
    """
    ids_por_nombre = {
        _normalizar_genero(genero.get("nombre")): genero.get("id_genero")
        for genero in generos_disponibles
        if isinstance(genero, dict)
    }
    ids_sugeridos = []
    sin_equivalente = []

    for nombre_externo in nombres_externos or []:
        clave = _normalizar_genero(nombre_externo)
        nombre_local = MAPEO_GENEROS_OMDB.get(clave) or nombre_externo
        id_genero = ids_por_nombre.get(_normalizar_genero(nombre_local))

        if id_genero is None:
            if nombre_externo not in sin_equivalente:
                sin_equivalente.append(nombre_externo)
            continue
        if id_genero not in ids_sugeridos:
            ids_sugeridos.append(id_genero)

    return ids_sugeridos, sin_equivalente


def agrupar_funciones(funciones: list[dict]) -> list[dict]:
    """
    Convierte la lista plana `funciones_vigentes` del detalle en:
    [{"nombre_local": ..., "fechas": [{"etiqueta": "Dom 15 Nov", "funciones": [...]}]}]
    Los complejos salen ordenados por nombre, y los días y las funciones por fecha de inicio.
    Se agrupa por nombre_local porque el endpoint no devuelve el id del local.
    Cada complejo lleva un `id` propio ("local-0", ...) y cada día el suyo (fecha ISO):
    son los ids que usa el template para vincular tarjetas, fechas y funciones.
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
            "id": f"local-{indice}",
            "nombre_local": nombre_local,
            "fechas": [
                {
                    "id": dia.isoformat(),
                    "etiqueta": formatear_fecha_corta(dia),
                    "funciones": lista,
                }
                for dia, lista in dias.items()
            ],
        }
        for indice, (nombre_local, dias) in enumerate(sorted(por_local.items()))
    ]


def adaptar_pelicula_para_card(p: dict) -> dict:
    """
    Pasa a card_pelicula.html solo lo que el backend informa en el listado.
    Lo que no viene (formato, sala, horarios) no se completa: el template lo oculta.
    """
    generos = [
        genero for genero in p.get("generos", []) if isinstance(genero, dict)
    ]
    nombres = [genero["nombre"] for genero in generos if genero.get("nombre")]
    return {
        "sinopsis": p.get("sinopsis"),
        "backdrop_url": p.get("backdrop_url") or p.get("poster_url"),
        "anio_estreno": p.get("anio_estreno"),
        "id_pelicula": p["id_pelicula"],
        "titulo": p["titulo"],
        "poster_url": p.get("poster_url"),
        "clasificacion": p.get("clasificacion"),
        "duracion_min": p.get("duracion_min"),
        "genero": " / ".join(nombres),
        "generos_ids": [
            genero["id_genero"]
            for genero in generos
            if genero.get("id_genero") is not None
        ],
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

    etiquetas_por_fecha = {
        fecha["id"]: fecha["etiqueta"] for local in locales for fecha in local["fechas"]
    }
    fechas = [
        {"id": id_fecha, "etiqueta": etiqueta, "activa": False}
        for id_fecha, etiqueta in sorted(etiquetas_por_fecha.items())
    ]

    complejos = [
        {
            "id": local["id"],
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
                        "complejo_id": local["id"],
                        "fecha_id": fecha["id"],
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
        for fecha in fechas:
            fecha["activa"] = fecha["id"] == primera["fecha_id"]
        seleccion_inicial = {
            "complejo": complejos[0]["nombre"],
            "fecha": next(f["etiqueta"] for f in fechas if f["activa"]),
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


def _formatear_fecha_resena(valor) -> str:
    """Formatea la fecha de la reseña a un formato legible en español como '20 Nov 2026'."""
    if not valor:
        return ""
    if isinstance(valor, datetime):
        fecha = valor
    else:
        try:
            texto = str(valor).replace("Z", "").split(".")[0]
            fecha = datetime.fromisoformat(texto)
        except (ValueError, TypeError):
            return str(valor)[:10]

    meses = ("Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic")
    return f"{fecha.day} {meses[fecha.month - 1]} {fecha.year}"


def procesar_resenas(resenas_raw: list[dict], id_usuario_actual: int | None = None) -> dict:
    """
    Calcula métricas y formatea las reseñas para su renderizado en plantillas Jinja2.
    Retorna diccionario con:
    - promedio: float redondeado a 1 decimal o None
    - estrellas_promedio: int de 0 a 5 para dibujo de estrellas
    - total: cantidad total de reseñas
    - resenas: lista formateada de reseñas
    - resena_propia: la reseña realizada por el usuario logueado si existe
    """
    if not resenas_raw or not isinstance(resenas_raw, list):
        return {
            "promedio": None,
            "estrellas_promedio": 0,
            "total": 0,
            "resenas": [],
            "resena_propia": None,
        }

    resenas_formateadas = []
    suma_puntuacion = 0
    resena_propia = None

    for r in resenas_raw:
        if not isinstance(r, dict):
            continue
        try:
            puntos = int(r.get("puntuacion", 0))
        except (ValueError, TypeError):
            puntos = 0

        puntos = max(1, min(5, puntos))
        suma_puntuacion += puntos

        id_autor = r.get("id_usuario")
        es_propia = bool(id_usuario_actual is not None and id_autor == id_usuario_actual)

        item = {
            "id_resena": r.get("id_resena"),
            "id_usuario": id_autor,
            "nombre_usuario": r.get("nombre_usuario") or "Espectador",
            "puntuacion": puntos,
            "comentario": (r.get("comentario") or "").strip(),
            "fecha_legible": _formatear_fecha_resena(r.get("creada_en")),
            "es_propia": es_propia,
        }

        if es_propia and resena_propia is None:
            resena_propia = item

        resenas_formateadas.append(item)

    total = len(resenas_formateadas)
    promedio = round(suma_puntuacion / total, 1) if total > 0 else None
    estrellas_promedio = round(promedio) if promedio else 0

    return {
        "promedio": promedio,
        "estrellas_promedio": estrellas_promedio,
        "total": total,
        "resenas": resenas_formateadas,
        "resena_propia": resena_propia,
    }


def verificar_usuario_puede_resenar(
    id_pelicula: int,
    token: str | None,
    resena_propia: dict | None,
) -> tuple[bool, int | None]:
    """
    Determina si el usuario logueado posee una compra con QR validado en sala
    para la película indicada y que todavía no tenga una reseña registrada.
    Retorna (puede_resenar, id_compra_habilitada).
    """
    if not token or resena_propia is not None:
        return False, None

    from services.compras_service import obtener_compra_del_backend, obtener_mis_compras

    compras_resp, estado = obtener_mis_compras(token)
    if estado != 200 or not isinstance(compras_resp, list):
        return False, None

    for compra in compras_resp:
        if not isinstance(compra, dict):
            continue
        if compra.get("estado", "").upper() != "PAGADA":
            continue

        id_compra = compra.get("id_compra")
        if not id_compra:
            continue

        detalle, estado_det = obtener_compra_del_backend(id_compra, token)
        if estado_det != 200 or not isinstance(detalle, dict):
            continue

        id_pel_compra = detalle.get("funcion", {}).get("id_pelicula")
        if id_pel_compra == id_pelicula and detalle.get("qr_validado_en"):
            return True, id_compra

    return False, None

