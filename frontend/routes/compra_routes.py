import base64
import io
import json
import secrets
from datetime import datetime, timedelta

import qrcode

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services.funciones_service import (
    obtener_detalle_funcion_del_backend,
    obtener_funciones_del_backend,
    obtener_mapa_butacas_del_backend,
)
from services.peliculas_service import obtener_detalle_pelicula
from services.servicios_service import (
    TIPOS_SERVICIO,
    obtener_servicios_del_backend,
    formatear_monto,
    obtener_servicios_disponibles,
)
from services.compras_service import (
    cancelar_compra_al_backend,
    enviar_compra_al_backend,
    liberar_reserva_en_backend,
    obtener_compra_del_backend,
    reenviar_comprobante_al_backend,
    reservar_butacas_en_backend,
)
from utils.csrf import crear_token_csrf, validar_token_csrf
from utils.formatos import (
    formatear_duracion,
    formatear_fecha_corta,
    formatear_hora,
    formatear_precio,
    formatear_fecha_hora,
    parsear_datetime_seguro,
)
from utils.temporizador_compra import (
    DURACION_COMPRA_SEGUNDOS,
    contexto_temporizador_compra,
    iniciar_temporizador_compra,
    limpiar_compra_temporal,
    registrar_contexto_compra,
    redirigir_compra_expirada,
    temporizador_compra_iniciado,
    temporizador_compra_vencido,
)
from validators.compras_validators import (
    validar_formulario_compra,
    validar_servicios_seleccionados,
)

compra_bp = Blueprint("compra", __name__, url_prefix="/compra")
# Mantener el namespace de los endpoints existentes del comprobante.
compras_bp = Blueprint("compras", __name__)


def _armar_filas_butacas(
    butacas_lista: list[dict],
    butacas_seleccionadas_ids: set[int],
    butacas_reservadas_por_sesion: set[int],
) -> list[dict]:
    """
    Agrupa la lista plana de butacas recibida del backend por letra de fila
    y las distribuye en los tres bloques de la sala (izquierda, centro, derecha).
    """
    filas_dict = {}
    for b in butacas_lista:
        letra = b.get("fila", "A")
        if letra not in filas_dict:
            filas_dict[letra] = []

        estado_db = b.get("estado", "DISPONIBLE")
        id_butaca = b.get("id_butaca")

        if estado_db == "OCUPADA":
            estado = "ocupada"
        elif estado_db == "RESERVADA":
            estado = (
                "seleccionada"
                if id_butaca in butacas_reservadas_por_sesion
                else "ocupada"
            )
        elif id_butaca in butacas_seleccionadas_ids:
            estado = "seleccionada"
        else:
            estado = "libre"

        filas_dict[letra].append({
            "id_butaca": id_butaca,
            "num": b.get("numero", 1),
            "estado": estado,
        })

    filas_ordenadas = []
    for letra in sorted(filas_dict.keys()):
        asientos = sorted(filas_dict[letra], key=lambda x: x["num"])
        total = len(asientos)

        # Distribuir proporcionalmente en 3 bloques (izq, centro, der)
        if total <= 4:
            izq = asientos[:1]
            centro = asientos[1:3]
            der = asientos[3:]
        elif total <= 6:
            izq = asientos[:1]
            centro = asientos[1:5]
            der = asientos[5:]
        elif total <= 10:
            izq = asientos[:2]
            centro = asientos[2:8]
            der = asientos[8:]
        else:
            c1 = 3
            c2 = total - 3
            izq = asientos[:c1]
            centro = asientos[c1:c2]
            der = asientos[c2:]

        filas_ordenadas.append({
            "letra": letra,
            "es_vip": letra in ("E", "F", "G"),
            "asientos_izq": izq,
            "asientos_centro": centro,
            "asientos_der": der,
        })

    return filas_ordenadas


@compra_bp.route("/expirada", methods=["GET"])
def compra_expirada():
    if not temporizador_compra_vencido():
        compra = session.get("compra") or {}
        if compra.get("butacas"):
            return redirect(url_for("compra.seleccion_checkout"))
        return redirect(url_for("compra.seleccion_butacas", id_funcion=compra.get("id_funcion")))
    token_reserva = session.get("token_reserva_butacas")
    access_token = session.get("access_token")
    if token_reserva and access_token:
        liberar_reserva_en_backend(token_reserva, access_token)
    return redirigir_compra_expirada()


