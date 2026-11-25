/* Interactividad del ABM de funciones: formulario desplegable y filtro complejo -> sala. */
document.addEventListener('DOMContentLoaded', function () {
    const contenedor = document.getElementById('contenedor-formulario');
    const formulario = document.getElementById('form-funcion');
    const abrirFormulario = contenedor && (
        contenedor.classList.contains('admin-funciones__form-container--activo') ||
        new URLSearchParams(window.location.search).get('nuevo') === '1'
    );

    if (abrirFormulario) {
        contenedor.classList.add('admin-funciones__form-container--activo');
        if (formulario) {
            formulario.scrollIntoView({ behavior: 'smooth', block: 'start' });
            const primerCampo = formulario.querySelector(
                'select, input:not([type="hidden"]), textarea'
            );
            if (primerCampo) primerCampo.focus({ preventScroll: true });
        }
    }

    const selectorLocal = document.getElementById('id_local');
    const selectorSala = document.getElementById('id_sala');
    if (!selectorLocal || !selectorSala) return;

    const opcionesSala = Array.from(
        selectorSala.querySelectorAll('option[data-local]')
    ).map(function (opcion) {
        return opcion.cloneNode(true);
    });

    function filtrarSalas() {
        const localId = selectorLocal.value;
        const salaActual = selectorSala.value;

        selectorSala.replaceChildren(new Option('Seleccioná una sala', ''));
        selectorSala.value = '';

        if (!localId) {
            selectorSala.disabled = true;
            return;
        }

        const opcionesLocal = opcionesSala.filter(function (opcion) {
            return opcion.dataset.local === localId;
        });
        opcionesLocal.forEach(function (opcion) {
            const copia = opcion.cloneNode(true);
            copia.selected = false;
            selectorSala.appendChild(copia);
        });

        selectorSala.disabled = opcionesLocal.length === 0;
        const salaSigueDisponible = opcionesLocal.some(function (opcion) {
            return opcion.value === salaActual;
        });
        if (salaSigueDisponible) selectorSala.value = salaActual;
    }

    selectorLocal.addEventListener('change', filtrarSalas);
    filtrarSalas();
});
