document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("checkoutForm");

    if (!form) return;

    // Comprueba el dígito de control de un número de tarjeta (algoritmo de Luhn).
    // No verifica que la tarjeta exista, esté habilitada o tenga fondos.
    function cumpleLuhn(numero) {
        let suma = 0;
        let duplicar = false;

        for (let i = numero.length - 1; i >= 0; i--) {
            let digito = Number(numero[i]);

            if (duplicar) {
                digito *= 2;
                if (digito > 9) digito -= 9;
            }

            suma += digito;
            duplicar = !duplicar;
        }

        return suma % 10 === 0 && !/^0+$/.test(numero);
    }

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

        const dni = document
            .getElementById("inputDni")
            .value.trim();

        const email = document
            .getElementById("inputEmail")
            .value.trim();

        const confirmarEmail = document
            .getElementById("inputEmailConfirm")
            .value.trim();

        // Validar formato y cantidad de dígitos (13 a 19).
        if (!/^\d{13,19}$/.test(numeroTarjeta)) {
            event.preventDefault();
            alert("Ingresá un número de tarjeta de entre 13 y 19 dígitos.");
            return;
        }

        // Validar el dígito de control.
        if (!cumpleLuhn(numeroTarjeta)) {
            event.preventDefault();
            alert("El número de tarjeta no supera la verificación de Luhn.");
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

        // Validar DNI argentino: de 1.000.000 a 99.999.999, sin separadores.
        if (!/^[1-9][0-9]{6,7}$/.test(dni)) {
            event.preventDefault();
            alert("Ingresá un DNI válido de 7 u 8 dígitos, sin puntos ni espacios.");
            return;
        }

        // Verificar que coincidan los correos
        if (email !== confirmarEmail) {
            event.preventDefault();
            alert("Los correos electrónicos no coinciden.");
            return;
        }

        // Deshabilitar botón para evitar envíos múltiples o doble clic
        const btnSubmit = document.querySelector(".btn-confirm-payment");
        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = "<span>PROCESANDO COMPRA...</span>";
        }
    });
});