@compra_bp.route("/butacas", methods=["GET", "POST"])
def seleccion_butacas():
    """
    Controlador SSR para el mapa de butacas en vivo.
    GET: Carga la función y el estado real de cada butaca desde el backend.
    POST: Recibe la selección del usuario, valida disponibilidad y persiste en session.
    """
    if request.method == "POST":
        if temporizador_compra_iniciado() and temporizador_compra_vencido():
            return redirigir_compra_expirada()
        id_funcion = request.form.get("id_funcion", type=int)
        raw_butacas = request.form.get("butacas_seleccionadas", "")

        ids_butacas = []
        if raw_butacas:
            try:
                ids_butacas = json.loads(raw_butacas)
            except (ValueError, TypeError):
                ids_butacas = [int(x) for x in raw_butacas.split(",") if x.strip().isdigit()]

        if not id_funcion:
            flash("No se especificó la función de cine seleccionada.", "error")
            return redirect(url_for("home.index"))

        if not ids_butacas:
            flash("Por favor seleccioná al menos una butaca libre para continuar.", "error")
            return redirect(url_for("compra.seleccion_butacas", id_funcion=id_funcion))

        # Los IDs enviados deben existir y estar disponibles en la función elegida.
        mapa_resp, status_mapa = obtener_mapa_butacas_del_backend(id_funcion)
        if status_mapa != 200 or not isinstance(mapa_resp, dict):
            flash("No se pudo verificar la disponibilidad de las butacas.", "error")
            return redirect(url_for("compra.seleccion_butacas", id_funcion=id_funcion))

        todas_butacas = mapa_resp.get("butacas") or []
        mapa_dict = {b["id_butaca"]: b for b in todas_butacas}
        compra_previa = session.get("compra") or {}
        token_previo = session.get("token_reserva_butacas")
        ids_reservadas_por_sesion = {
            butaca["id_butaca"]
            for butaca in compra_previa.get("butacas", [])
            if token_previo
            and compra_previa.get("id_funcion") == id_funcion
            and "id_butaca" in butaca
        }
        butacas_elegidas = []
        for id_b in ids_butacas:
            b = mapa_dict.get(id_b)
            if b is None:
                flash(f"La butaca seleccionada (ID {id_b}) no existe en esta función.", "error")
                return redirect(url_for("compra.seleccion_butacas", id_funcion=id_funcion))
            if b.get("estado") == "OCUPADA" or (
                b.get("estado") == "RESERVADA"
                and id_b not in ids_reservadas_por_sesion
            ):
                flash("Una de las butacas seleccionadas ya no está disponible.", "error")
                return redirect(url_for("compra.seleccion_butacas", id_funcion=id_funcion))
            butacas_elegidas.append(b)

        token_acceso = session.get("access_token")
        if token_acceso:
            token_reserva = token_previo or secrets.token_hex(32)
            duracion_segundos = (
                contexto_temporizador_compra()["duracion_restante_segundos"]
                if temporizador_compra_iniciado()
                else DURACION_COMPRA_SEGUNDOS
            )
            respuesta_reserva, estado_reserva = reservar_butacas_en_backend(
                {
                    "id_funcion": id_funcion,
                    "butacas_ids": ids_butacas,
                    "token_reserva": token_reserva,
                    "duracion_segundos": duracion_segundos,
                },
                token_acceso,
            )
            if estado_reserva != 201:
                errores = (
                    respuesta_reserva.get("errors", [])
                    if isinstance(respuesta_reserva, dict)
                    else []
                )
                mensaje = errores[0].get("description") if errores else None
                flash(mensaje or "No se pudieron apartar las butacas elegidas.", "error")
                return redirect(
                    url_for("compra.seleccion_butacas", id_funcion=id_funcion)
                )
            session["token_reserva_butacas"] = token_reserva

        iniciar_temporizador_compra(
            id_funcion=id_funcion,
            id_pelicula=session.get("compra_id_pelicula"),
        )

        # Obtener detalle de función para precio y datos de la orden
        func_detalle, _ = obtener_detalle_funcion_del_backend(id_funcion)
        precio_unitario = (
            float(func_detalle.get("precio_entrada", 8500))
            if isinstance(func_detalle, dict)
            else 8500.0
        )
        precio_vip = round(precio_unitario * 1.25, 2)
        butacas_guardadas = []
        for b in butacas_elegidas:
            es_vip = b.get("fila") in ("E", "F", "G")
            pr = precio_vip if es_vip else precio_unitario
            butacas_guardadas.append({
                "id_butaca": b["id_butaca"],
                "fila": b["fila"],
                "numero": b["numero"],
                "es_vip": es_vip,
                "precio": pr,
            })
        subtotal = sum(b["precio"] for b in butacas_guardadas)

        # Guardar la selección en la sesión de Flask
        session["compra"] = {
            "id_funcion": id_funcion,
            "id_pelicula": func_detalle.get("id_pelicula") if isinstance(func_detalle, dict) else session.get("compra_id_pelicula"),
            "pelicula_titulo": func_detalle.get("titulo_pelicula", "Película") if isinstance(func_detalle, dict) else "Película",
            "complejo": func_detalle.get("nombre_local", "Cine Paradiso") if isinstance(func_detalle, dict) else "Cine Paradiso",
            "sala_numero": func_detalle.get("numero_sala", 1) if isinstance(func_detalle, dict) else 1,
            "sala_completa": f"Sala {func_detalle.get('numero_sala', 1)} ({func_detalle.get('formato', '2D')})" if isinstance(func_detalle, dict) else "Sala 1",
            "horario": func_detalle.get("inicio", "") if isinstance(func_detalle, dict) else "",
            "precio_unitario": precio_unitario,
            "butacas": butacas_guardadas,
            "total_butacas": len(butacas_guardadas),
            "subtotal_entradas": subtotal,
        }

        return redirect(url_for("compra.seleccion_servicios"))

    # Petición GET: Cargar mapa y datos
    id_funcion = request.args.get("id_funcion", type=int)
    if not id_funcion:
        id_funcion = (session.get("compra") or {}).get("id_funcion") or session.get("compra_id_funcion")

    # Si no vino id_funcion, buscar la primera función programada activa
    if not id_funcion:
        funciones_disponibles, status_f = obtener_funciones_del_backend()
        if status_f == 200 and isinstance(funciones_disponibles, list) and funciones_disponibles:
            id_funcion = funciones_disponibles[0].get("id_funcion")
        else:
            flash("No hay funciones disponibles para seleccionar butacas.", "error")
            return redirect(url_for("home.index"))

    # 1. Consultar mapa de butacas al backend
    mapa_resp, status_mapa = obtener_mapa_butacas_del_backend(id_funcion)
    # 2. Consultar detalles de la función
    func_resp, status_func = obtener_detalle_funcion_del_backend(id_funcion)
    if status_func != 200 or not isinstance(func_resp, dict):
        flash("La función seleccionada no está disponible.", "error")
        return redirect(url_for("home.index"))
    if status_mapa != 200 or not isinstance(mapa_resp, dict) or not mapa_resp.get("butacas"):
        flash("No se pudo cargar el mapa real de butacas de esta función.", "error")
        return redirect(url_for("peliculas.detalle_pelicula", id_pelicula=func_resp["id_pelicula"]))

    id_pelicula = func_resp.get("id_pelicula")
    registrar_contexto_compra(id_funcion=id_funcion, id_pelicula=id_pelicula)
    if temporizador_compra_iniciado() and temporizador_compra_vencido():
        return redirigir_compra_expirada()
    temporizador = (
        contexto_temporizador_compra()
        if temporizador_compra_iniciado()
        else None
    )

    # Obtener butacas de la sesión previa si corresponden a esta función
    compra_sesion = session.get("compra", {})
    butacas_previas = (
        compra_sesion.get("butacas", [])
        if compra_sesion.get("id_funcion") == id_funcion
        else []
    )
    ids_seleccionadas = {b["id_butaca"] for b in butacas_previas if "id_butaca" in b}
    ids_reservadas_por_sesion = (
        ids_seleccionadas if session.get("token_reserva_butacas") else set()
    )

    # Armar filas dinámicas si el backend respondió
    butacas_db = mapa_resp.get("butacas", []) if isinstance(mapa_resp, dict) else []
    filas_construidas = _armar_filas_butacas(
        butacas_db, ids_seleccionadas, ids_reservadas_por_sesion
    )

    # Buscar detalles de la película
    peli_resp, estado_pelicula = (
        obtener_detalle_pelicula(id_pelicula)
        if id_pelicula
        else (None, 404)
    )

    if estado_pelicula != 200 or not isinstance(peli_resp, dict):
        peli_resp = {}

    titulo_pelicula = (
        func_resp.get("titulo_pelicula")
        or peli_resp.get("titulo")
        or "Película en Cartelera"
    )
    poster_url = (
        peli_resp.get("poster_url")
        or "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg"
    )
    duracion = formatear_duracion(peli_resp.get("duracion_min")) or "120 min"
    formato = func_resp.get("formato", "2D") if isinstance(func_resp, dict) else "2D"
    idioma = func_resp.get("idioma", "Original") if isinstance(func_resp, dict) else "Original"
    subtitulada = (
        "Subtitulada"
        if (func_resp.get("subtitulada") if isinstance(func_resp, dict) else True)
        else "Doblada"
    )
    complejo = (
        func_resp.get("nombre_local", "Cine Paradiso")
        if isinstance(func_resp, dict)
        else "Cine Paradiso"
    )
    num_sala = func_resp.get("numero_sala", 1) if isinstance(func_resp, dict) else 1
    precio_base = (
        float(func_resp.get("precio_entrada", 8500))
        if isinstance(func_resp, dict)
        else 8500.0
    )
    precio_vip = precio_base * 1.25

    # Formato de horario
    inicio_raw = func_resp.get("inicio", "") if isinstance(func_resp, dict) else ""
    horario_etiqueta = formatear_fecha_hora(inicio_raw) or "Horario a confirmar"

    # Resumen lateral
    ubicaciones_resumen = []
    subtotal = 0.0
    for b in butacas_previas:
        pr = b.get("precio", precio_base)
        subtotal += pr
        ubicaciones_resumen.append({
            "id": f"{b.get('fila')}-{b.get('numero')}",
            "id_butaca": b.get("id_butaca"),
            "fila": b.get("fila"),
            "butaca": b.get("numero"),
            "categoria": f"General {formato}",
            "precio": int(pr),
            "precio_formato": f"${int(pr):,.0f}".replace(",", "."),
        })

    datos_compra = {
        "pelicula": {
            "id_pelicula": id_pelicula,
            "titulo": titulo_pelicula,
            "titulo_upper": titulo_pelicula.upper(),
            "poster_url": poster_url,
            "formato": f"SALA {formato}",
            "idioma": f"{idioma} ({subtitulada})",
            "duracion": duracion,
        },
        "funcion": {
            "id_funcion": id_funcion,
            "complejo": complejo,
            "sala_nombre": f"Sala {num_sala}",
            "sala_completa": f"Sala {num_sala} ({formato})",
            "horario_etiqueta": horario_etiqueta,
            "pantalla_tipo": f"PANTALLA {formato}",
            "tiempo_restante": (
                f"{temporizador['tiempo_restante']} min"
                if temporizador
                else "10:00 min"
            ),
            "precio_general": int(precio_base),
            "precio_vip": int(precio_vip),
            "precio_general_formato": formatear_precio(precio_base),
            "precio_vip_formato": formatear_precio(precio_vip),
        },
        "sala": {
            "filas": filas_construidas,
        },
        "resumen": {
            "total_butacas": len(ubicaciones_resumen),
            "ubicaciones": ubicaciones_resumen,
            "subtotal": int(subtotal),
            "subtotal_formato": f"${int(subtotal):,.0f}".replace(",", "."),
            "cargo_servicio": 0,
            "cargo_servicio_texto": "Bonificado $0",
            "total": int(subtotal),
            "total_formato": f"${int(subtotal):,.0f}".replace(",", "."),
        },
    }

    return render_template("seleccion_butacas.html", c=datos_compra, temporizador=temporizador)


