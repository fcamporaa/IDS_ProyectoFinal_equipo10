import json
from datetime import datetime

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
    obtener_servicios_del_backend,
    formatear_monto,
    obtener_servicios_disponibles,
)
from utils.csrf import crear_token_csrf, validar_token_csrf
from utils.formatos import formatear_duracion, formatear_fecha_corta, formatear_hora
from utils.temporizador_compra import (
    contexto_temporizador_compra,
    iniciar_temporizador_compra,
    redirigir_compra_expirada,
    temporizador_compra_vencido,
)
from validators.compras_validators import validar_servicios_seleccionados

compra_bp = Blueprint("compra", __name__, url_prefix="/compra")


def _armar_filas_butacas(butacas_lista: list[dict], butacas_seleccionadas_ids: set[int]) -> list[dict]:
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

        if estado_db in ("OCUPADA", "RESERVADA"):
            estado = "ocupada"
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
    return redirigir_compra_expirada()


@compra_bp.route("/butacas", methods=["GET", "POST"])
def seleccion_butacas():
    """
    Controlador SSR para el mapa de butacas en vivo.
    GET: Carga la función y el estado real de cada butaca desde el backend.
    POST: Recibe la selección del usuario, valida disponibilidad y persiste en session.
    """
    if request.method == "POST":
        if temporizador_compra_vencido():
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
        butacas_elegidas = []
        for id_b in ids_butacas:
            b = mapa_dict.get(id_b)
            if b is None:
                flash(f"La butaca seleccionada (ID {id_b}) no existe en esta función.", "error")
                return redirect(url_for("compra.seleccion_butacas", id_funcion=id_funcion))
            if b.get("estado") in ("OCUPADA", "RESERVADA"):
                flash(
                    f"La butaca elegida (Fila {b.get('fila', '')} N° {b.get('numero', '')}) ya no está disponible.",
                    "error",
                )
                return redirect(url_for("compra.seleccion_butacas", id_funcion=id_funcion))
            butacas_elegidas.append(b)

        # Obtener detalle de función para precio y datos de la orden
        func_detalle, _ = obtener_detalle_funcion_del_backend(id_funcion)
        precio_unitario = (
            float(func_detalle.get("precio_entrada", 8500))
            if isinstance(func_detalle, dict)
            else 8500.0
        )
        subtotal = precio_unitario * len(butacas_elegidas)

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
            "butacas": [
                {
                    "id_butaca": b["id_butaca"],
                    "fila": b["fila"],
                    "numero": b["numero"],
                    "precio": precio_unitario,
                }
                for b in butacas_elegidas
            ],
            "total_butacas": len(butacas_elegidas),
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
    iniciar_temporizador_compra(id_funcion=id_funcion, id_pelicula=id_pelicula)
    if temporizador_compra_vencido():
        return redirigir_compra_expirada()
    temporizador = contexto_temporizador_compra()

    # Obtener butacas de la sesión previa si corresponden a esta función
    compra_sesion = session.get("compra", {})
    butacas_previas = (
        compra_sesion.get("butacas", [])
        if compra_sesion.get("id_funcion") == id_funcion
        else []
    )
    ids_seleccionadas = {b["id_butaca"] for b in butacas_previas if "id_butaca" in b}

    # Armar filas dinámicas si el backend respondió
    butacas_db = mapa_resp.get("butacas", []) if isinstance(mapa_resp, dict) else []
    filas_construidas = _armar_filas_butacas(butacas_db, ids_seleccionadas)

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
    horario_etiqueta = "Horario a confirmar"
    if inicio_raw:
        try:
            dt = datetime.fromisoformat(inicio_raw)
            horario_etiqueta = f"{formatear_fecha_corta(dt.date())} {formatear_hora(dt)}"
        except Exception:
            horario_etiqueta = inicio_raw

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
            "tiempo_restante": f"{temporizador['tiempo_restante']} min",
            "precio_general": int(precio_base),
            "precio_vip": int(precio_vip),
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
    """Renderiza Candy Bar, controla el vencimiento y conserva los servicios elegidos."""
    if temporizador_compra_vencido():
        return redirigir_compra_expirada()
    if not (session.get("compra") or {}).get("butacas"):
        return redirect(url_for("compra.seleccion_butacas"))

    """Renderiza Candy Bar y conserva sus cantidades en la sesión Flask."""
    if request.method == "POST":
        if not validar_token_csrf(request.form.get("csrf_token", "")):
            flash("Formulario vencido o CSRF inválido.", "error")
            return redirect(url_for("compra.seleccion_servicios"))

        if request.form.get("accion") == "omitir":
            session["servicios_seleccionados"] = []
            return redirect(url_for("compra.seleccion_checkout"))

        try:
            servicios = validar_servicios_seleccionados(
                request.form.get("servicios_json", "[]")
            )
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("compra.seleccion_servicios"))

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
    servicios = [
        {**servicio, "cantidad": cantidades.get(servicio["id_servicio"], 0)}
        for servicio in servicios_api
    ]
    subtotal_entradas = 17000
    items_seleccionados = [
        {
            "id_servicio": servicio["id_servicio"],
            "nombre": servicio["nombre"],
            "descripcion": servicio["descripcion"],
            "cantidad": servicio["cantidad"],
            "subtotal_formato": formatear_monto(
                servicio["precio"] * servicio["cantidad"]
            ),
        }
        for servicio in servicios
        if servicio["cantidad"] > 0
    ]
    subtotal_candy = sum(
        servicio["precio"] * servicio["cantidad"]
        for servicio in servicios
    )
    temporizador = contexto_temporizador_compra()

    datos_compra = {
        "pelicula": {
            "id_pelicula": 2,
            "titulo": "Furiosa: Saga Mad Max",
            "titulo_upper": "FURIOSA: SAGA MAD MAX",
            "poster_url": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&auto=format&fit=crop&q=80",
            "formato": "SALA 2 • 4D",
            "sala_badge": "SALA 2 • 4D",
            "idioma": "Subtitulada",
            "horario_etiqueta": "Hoy 20:15 hs • Subtitulada",
            "complejo": "Paradiso Centro (Corrientes 1240)",
        },
        "entradas": {
            "items": [
                {
                    "descripcion": "2x Entrada General 4D",
                    "detalle": "Butacas E-08, E-09",
                    "subtotal": subtotal_entradas,
                    "subtotal_formato": formatear_monto(subtotal_entradas),
                }
            ],
            "subtotal": subtotal_entradas,
            "subtotal_formato": formatear_monto(subtotal_entradas),
        },
        "categorias_filtro": [
            {"id": "todos", "nombre": "Todos los Servicios"},
            {"id": "comida", "nombre": "COMIDA"},
            {"id": "bebida", "nombre": "BEBIDA"},
        ],
        "servicios": servicios,
        "servicios_seleccionados": [
            item for item in session.get("servicios_seleccionados", [])
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
            "total": subtotal_entradas + subtotal_candy,
            "total_formato": formatear_monto(subtotal_entradas + subtotal_candy),
        },
    }

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

    subtotal_entradas = precio_unitario * cantidad_entradas

    # 6. Construir el desglose de las entradas
    desglose = [
        {
            "titulo": f"{cantidad_entradas}x Entrada",
            "subtexto": compra["pelicula_titulo"],
            "precio": f"${subtotal_entradas:,.0f}".replace(",", "."),
        }
    ]

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

    horario = funcion.get("inicio", compra.get("horario", ""))

    try:
        fecha_funcion = datetime.fromisoformat(horario)

        horario = (
            f"{formatear_fecha_corta(fecha_funcion.date())} "
            f"{formatear_hora(fecha_funcion)}"
        )
    except (ValueError, TypeError):
        pass

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
