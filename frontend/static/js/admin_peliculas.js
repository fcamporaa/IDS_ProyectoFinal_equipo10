/* Interactividad del ABM de películas: modales, confirmación y vista previa del póster. */
document.addEventListener('DOMContentLoaded', function () {
    let elementoConFoco = null;

    function abrirModal(modal) {
        if (!modal) return;
        elementoConFoco = document.activeElement;
        modal.hidden = false;
        modal.classList.add('modal--abierto');
        document.body.classList.add('modal-abierto');

        const dialogo = modal.querySelector('.modal__dialog');
        if (dialogo) dialogo.focus();
    }

    function cerrarModal(modal) {
        if (!modal) return;
        modal.hidden = true;
        modal.classList.remove('modal--abierto');
        if (!document.querySelector('.modal--abierto')) {
            document.body.classList.remove('modal-abierto');
        }
        if (elementoConFoco && typeof elementoConFoco.focus === 'function') {
            elementoConFoco.focus();
        }
    }

    document.querySelectorAll('[data-modal-open]').forEach(function (boton) {
        boton.addEventListener('click', function () {
            abrirModal(document.getElementById(boton.dataset.modalOpen));
        });
    });

    document.querySelectorAll('[data-modal-close]').forEach(function (elemento) {
        elemento.addEventListener('click', function (evento) {
            evento.preventDefault();
            cerrarModal(elemento.closest('.modal'));
        });
    });

    document.addEventListener('keydown', function (evento) {
        if (evento.key !== 'Escape') return;
        const modalAbierto = document.querySelector('.modal--abierto');
        if (modalAbierto) cerrarModal(modalAbierto);
    });

    document.querySelectorAll('form[data-confirmar-baja]').forEach(function (formulario) {
        formulario.addEventListener('submit', function (evento) {
            const modal = document.getElementById(
                formulario.dataset.modalDestino || 'modal-confirmar-baja'
            );
            const formModal = modal ? modal.querySelector('form') : null;
            if (!modal || !formModal) return;

            evento.preventDefault();
            formModal.action = formulario.action;

            const nombrePelicula = modal.querySelector('[data-modal-pelicula]');
            if (nombrePelicula) {
                nombrePelicula.textContent = formulario.dataset.tituloPelicula || '';
            }
            abrirModal(modal);
        });
    });

    const inputPoster = document.querySelector('input[name="poster_url"]');
    const previewPoster = document.querySelector('[data-poster-preview]');
    if (inputPoster && previewPoster) {
        const imagen = previewPoster.querySelector('[data-poster-preview-img]');
        const vacio = previewPoster.querySelector('[data-poster-preview-empty]');

        const actualizarPreview = function () {
            if (!imagen) return;
            const url = inputPoster.value.trim();
            if (url) {
                imagen.src = url;
                imagen.hidden = false;
                if (vacio) vacio.hidden = true;
            } else {
                imagen.removeAttribute('src');
                imagen.hidden = true;
                if (vacio) vacio.hidden = false;
            }
        };

        inputPoster.addEventListener('input', actualizarPreview);
        imagen.addEventListener('error', function () {
            imagen.hidden = true;
            if (vacio) vacio.hidden = false;
        });
        actualizarPreview();
    }

    const formularioPelicula = document.getElementById('form-pelicula');
    if (
        formularioPelicula &&
        formularioPelicula.dataset.abrirFormulario === 'true'
    ) {
        formularioPelicula.scrollIntoView({ behavior: 'smooth', block: 'start' });
        const primerCampo = formularioPelicula.querySelector(
            'input:not([type="hidden"]), textarea, select'
        );
        if (primerCampo) primerCampo.focus({ preventScroll: true });
    }
});