@compra_bp.route("/servicios", methods=["GET", "POST"])
def seleccion_servicios():
    """Renderiza Candy Bar con la compra real y conserva los servicios elegidos."""
    if temporizador_compra_vencido():
        return redirigir_compra_expirada()

    compra = session.get("compra") or {}
    if not compra.get("butacas") or not compra.get("id_funcion"):
        return redirect(url_for("compra.seleccion_butacas"))

    def _parsear_inicio(valor: str):
        if not valor:
            return None
        try:
            return datetime.fromisoformat(str(valor))
        except (ValueError, TypeError):
            return None

    def _construir_contexto(compra_actual: dict, servicios_api: list[dict], cantidades: dict):
        id_funcion = compra_actual.get("id_funcion")
        funcion, _ = obtener_detalle_funcion_del_backend(id_funcion) if id_funcion else (None, 404)
        if not isinstance(funcion, dict):
            funcion = {}

        id_pelicula = compra_actual.get("id_pelicula") or funcion.get("id_pelicula")
        pelicula, estado_pelicula = (
            obtener_detalle_pelicula(id_pelicula)
            if id_pelicula
            else (None, 404)
        )
        if estado_pelicula != 200 or not isinstance(pelicula, dict):
            pelicula = {}

        titulo = (
            compra_actual.get("pelicula_titulo")
            or funcion.get("titulo_pelicula")
            or pelicula.get("titulo")
            or "Película en cartelera"
        )
        formato = funcion.get("formato") or (compra_actual.get("sala_completa") or "").split("(")[-1].replace(")", "").strip() or "2D"
        idioma_base = funcion.get("idioma") or "Original"
        subtitulada = funcion.get("subtitulada")
        if subtitulada is None:
            subtitulada = True
        idioma = f"{idioma_base} ({'Subtitulada' if subtitulada else 'Doblada'})"
        complejo = compra_actual.get("complejo") or funcion.get("nombre_local") or "Cine Paradiso"
        sala_numero = compra_actual.get("sala_numero") or funcion.get("numero_sala") or 1
        sala_completa = compra_actual.get("sala_completa") or f"Sala {sala_numero} ({formato})"
        sala_badge = f"SALA {sala_numero} • {formato}".upper()

        inicio_dt = parsear_datetime_seguro(
            funcion.get("inicio") or compra_actual.get("horario", "")
        )
        if inicio_dt:
            horario_etiqueta = (
                f"{formatear_fecha_hora(inicio_dt)} • "
                f"{'Subtitulada' if subtitulada else 'Doblada'}"
            )
        else:
            horario_etiqueta = compra_actual.get("horario") or "Horario a confirmar"

        poster_url = (
            pelicula.get("poster_url")
            or "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg"
        )

        butacas = compra_actual.get("butacas") or []
        butacas_texto = ", ".join(
            f"{b.get('fila')}-{b.get('numero')}" for b in butacas
        ) or "Sin butacas"
        precio_unitario = float(compra_actual.get("precio_unitario") or funcion.get("precio_entrada") or 0)
        subtotal_entradas = float(compra_actual.get("subtotal_entradas") or (precio_unitario * len(butacas)))

        servicios = [
            {**servicio, "cantidad": cantidades.get(servicio["id_servicio"], 0)}
            for servicio in servicios_api
        ]
        items_seleccionados = [
            {
                "id_servicio": servicio["id_servicio"],
                "nombre": servicio["nombre"],
                "descripcion": servicio.get("descripcion") or servicio.get("tipo") or "",
                "cantidad": servicio["cantidad"],
                "subtotal_formato": formatear_monto(
                    float(servicio["precio"]) * servicio["cantidad"]
                ),
            }
            for servicio in servicios
            if servicio["cantidad"] > 0
        ]
        subtotal_candy = sum(
            float(servicio["precio"]) * servicio["cantidad"] for servicio in servicios
        )
        total = subtotal_entradas + subtotal_candy

        entradas_items = []
        vip_butacas = [b for b in butacas if b.get("es_vip") or b.get("fila") in ("E", "F", "G")]
        gen_butacas = [b for b in butacas if not (b.get("es_vip") or b.get("fila") in ("E", "F", "G"))]
        if gen_butacas:
            sub_gen = sum(float(b.get("precio", precio_unitario)) for b in gen_butacas)
            txt_gen = ", ".join(f"{b.get('fila')}-{b.get('numero')}" for b in gen_butacas)
            entradas_items.append({
                "descripcion": f"{len(gen_butacas)}x Entrada {formato}",
                "detalle": f"Butacas {txt_gen}",
                "subtotal": sub_gen,
                "subtotal_formato": formatear_monto(sub_gen),
            })
        if vip_butacas:
            precio_vip = round(precio_unitario * 1.25, 2)
            sub_vip = sum(float(b.get("precio", precio_vip)) for b in vip_butacas)
            txt_vip = ", ".join(f"{b.get('fila')}-{b.get('numero')}" for b in vip_butacas)
            entradas_items.append({
                "descripcion": f"{len(vip_butacas)}x Entrada VIP ({formato})",
                "detalle": f"Butacas {txt_vip}",
                "subtotal": sub_vip,
                "subtotal_formato": formatear_monto(sub_vip),
            })
        if not entradas_items:
            entradas_items.append({
                "descripcion": f"{len(butacas)}x Entrada {formato}",
                "detalle": f"Butacas {butacas_texto}",
                "subtotal": subtotal_entradas,
                "subtotal_formato": formatear_monto(subtotal_entradas),
            })

        return {
            "pelicula": {
                "id_pelicula": id_pelicula,
                "titulo": titulo,
                "titulo_upper": str(titulo).upper(),
                "poster_url": poster_url,
                "formato": sala_completa,
                "sala_badge": sala_badge,
                "idioma": idioma,
                "horario_etiqueta": horario_etiqueta,
                "complejo": complejo,
            },
            "entradas": {
                "items": entradas_items,
                "subtotal": subtotal_entradas,
                "subtotal_formato": formatear_monto(subtotal_entradas),
            },
            "categorias_filtro": [
                {"id": "todos", "nombre": "Todos los Servicios"},
                *({"id": tipo.lower(), "nombre": tipo} for tipo in TIPOS_SERVICIO),
            ],
            "servicios": servicios,
            "servicios_seleccionados": [
                {"id_servicio": sid, "cantidad": cant}
                for sid, cant in cantidades.items()
                if cant > 0
            ],
            "candy_seleccionado": {
                "items": items_seleccionados,
                "total_items": sum(item["cantidad"] for item in items_seleccionados),
                "subtotal": subtotal_candy,
                "subtotal_formato": formatear_monto(subtotal_candy),
            },
            "resumen": {
                "subtotal_entradas": subtotal_entradas,
                "subtotal_entradas_formato": formatear_monto(subtotal_entradas),
                "subtotal_candy": subtotal_candy,
                "subtotal_candy_formato": formatear_monto(subtotal_candy),
                "cargos_servicio_texto": "100% Bonificado",
                "total": total,
                "total_formato": formatear_monto(total),
            },
        }

    if request.method == "POST":
        if not validar_token_csrf(request.form.get("csrf_token", "")):
            flash("Formulario inválido.", "error")
            return redirect(url_for("compra.seleccion_servicios"))

        try:
            servicios = validar_servicios_seleccionados(
                request.form.get("servicios_json", "[]")
            )
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("compra.seleccion_servicios"))

        if servicios:
            catalogo = obtener_servicios_disponibles()
            if catalogo is None:
                flash("No se pudo validar el catálogo de servicios.", "error")
                return redirect(url_for("compra.seleccion_servicios"))
            ids_disponibles = {servicio["id_servicio"] for servicio in catalogo}
            if any(item["id_servicio"] not in ids_disponibles for item in servicios):
                flash(
                    "La selección contiene un servicio que ya no está disponible.",
                    "error",
                )
                return redirect(url_for("compra.seleccion_servicios"))

        session["servicios_seleccionados"] = servicios
        return redirect(url_for("compra.seleccion_checkout"))

    servicios_api = obtener_servicios_disponibles()
    if servicios_api is None:
        flash("No se pudo cargar el catálogo de servicios.", "error")
        servicios_api = []

    cantidades = {
        item["id_servicio"]: item["cantidad"]
        for item in session.get("servicios_seleccionados", [])
    }
    datos_compra = _construir_contexto(compra, servicios_api, cantidades)
    temporizador = contexto_temporizador_compra()

    return render_template(
        "seleccion_servicios.html",
        c=datos_compra,
        csrf_token=crear_token_csrf(),
        temporizador=temporizador,
    )


