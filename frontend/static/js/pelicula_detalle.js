/* Interactividad del Detalle de Película y Selección de Funciones */
document.addEventListener('DOMContentLoaded', function () {
    // Elementos de la barra flotante
    const displayComplex = document.getElementById('selectedComplexDisplay');
    const displayDate = document.getElementById('selectedDateDisplay');
    const displayHall = document.getElementById('selectedHallDisplay');
    const displayTime = document.getElementById('selectedTimeDisplay');
    const displayPrice = document.getElementById('selectedPriceDisplay');

    const complexCards = document.querySelectorAll('.complex-card');
    const datePills = document.querySelectorAll('.showtime-date-pill');
    const hallBlocks = document.querySelectorAll('.hall-showtime-block');
    const showtimeCards = document.querySelectorAll('.showtime-select-card');
    const btnContinueSeats = document.getElementById('btnContinueSeats');

    function seleccionarHorario(btn) {
        showtimeCards.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');

        const funcId = btn.getAttribute('data-func-id');
        const time = btn.getAttribute('data-func-time');
        const badge = btn.getAttribute('data-hall-badge');
        const price = btn.getAttribute('data-hall-price');
        const hallName = btn.getAttribute('data-hall-name');

        if (displayTime) displayTime.textContent = time;
        if (displayHall) displayHall.textContent = hallName.split('—')[0].trim() + ' (' + badge + ')';
        if (displayPrice) displayPrice.textContent = price;

        if (btnContinueSeats && funcId) {
            const url = new URL(btnContinueSeats.href, window.location.origin);
            url.searchParams.set('id_funcion', funcId);
            btnContinueSeats.href = url.pathname + url.search;
        }
    }

    // Muestra solo las funciones del complejo y la fecha elegidos.
    // Las fechas sin funciones en ese complejo se ocultan, así no hay combinaciones vacías.
    function aplicarFiltros() {
        const complejoActivo = document.querySelector('.complex-card.active');
        if (!complejoActivo) return;
        const complexId = complejoActivo.getAttribute('data-complex-id');

        const fechasDelComplejo = new Set();
        hallBlocks.forEach(function (bloque) {
            if (bloque.getAttribute('data-complex-id') === complexId) {
                fechasDelComplejo.add(bloque.getAttribute('data-date-id'));
            }
        });

        let fechaActiva = null;
        datePills.forEach(function (pill) {
            const disponible = fechasDelComplejo.has(pill.getAttribute('data-date-id'));
            pill.style.display = disponible ? '' : 'none';
            if (!disponible) pill.classList.remove('active');
            else if (pill.classList.contains('active')) fechaActiva = pill;
        });
        if (!fechaActiva) {
            fechaActiva = Array.from(datePills).find(function (pill) {
                return pill.style.display !== 'none';
            }) || null;
            if (fechaActiva) fechaActiva.classList.add('active');
        }
        if (!fechaActiva) return;
        const dateId = fechaActiva.getAttribute('data-date-id');

        hallBlocks.forEach(function (bloque) {
            const visible = bloque.getAttribute('data-complex-id') === complexId
                && bloque.getAttribute('data-date-id') === dateId;
            bloque.style.display = visible ? '' : 'none';
            if (!visible) {
                bloque.querySelectorAll('.showtime-select-card.active').forEach(function (c) {
                    c.classList.remove('active');
                });
            }
        });

        if (displayComplex) displayComplex.textContent = complejoActivo.getAttribute('data-complex-name');
        if (displayDate) displayDate.textContent = fechaActiva.getAttribute('data-date');

        // Sincroniza barra y botón con el horario activo (o con el primero visible).
        const horario = document.querySelector('.showtime-select-card.active')
            || Array.from(showtimeCards).find(function (c) {
                return c.closest('.hall-showtime-block').style.display !== 'none';
            });
        if (horario) seleccionarHorario(horario);
    }

    // Selector de Complejos
    complexCards.forEach(function (card) {
        card.addEventListener('click', function () {
            complexCards.forEach(function (c) {
                c.classList.remove('active');
                const radio = c.querySelector('.complex-radio-circle');
                if (radio) radio.innerHTML = '';
                const roleTag = c.querySelector('.complex-role-tag');
                if (roleTag) roleTag.classList.remove('tag-red');
            });

            card.classList.add('active');
            const radio = card.querySelector('.complex-radio-circle');
            if (radio) radio.innerHTML = '<span class="radio-check-mark">✓</span>';
            const roleTag = card.querySelector('.complex-role-tag');
            if (roleTag) roleTag.classList.add('tag-red');

            aplicarFiltros();
        });
    });

    // Selector de Fechas
    datePills.forEach(function (pill) {
        pill.addEventListener('click', function () {
            datePills.forEach(function (p) { p.classList.remove('active'); });
            pill.classList.add('active');
            aplicarFiltros();
        });
    });

    // Selector de Horarios
    showtimeCards.forEach(function (btn) {
        btn.addEventListener('click', function () { seleccionarHorario(btn); });
    });

    aplicarFiltros();

    // Modal de Tráiler (Se activa desde el póster)
    const openTrailerBtn = document.getElementById('openTrailerBtn');
    const closeTrailerBtn = document.getElementById('closeTrailerBtn');
    const trailerModal = document.getElementById('trailerModal');
    const trailerIframe = document.getElementById('trailerIframe');

    function openModal() {
        if (trailerModal && trailerIframe) {
            trailerIframe.src = trailerIframe.getAttribute('data-src');
            trailerModal.classList.add('active');
        }
    }

    function closeModal() {
        if (trailerModal && trailerIframe) {
            trailerIframe.src = '';
            trailerModal.classList.remove('active');
        }
    }

    if (openTrailerBtn) openTrailerBtn.addEventListener('click', openModal);
    if (closeTrailerBtn) closeTrailerBtn.addEventListener('click', closeModal);
    if (trailerModal) {
        trailerModal.addEventListener('click', function (e) {
            if (e.target === trailerModal) closeModal();
        });
    }
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && trailerModal && trailerModal.classList.contains('active')) {
            closeModal();
        }
    });

    // Botón Compartir
    const btnCompartir = document.getElementById('btnCompartirPelicula');
    if (btnCompartir) {
        btnCompartir.addEventListener('click', function () {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(window.location.href);
                const originalText = btnCompartir.innerHTML;
                btnCompartir.innerHTML = '<span>✓</span><span>¡Copiado!</span>';
                setTimeout(function () { btnCompartir.innerHTML = originalText; }, 2000);
            }
        });
    }
});

