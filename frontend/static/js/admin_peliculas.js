/* Interactividad específica del ABM de películas: vista previa del póster y foco del formulario. */
document.addEventListener('DOMContentLoaded', function () {
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
        if (imagen) {
            imagen.addEventListener('error', function () {
                imagen.hidden = true;
                if (vacio) vacio.hidden = false;
            });
        }
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
