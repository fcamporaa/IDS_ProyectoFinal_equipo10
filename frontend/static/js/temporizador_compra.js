/* Cuenta regresiva compartida, sin AJAX. El servidor decide el vencimiento. */
document.addEventListener('DOMContentLoaded', function () {
    const reloj = document.querySelector('[data-expira-en-ms][data-ahora-servidor-ms]');
    if (!reloj) return;

    const expiraEn = Number(reloj.dataset.expiraEnMs);
    const horaServidor = Number(reloj.dataset.ahoraServidorMs);
    const urlExpiracion = reloj.dataset.urlExpiracion;
    const sufijo = reloj.dataset.sufijo || '';
    if (!Number.isFinite(expiraEn) || !Number.isFinite(horaServidor) || !urlExpiracion) return;

    const restanteInicialMs = Math.max(0, expiraEn - horaServidor);
    const inicioMonotonico = performance.now();
    let redirigiendo = false;

    function actualizar() {
        const transcurridoMs = performance.now() - inicioMonotonico;
        const segundos = Math.max(0, Math.ceil((restanteInicialMs - transcurridoMs) / 1000));
        const minutos = String(Math.floor(segundos / 60)).padStart(2, '0');
        const segundosResto = String(segundos % 60).padStart(2, '0');
        reloj.textContent = `${minutos}:${segundosResto}${sufijo}`;

        if (segundos === 0 && !redirigiendo) {
            redirigiendo = true;
            window.location.replace(urlExpiracion);
        }
    }

    actualizar();
    setInterval(actualizar, 500);
    document.addEventListener('visibilitychange', actualizar);
});