@compra_bp.route("/checkout")
def seleccion_checkout():
    """
    Muestra el checkout con los datos de la compra actual.
    Recupera las butacas y los servicios desde la sesión.
    Consulta los precios vigentes al backend.
    """

    # 1. Verificar que el usuario haya iniciado sesión
    usuario = session.get("usuario")

    if not usuario or not session.get("access_token"):
        flash("Debés iniciar sesión para comprar.", "error")
        return redirect(url_for("auth.login"))

    # 2. Recuperar la compra de la sesión
    compra = session.get("compra")

    if not compra or not compra.get("id_funcion") or not compra.get("butacas"):
        flash("Primero debés seleccionar tus butacas.", "error")
        return redirect(url_for("compra.seleccion_butacas"))

    if temporizador_compra_vencido():
        return redirigir_compra_expirada()
    temporizador = contexto_temporizador_compra()

    token_reserva = session.get("token_reserva_butacas") or secrets.token_hex(32)
    datos_reserva = {
        "id_funcion": compra["id_funcion"],
        "butacas_ids": [butaca["id_butaca"] for butaca in compra["butacas"]],
        "token_reserva": token_reserva,
        "duracion_segundos": temporizador["duracion_restante_segundos"],
    }
    reserva, estado_reserva = reservar_butacas_en_backend(
        datos_reserva, session["access_token"]
    )
    if estado_reserva != 201:
        session.pop("token_reserva_butacas", None)
        errores = reserva.get("errors", []) if isinstance(reserva, dict) else []
        mensaje = errores[0].get("description") if errores else None
        flash(mensaje or "No se pudieron apartar las butacas. Volvé a seleccionarlas.", "error")
        return redirect(url_for("compra.seleccion_butacas", id_funcion=compra["id_funcion"]))
    session["token_reserva_butacas"] = token_reserva

    # 3. Consultar los datos actuales de la función
    funcion, estado = obtener_detalle_funcion_del_backend(
        compra["id_funcion"]
    )

    if estado != 200 or not isinstance(funcion, dict):
        flash("La función seleccionada ya no está disponible.", "error")
        return redirect(url_for("compra.seleccion_butacas"))

    # 4. Obtener los datos de la película
    id_pelicula = funcion.get("id_pelicula")

    pelicula, estado_pelicula = (
        obtener_detalle_pelicula(id_pelicula)
        if id_pelicula
        else (None, 404)
    )

    if estado_pelicula != 200 or not isinstance(pelicula, dict):
        pelicula = {}

    # 5. Calcular el subtotal de las entradas
    cantidad_entradas = len(compra["butacas"])

    precio_unitario = float(funcion["precio_entrada"])
    precio_vip = round(precio_unitario * 1.25, 2)

    # 6. Construir el desglose de las entradas considerando butacas VIP
    desglose = []
    vip_butacas = [b for b in compra["butacas"] if b.get("es_vip") or b.get("fila") in ("E", "F", "G")]
    gen_butacas = [b for b in compra["butacas"] if not (b.get("es_vip") or b.get("fila") in ("E", "F", "G"))]

    subtotal_entradas = 0.0
    if gen_butacas:
        sub_gen = sum(float(b.get("precio", precio_unitario)) for b in gen_butacas)
        subtotal_entradas += sub_gen
        desglose.append({
            "titulo": f"{len(gen_butacas)}x Entrada {funcion.get('formato', '2D')}",
            "subtexto": compra["pelicula_titulo"],
            "precio": f"${sub_gen:,.0f}".replace(",", "."),
        })
    if vip_butacas:
        sub_vip = sum(float(b.get("precio", precio_vip)) for b in vip_butacas)
        subtotal_entradas += sub_vip
        desglose.append({
            "titulo": f"{len(vip_butacas)}x Entrada VIP ({funcion.get('formato', '2D')})",
            "subtexto": compra["pelicula_titulo"],
            "precio": f"${sub_vip:,.0f}".replace(",", "."),
        })
    if not desglose:
        subtotal_entradas = float(compra.get("subtotal_entradas") or (precio_unitario * cantidad_entradas))
        desglose.append({
            "titulo": f"{cantidad_entradas}x Entrada",
            "subtexto": compra["pelicula_titulo"],
            "precio": f"${subtotal_entradas:,.0f}".replace(",", "."),
        })

    # 7. Recuperar los servicios seleccionados (si existen)
    servicios_seleccionados = session.get("servicios_seleccionados", [])

    subtotal_servicios = 0

    if servicios_seleccionados:

        catalogo, estado = obtener_servicios_del_backend()

        if estado != 200 or not isinstance(catalogo, list):
            flash("No se pudieron consultar los servicios.", "error")
            return redirect(url_for("compra.seleccion_servicios"))

        servicios_por_id = {
            servicio["id_servicio"]: servicio
            for servicio in catalogo
        }

        ids_procesados = set()

        for item in servicios_seleccionados:

            try:
                id_servicio = int(item["id_servicio"])
                cantidad = int(item["cantidad"])
            except (KeyError, TypeError, ValueError):
                flash("Hay un servicio inválido en la compra.", "error")
                return redirect(url_for("compra.seleccion_servicios"))

            servicio = servicios_por_id.get(id_servicio)

            if (
                servicio is None
                or cantidad <= 0
                or cantidad > 99
                or id_servicio in ids_procesados
            ):
                flash("Hay un servicio inválido en la compra.", "error")
                return redirect(url_for("compra.seleccion_servicios"))

            ids_procesados.add(id_servicio)

            precio = float(servicio["precio"])
            subtotal = precio * cantidad

            subtotal_servicios += subtotal

            desglose.append({
                "titulo": f"{cantidad}x {servicio['nombre']}",
                "subtexto": None,
                "precio": f"${subtotal:,.0f}".replace(",", "."),
            })

    # 8. Calcular el total de la compra
    total = subtotal_entradas + subtotal_servicios

    total_formateado = f"${total:,.0f}".replace(",", ".")

    # 9. Preparar los datos visuales de la película
    formato = funcion.get("formato", "")
    idioma = funcion.get("idioma", "")

    subtitulos = (
        "Subtitulada"
        if funcion.get("subtitulada")
        else "Doblada"
    )

    duracion = formatear_duracion(pelicula.get("duracion_min"))

    especificaciones = " • ".join(
        dato for dato in [idioma, subtitulos, duracion] if dato
    )

    horario_raw = funcion.get("inicio", compra.get("horario", ""))
    horario = formatear_fecha_hora(horario_raw) or horario_raw

    # 10. Preparar el diccionario que utiliza checkout.html
    datos_compra = {

        "tiempo_restante": temporizador["tiempo_restante"],

        "pelicula": {
            "id_pelicula": id_pelicula,
            "titulo": pelicula.get(
                "titulo",
                compra["pelicula_titulo"]
            ),
            "poster_url": pelicula.get("poster_url") or "",
            "badge_formato": formato,
            "badge_edad": pelicula.get("clasificacion") or "",
            "especificaciones": especificaciones,
            "sala_completa": compra["sala_completa"],
            "dia_horario": horario,
            "complejo": compra["complejo"],
            "butacas_asignadas": ", ".join(
                f"{butaca['fila']}-{butaca['numero']}"
                for butaca in compra["butacas"]
            ),
        },

        "desglose": desglose,

        "subtotal_parcial": total_formateado,

        "cargo_servicio": "BONIFICADO ($0)",

        "total": total_formateado,

        "total_monto": total,

        # Opciones visuales de cuotas calculadas sobre el total real.
        # El procesamiento del pago continúa siendo simulado.
        "cuotas": [
            f"1 pago de {total_formateado} (Sin interés)",
            f"3 cuotas de {formatear_monto(total / 3)} (Sin interés)",
            f"6 cuotas fijas de {formatear_monto(total / 6)} (Sin interés)",
        ],

        "comprador_default": {
            "nombre": usuario.get("nombre", ""),
            "email": usuario.get("email", ""),
            "dni": "",
            "telefono": "",
            "tarjeta_numero": "",
            "tarjeta_titular": "",
            "tarjeta_vencimiento": "",
        },
    }

    # 11. Renderizar el checkout
    return render_template(
        "checkout.html",
        c=datos_compra,
        csrf_token=crear_token_csrf(),
        temporizador=temporizador,
    )


