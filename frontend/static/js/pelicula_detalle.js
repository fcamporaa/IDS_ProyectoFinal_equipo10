/* Interactividad del Detalle de Película y Selección de Funciones */
document.addEventListener('DOMContentLoaded', function () {
    // Elementos de la barra flotante
    const displayComplex = document.getElementById('selectedComplexDisplay');
    const displayDate = document.getElementById('selectedDateDisplay');
    const displayHall = document.getElementById('selectedHallDisplay');
    const displayTime = document.getElementById('selectedTimeDisplay');
    const displayPrice = document.getElementById('selectedPriceDisplay');

    // Selector de Complejos
    const complexCards = document.querySelectorAll('.complex-card');
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

            if (displayComplex) {
                displayComplex.textContent = card.getAttribute('data-complex-name');
            }
        });
    });

    // Selector de Fechas
    const datePills = document.querySelectorAll('.showtime-date-pill');
    datePills.forEach(function (pill) {
        pill.addEventListener('click', function () {
            datePills.forEach(function (p) { p.classList.remove('active'); });
            pill.classList.add('active');
            if (displayDate) {
                displayDate.textContent = pill.getAttribute('data-date');
            }
        });
    });

    // Selector de Horarios
    const showtimeCards = document.querySelectorAll('.showtime-select-card');
    showtimeCards.forEach(function (btn) {
        btn.addEventListener('click', function () {
            showtimeCards.forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');

            const time = btn.getAttribute('data-func-time');
            const badge = btn.getAttribute('data-hall-badge');
            const price = btn.getAttribute('data-hall-price');
            const hallName = btn.getAttribute('data-hall-name');

            if (displayTime) displayTime.textContent = time;
            if (displayHall) displayHall.textContent = hallName.split('—')[0].trim() + ' (' + badge + ')';
            if (displayPrice) displayPrice.textContent = price;
        });
    });

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

