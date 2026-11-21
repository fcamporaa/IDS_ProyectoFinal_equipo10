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

    const gruposOriginales = Array.from(
        selectorSala.querySelectorAll('optgroup')
    ).map(function (grupo) {
        return grupo.cloneNode(true);
    });
    const opcionesSueltas = Array.from(
        selectorSala.querySelectorAll('option[data-local]')
    ).map(function (opcion) {
        return opcion.cloneNode(true);
    });
    const opcionVacia = selectorSala.querySelector('option[value=""]');

    function filtrarSalas(seleccionarPrimera) {
        const localId = selectorLocal.value;
        const salaActual = selectorSala.value;
        let primeraVisible = null;
        let salaActualSigueVisible = false;

        selectorSala.replaceChildren(
            opcionVacia
                ? opcionVacia.cloneNode(true)
                : new Option('Seleccioná una sala', '')
        );

        function agregarOpcion(origen, destino) {
            const copia = origen.cloneNode(true);
            copia.selected = false;
            destino.appendChild(copia);
            if (copia.value === salaActual) salaActualSigueVisible = true;
            if (!primeraVisible) primeraVisible = copia;
        }

        gruposOriginales.forEach(function (grupo) {
            const opcionesVisibles = Array.from(
                grupo.querySelectorAll('option[data-local]')
            ).filter(function (opcion) {
                return !localId || opcion.dataset.local === localId;
            });
            if (!opcionesVisibles.length) return;

            const nuevoGrupo = grupo.cloneNode(false);
            opcionesVisibles.forEach(function (opcion) {
                agregarOpcion(opcion, nuevoGrupo);
            });
            selectorSala.appendChild(nuevoGrupo);
        });

        opcionesSueltas.forEach(function (opcion) {
            if (!localId || opcion.dataset.local === localId) {
                agregarOpcion(opcion, selectorSala);
            }
        });

        if (salaActualSigueVisible) {
            selectorSala.value = salaActual;
        } else if (seleccionarPrimera && primeraVisible) {
            selectorSala.value = primeraVisible.value;
        } else {
            selectorSala.value = '';
        }
    }

    selectorLocal.addEventListener('change', function () {
        filtrarSalas(true);
    });

    if (selectorLocal.value) {
        filtrarSalas(true);
    }
});