def _extraer_mensaje_error_backend(respuesta, fallback: str) -> str:
    if isinstance(respuesta, dict):
        errores = respuesta.get("errors")
        if isinstance(errores, list) and errores:
            primero = errores[0] if isinstance(errores[0], dict) else {}
            mensaje = primero.get("description") or primero.get("message")
            if mensaje:
                return str(mensaje)
        mensaje = respuesta.get("error") or respuesta.get("mensaje")
        if mensaje:
            return str(mensaje)
    return fallback


@compras_bp.route("/compra/confirmar", methods=["POST"])
def confirmar_compra():
    if temporizador_compra_vencido():
        return redirigir_compra_expirada()
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        return "La sesión del formulario venció. Volvé a intentarlo.", 400
    token = session.get("access_token")
    if not token:
        flash("Necesitás iniciar sesión para realizar la compra.", "error")
        return redirect(url_for("home.index"))
    try:
        datos = validar_formulario_compra(
            request.form,
            session.get("servicios_seleccionados", []),
        )
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("compra.seleccion_checkout"))
    compra, estado = enviar_compra_al_backend(datos, token)
    if estado == 201 and isinstance(compra, dict) and type(compra.get("id_compra")) is int:
        limpiar_compra_temporal()
        return redirect(url_for("compras.compra_exitosa", id_compra=compra["id_compra"]))
    flash(
        _extraer_mensaje_error_backend(
            compra,
            "No se pudo confirmar la compra. Revisá la función, las butacas y la sesión.",
        ),
        "error",
    )
    return redirect(url_for("compra.seleccion_checkout"))


