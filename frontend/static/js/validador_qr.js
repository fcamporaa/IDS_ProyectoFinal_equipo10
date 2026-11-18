(function () {
    "use strict";

    var PATRON_TOKEN = /^[A-Za-z0-9_-]{8,160}$/;
    var STORAGE_CAMARA = "cp_qr_camara_activa";
    var STORAGE_ULTIMO_TOKEN = "cp_qr_ultimo_token";
    var STORAGE_ULTIMO_TS = "cp_qr_ultimo_ts";
    var COOLDOWN_MS = 4500;

    var formulario = document.getElementById("validadorQrForm");
    var inputToken = document.getElementById("qr_token");
    var seccionCamara = document.getElementById("qrCameraSection");
    var visor = document.getElementById("qrVisor");
    var video = document.getElementById("qrVideo");
    var placeholder = document.getElementById("qrPlaceholder");
    var badgeEstado = document.getElementById("qrSensorBadge");
    var textoEstado = document.getElementById("qrSensorTexto");
    var mensajeCamara = document.getElementById("qrCamaraMensaje");
    var btnToggleCamara = document.getElementById("btnToggleCamara");

    if (!formulario || !inputToken || !visor || !video || !btnToggleCamara) {
        return;
    }

    var streamActivo = null;
    var animacionId = null;
    var escaneando = false;
    var detectorNativo = null;
    var canvasOculto = document.createElement("canvas");
    var contextoCanvas = canvasOculto.getContext("2d", { willReadFrequently: true });

    function establecerEstadoVisor(activo, texto, mensaje, mantenerAbierto) {
        visor.classList.toggle("is-scanning", activo);
        visor.classList.toggle("is-open", Boolean(activo || mantenerAbierto));
        if (badgeEstado) {
            badgeEstado.classList.toggle("is-live", activo);
        }
        if (textoEstado && texto) {
            textoEstado.textContent = texto;
        }
        if (placeholder) {
            placeholder.hidden = activo;
        }
        btnToggleCamara.textContent = activo ? "Detener cámara" : "Escanear con cámara";
        btnToggleCamara.setAttribute("aria-pressed", activo ? "true" : "false");
        if (mensajeCamara) {
            mensajeCamara.textContent = mensaje || "";
            mensajeCamara.hidden = !mensaje;
        }
    }

    function detenerCamara(guardarPreferencia, estadoTexto, mensaje) {
        escaneando = false;
        if (animacionId !== null) {
            cancelAnimationFrame(animacionId);
            animacionId = null;
        }
        if (streamActivo) {
            streamActivo.getTracks().forEach(function (track) {
                track.stop();
            });
            streamActivo = null;
        }
        video.srcObject = null;
        if (guardarPreferencia) {
            sessionStorage.setItem(STORAGE_CAMARA, "0");
        }
        establecerEstadoVisor(false, estadoTexto || "MODO MANUAL", mensaje || "", Boolean(mensaje));
    }

    async function inicializarDetectorNativo() {
        if (!("BarcodeDetector" in window)) {
            return null;
        }
        try {
            if (typeof window.BarcodeDetector.getSupportedFormats === "function") {
                var formatos = await window.BarcodeDetector.getSupportedFormats();
                if (formatos.indexOf("qr_code") === -1) {
                    return null;
                }
            }
            return new window.BarcodeDetector({ formats: ["qr_code"] });
        } catch (_err) {
            return null;
        }
    }

    function leerFrameConJsQr() {
        if (typeof window.jsQR !== "function") {
            return null;
        }
        var ancho = video.videoWidth;
        var alto = video.videoHeight;
        if (!ancho || !alto) {
            return null;
        }
        canvasOculto.width = ancho;
        canvasOculto.height = alto;
        contextoCanvas.drawImage(video, 0, 0, ancho, alto);
        var imagen = contextoCanvas.getImageData(0, 0, ancho, alto);
        var resultado = window.jsQR(imagen.data, ancho, alto, {
            inversionAttempts: "dontInvert",
        });
        return resultado ? resultado.data : null;
    }

    async function detectarCodigoEnFrame() {
        if (detectorNativo) {
            var codigos = await detectorNativo.detect(video);
            if (codigos && codigos.length > 0 && codigos[0].rawValue) {
                return codigos[0].rawValue;
            }
        }
        return leerFrameConJsQr();
    }

    function esMismoTokenEnCooldown(token) {
        var ultimo = sessionStorage.getItem(STORAGE_ULTIMO_TOKEN);
        var ts = Number(sessionStorage.getItem(STORAGE_ULTIMO_TS) || "0");
        return ultimo === token && Date.now() - ts < COOLDOWN_MS;
    }

    function procesarCodigoDetectado(valorCrudo) {
        var token = (valorCrudo || "").trim();
        if (!token) {
            return false;
        }
        if (esMismoTokenEnCooldown(token)) {
            establecerEstadoVisor(
                true,
                "SENSOR ACTIVO",
                "QR recién evaluado. Retirá la pantalla o acercá la siguiente entrada."
            );
            return false;
        }
        if (!PATRON_TOKEN.test(token)) {
            establecerEstadoVisor(
                true,
                "SENSOR ACTIVO",
                "El código leído no corresponde a una entrada de Cine Paradiso."
            );
            return false;
        }

        sessionStorage.setItem(STORAGE_ULTIMO_TOKEN, token);
        sessionStorage.setItem(STORAGE_ULTIMO_TS, String(Date.now()));
        inputToken.value = token;
        detenerCamara(false);
        formulario.submit();
        return true;
    }

    async function cicloEscaneo() {
        if (!escaneando) {
            return;
        }
        try {
            if (video.readyState >= 2) {
                var detectado = await detectarCodigoEnFrame();
                if (detectado && procesarCodigoDetectado(detectado)) {
                    return;
                }
            }
        } catch (_err) {
            // Continúa en el siguiente frame si una lectura puntual falla.
        }
        animacionId = requestAnimationFrame(cicloEscaneo);
    }

    function describirErrorCamara(error) {
        var nombre = (error && error.name) || "";
        if (nombre === "NotFoundError" || nombre === "DevicesNotFoundError") {
            return {
                badge: "SIN CÁMARA",
                mensaje: "No se detectó ninguna cámara conectada en este equipo. Usá el ingreso manual o lector USB.",
            };
        }
        if (nombre === "NotAllowedError" || nombre === "PermissionDeniedError") {
            return {
                badge: "PERMISO BLOQUEADO",
                mensaje: "El navegador bloqueó el acceso a la cámara. Habilitalo desde el ícono junto a la URL o usá el ingreso manual.",
            };
        }
        if (nombre === "NotReadableError" || nombre === "TrackStartError") {
            return {
                badge: "CÁMARA OCUPADA",
                mensaje: "La cámara está siendo utilizada por otra aplicación. Cerrala o usá el ingreso manual.",
            };
        }
        return {
            badge: "CÁMARA NO DISPONIBLE",
            mensaje: "No se pudo iniciar la cámara (" + (nombre || "error del navegador") + "). Usá el ingreso manual.",
        };
    }

    async function solicitarStreamCamara() {
        try {
            return await navigator.mediaDevices.getUserMedia({
                video: { facingMode: { ideal: "environment" } },
                audio: false,
            });
        } catch (error) {
            if (error && (error.name === "OverconstrainedError" || error.name === "ConstraintNotSatisfiedError")) {
                return await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            }
            throw error;
        }
    }

    async function iniciarCamara() {
        if (escaneando) {
            return;
        }
        if (!navigator.mediaDevices || typeof navigator.mediaDevices.getUserMedia !== "function") {
            establecerEstadoVisor(
                false,
                "CÁMARA NO DISPONIBLE",
                "El navegador no habilita cámara en esta URL (requiere localhost o HTTPS). Usá el ingreso manual.",
                false
            );
            return;
        }

        try {
            streamActivo = await solicitarStreamCamara();
        } catch (error) {
            sessionStorage.setItem(STORAGE_CAMARA, "0");
            var detalle = describirErrorCamara(error);
            establecerEstadoVisor(false, detalle.badge, detalle.mensaje, false);
            return;
        }

        detectorNativo = await inicializarDetectorNativo();
        if (!detectorNativo && typeof window.jsQR !== "function") {
            detenerCamara(
                true,
                "MODO MANUAL",
                "Se abrió la cámara pero no hay decodificador QR disponible sin conexión. Usá el ingreso manual."
            );
            return;
        }

        try {
            video.srcObject = streamActivo;
            await video.play();
            escaneando = true;
            sessionStorage.setItem(STORAGE_CAMARA, "1");
            establecerEstadoVisor(true, "SENSOR ACTIVO", "", true);
            animacionId = requestAnimationFrame(cicloEscaneo);
        } catch (error) {
            var detallePlay = describirErrorCamara(error);
            detenerCamara(true, detallePlay.badge, detallePlay.mensaje);
        }
    }

    btnToggleCamara.addEventListener("click", function () {
        if (escaneando) {
            detenerCamara(true);
        } else {
            iniciarCamara();
        }
    });

    formulario.addEventListener("submit", function () {
        detenerCamara(false);
    });

    window.addEventListener("beforeunload", function () {
        if (streamActivo) {
            streamActivo.getTracks().forEach(function (track) {
                track.stop();
            });
        }
    });

    function ocultarCamaraSinHardwareEnDesktop() {
        if (
            !seccionCamara ||
            !window.matchMedia("(min-width: 769px)").matches ||
            !navigator.mediaDevices ||
            typeof navigator.mediaDevices.enumerateDevices !== "function"
        ) {
            return;
        }
        navigator.mediaDevices
            .enumerateDevices()
            .then(function (dispositivos) {
                var tieneCamara = dispositivos.some(function (d) {
                    return d.kind === "videoinput";
                });
                if (!tieneCamara) {
                    seccionCamara.hidden = true;
                }
            })
            .catch(function () {
                // Si el navegador bloquea la enumeración, conserva el botón disponible.
            });
    }

    ocultarCamaraSinHardwareEnDesktop();

    if (sessionStorage.getItem(STORAGE_CAMARA) === "1") {
        iniciarCamara();
    }
})();
