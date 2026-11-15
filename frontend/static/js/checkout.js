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

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("checkoutForm");

    if (!form) return;

    form.addEventListener("submit", function (event) {

        const numeroTarjeta = document
            .getElementById("inputNumeroTarjeta")
            .value.replace(/[\s-]/g, "");

        const titular = document
            .getElementById("inputTitularTarjeta")
            .value.trim();

        const vencimiento = document
            .getElementById("inputVencimiento")
            .value.trim();

        const cvv = document
            .getElementById("inputCvv")
            .value.trim();

        const email = document
            .getElementById("inputEmail")
            .value.trim();

        const confirmarEmail = document
            .getElementById("inputEmailConfirm")
            .value.trim();

        // Validar número de tarjeta: entre 13 y 19 dígitos
        if (!/^\d{13,19}$/.test(numeroTarjeta)) {
            event.preventDefault();
            alert("El número de tarjeta no tiene un formato válido.");
            return;
        }

        // Validar titular
        if (!titular) {
            event.preventDefault();
            alert("Ingresá el titular de la tarjeta.");
            return;
        }

        // Validar vencimiento
        const match = vencimiento.match(/^(0[1-9]|1[0-2])\/(\d{2})$/);

        if (!match) {
            event.preventDefault();
            alert("El vencimiento debe tener formato MM/AA.");
            return;
        }

        const mes = Number(match[1]);
        const anio = 2000 + Number(match[2]);
        const hoy = new Date();

        if (
            anio < hoy.getFullYear() ||
            (anio === hoy.getFullYear() && mes < hoy.getMonth() + 1)
        ) {
            event.preventDefault();
            alert("La tarjeta está vencida.");
            return;
        }

        // Validar CVV
        if (!/^\d{3,4}$/.test(cvv)) {
            event.preventDefault();
            alert("El código de seguridad debe tener 3 o 4 dígitos.");
            return;
        }

        // Verificar que coincidan los correos
        if (email !== confirmarEmail) {
            event.preventDefault();
            alert("Los correos electrónicos no coinciden.");
            return;
        }
    });
});