@compras_bp.route("/compras/<int:id_compra>/confirmacion", methods=["GET"])
def compra_exitosa(id_compra: int):

    token = session.get("access_token")

    if not token:
        flash("Debés iniciar sesión.", "error")
        return redirect(url_for("auth.login"))

    # Obtener la compra real desde MySQL
    compra, estado = obtener_compra_del_backend(id_compra, token)

    if estado != 200 or not isinstance(compra, dict):
        flash("No se pudo obtener el comprobante.", "error")
        return redirect(url_for("home.index"))

    funcion = compra["funcion"]
    entradas = compra.get("entradas", [])
    servicios = compra.get("servicios", [])

    # Obtener información adicional de la película
    pelicula, estado_pelicula = obtener_detalle_pelicula(funcion["id_pelicula"])
    if estado_pelicula != 200 or not isinstance(pelicula, dict):
        pelicula = {}

    # Interpretar fecha y horario de la función
    inicio_texto = str(funcion.get("inicio") or "")
    fecha_funcion = parsear_datetime_seguro(inicio_texto)

    fecha = formatear_fecha_corta(fecha_funcion) if fecha_funcion else inicio_texto
    horario = formatear_hora(fecha_funcion) if fecha_funcion else ""
    limite_dt = (fecha_funcion - timedelta(hours=24)) if fecha_funcion else None
    limite_cancelacion = (
        formatear_fecha_hora(limite_dt)
        if limite_dt
        else "24 horas antes de la función"
    )

    puede_cancelar = (
    compra.get("estado") == "PAGADA"
    and not compra.get("qr_validado_en")
    and fecha_funcion is not None
    and fecha_funcion > (
        datetime.now(fecha_funcion.tzinfo)
        + timedelta(hours=24)
    )
    )

    # Construir descripción de las butacas
    butacas = ", ".join(
        f"{entrada['fila']}-{entrada['numero']}"
        for entrada in entradas
    )

    # Construir el detalle de la compra
    items = [
        {
            "descripcion": f"{len(entradas)}x Entrada ({butacas})",
            "monto": formatear_precio(compra["subtotal_entradas"]),
        }
    ]

    for servicio in servicios:
        items.append({
            "descripcion": (
                f"{servicio['cantidad']}x "
                f"{servicio['nombre_servicio']}"
            ),
            "monto": formatear_precio(servicio["subtotal"]),
        })

    # Servicios adicionales para las tarjetas del voucher
    adicionales = [
        {
            "tipo": "combo",
            "nombre": (
                f"{servicio['cantidad']}x "
                f"{servicio['nombre_servicio']}"
            ),
            "detalle": (
                "Precio unitario: "
                + formatear_precio(servicio["precio_unitario"])
            ),
            "subdetalle": None,
            "estado": "Incluido",
            "icono": "combo",
        }
        for servicio in servicios
    ]

    # Crear imagen del QR usando el token real
    qr_base64 = None

    if (
        compra.get("estado") == "PAGADA"
        and compra.get("qr_token")
        and not compra.get("qr_validado_en")
    ):
        imagen = qrcode.make(compra["qr_token"])
        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")

        qr_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

    duracion = pelicula.get("duracion_min")

    datos_confirmacion = {

        "id_compra": id_compra,
        "id_transaccion": compra["codigo_reserva"],
        "estado": compra["estado"],
        "email_comprador": compra["email_comprobante"],
        "codigo_reserva": compra["codigo_reserva"],
        "qr_base64": qr_base64,

        "pelicula": {
            "id_pelicula": funcion["id_pelicula"],
            "titulo": funcion["titulo_pelicula"],
            "poster_url": pelicula.get("poster_url") or "",
            "badge_poster": funcion.get("formato") or "",
            "clasificacion": pelicula.get("clasificacion") or "",
            "duracion": f"{duracion} MIN" if duracion else "",
            "formato_sala": funcion.get("formato") or "",
            "idioma": funcion.get("idioma") or "",
            "direccion_sonido": "",
            "fecha": fecha,
            "horario": horario,
            "complejo": funcion["nombre_local"],
            "sala_nombre": f"Sala {funcion['numero_sala']}",
            "butacas": butacas,
            "badge_butacas": funcion.get("formato") or "",
        },

        "facturacion": {
            "tipo": "COMPRA SIMULADA",
            "items": items,
            "cargo_servicio": "100% BONIFICADO",
            "cargo_servicio_monto": formatear_precio(
                compra.get("cargo_servicio", 0)
            ),
            "total": formatear_precio(compra["total"]),
            "iva_discriminado": None,
            "tarjeta_info": "Pago simulado",
            "cuotas_info": "Sin transacción bancaria",
            "cae": None,
            "vto_cae": None,
        },

        "adicionales": adicionales,

        "cancelacion": {
            "limite_texto": limite_cancelacion,
            "habilitada": puede_cancelar,
        },
    }

    return render_template(
        "confirmacion_compra.html",
        c=datos_confirmacion,
        csrf_token=crear_token_csrf()
    )


