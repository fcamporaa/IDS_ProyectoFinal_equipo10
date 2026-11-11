/* Interactividad de Checkout y Temporizador de Pago */
document.addEventListener('DOMContentLoaded', function () {
    let totalSeconds = 8 * 60 + 40;
    const countdownEl = document.getElementById('checkoutCountdown');

    if (countdownEl) {
        setInterval(function () {
            if (totalSeconds > 0) {
                totalSeconds--;
                const mins = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
                const secs = String(totalSeconds % 60).padStart(2, '0');
                countdownEl.textContent = `${mins}:${secs}`;
            }
        }, 1000);
    }
});

// Simulación del procesamiento de pago exitoso para este hito
function handleSimulatedPayment(e) {
    if (e) e.preventDefault();
    const form = document.getElementById('checkoutForm');
    const targetUrl = form ? form.getAttribute('action') : '/compra/confirmacion';
    window.location.href = targetUrl;
    return false;
}