@compras_bp.route("/compras/<int:id_compra>/reenviar-email", methods=["POST"])
def reenviar_email(id_compra: int):
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida.", 400
    token = session.get("access_token")
    if not token:
        flash("Necesitás iniciar sesión antes de comprar.", "error")
        return redirect(url_for("home.index"))
    respuesta, estado = reenviar_comprobante_al_backend(id_compra, token)
    if estado == 200:
        flash("Solicitud de reenvío procesada.", "success")
    else:
        flash("No se pudo enviar el comprobante.", "error")
    return redirect(url_for("compras.compra_exitosa", id_compra=id_compra))


@compras_bp.route("/compras/<int:id_compra>/cancelar", methods=["POST"])
def cancelar_compra_web(id_compra: int):
    """
    Recibe la solicitud de cancelación del usuario
    y la envía al backend mediante PUT.
    """

    # 1. Validar el token CSRF
    if not validar_token_csrf(request.form.get("csrf_token", "")):
        flash("La sesión del formulario venció. Volvé a intentarlo.", "error")
        return redirect(
            url_for("compras.compra_exitosa", id_compra=id_compra)
        )

    # 2. Verificar autenticación
    token = session.get("access_token")

    if not token:
        flash("Debés iniciar sesión para cancelar la compra.", "error")
        return redirect(url_for("auth.login"))

    # 3. Solicitar la cancelación al backend
    respuesta, estado = cancelar_compra_al_backend(id_compra, token)

    # 4. Procesar el resultado
    if (
        estado == 200
        and isinstance(respuesta, dict)
        and respuesta.get("estado") == "CANCELADA"
    ):
        flash("La compra fue cancelada correctamente.", "success")

    else:
        mensaje = "No se pudo cancelar la compra."

        if isinstance(respuesta, dict):
            errores = respuesta.get("errors", [])

            if errores:
                mensaje = (
                    errores[0].get("description")
                    or errores[0].get("message")
                    or mensaje
                )

        flash(mensaje, "error")

    # 5. Volver al comprobante actualizado
    return redirect(
        url_for("compras.compra_exitosa", id_compra=id_compra)
    )
