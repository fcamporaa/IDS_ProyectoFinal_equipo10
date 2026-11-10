/* Interactividad de Selección de Butacas (Sin peticiones AJAX ni WebSockets - SSR Nativo) */
document.addEventListener('DOMContentLoaded', function () {
    const seatsMatrix = document.getElementById('seatsMatrix');
    const assignedList = document.getElementById('assignedSeatsList');
    const countBadge = document.getElementById('seatsCountBadge');
    const displaySubtotal = document.getElementById('displaySubtotal');
    const displayTotal = document.getElementById('displayTotal');
    const inputHidden = document.getElementById('inputButacasSeleccionadas');
    const formSeleccion = document.getElementById('formSeleccionButacas');

    if (!seatsMatrix || !assignedList || !countBadge) return;

    let selectedSeats = [];

    function formatMoney(amount) {
        return '$' + amount.toLocaleString('es-AR');
    }

    function syncHiddenInput() {
        if (inputHidden) {
            const ids = selectedSeats.map(function (s) { return s.id_butaca; });
            inputHidden.value = JSON.stringify(ids);
        }
    }

    function updateSidebar() {
        // Actualizar badge
        countBadge.textContent = selectedSeats.length + (selectedSeats.length === 1 ? ' Butaca' : ' Butacas');

        // Renderizar items en la columna lateral
        assignedList.innerHTML = '';
        let total = 0;

        selectedSeats.forEach(function (s) {
            total += s.precio;
            const item = document.createElement('div');
            item.className = 'assigned-seat-item';
            item.setAttribute('data-item-id', s.id);
            item.innerHTML = `
                <div class="assigned-seat-left">
                    <div class="seat-icon-amber">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                            <path d="M4 18v3h3v-3h10v3h3v-3h1a1 1 0 0 0 1-1v-8a4 4 0 0 0-4-4h-1V3a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v2H6a4 4 0 0 0-4 4v8a1 1 0 0 0 1 1h1z"/>
                        </svg>
                    </div>
                    <div class="assigned-seat-texts">
                        <span class="seat-name-title">Fila ${s.fila} • Butaca ${s.butaca}</span>
                        <span class="seat-category-sub">${s.categoria}</span>
                    </div>
                </div>
                <div class="assigned-seat-right">
                    <span class="seat-price-val">${formatMoney(s.precio)}</span>
                    <button type="button" class="btn-remove-seat" data-remove-id="${s.id}" title="Quitar butaca">
                        <svg viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </button>
                </div>
            `;
            assignedList.appendChild(item);
        });

        // Actualizar montos en pantalla
        if (displaySubtotal) displaySubtotal.textContent = formatMoney(total);
        if (displayTotal) displayTotal.textContent = formatMoney(total);

        // Sincronizar el campo del formulario POST
        syncHiddenInput();

        // Re-vincular botones de eliminar del sidebar
        bindRemoveButtons();
    }

    function toggleSeat(btn) {
        const seatId = parseInt(btn.getAttribute('data-seat-id'), 10);
        const seatCode = btn.getAttribute('data-seat-code') || btn.getAttribute('data-seat-id');
        const row = btn.getAttribute('data-seat-row');
        const num = parseInt(btn.getAttribute('data-seat-num'), 10);
        const isVip = btn.getAttribute('data-seat-vip') === 'true';
        const price = parseInt(btn.getAttribute('data-seat-price'), 10) || 0;
        const category = isVip ? 'VIP D-BOX' : 'General';

        const existingIndex = selectedSeats.findIndex(function (s) {
            return s.id_butaca === seatId;
        });

        if (existingIndex >= 0) {
            // Deseleccionar
            selectedSeats.splice(existingIndex, 1);
            btn.classList.remove('selected');
            btn.textContent = '';
        } else {
            // Seleccionar
            selectedSeats.push({
                id_butaca: seatId,
                id: seatCode,
                fila: row,
                butaca: num,
                categoria: category,
                precio: price
            });
            btn.classList.add('selected');
            btn.textContent = num;
        }

        updateSidebar();
    }

    // Delegación de clicks en la matriz de la sala
    seatsMatrix.addEventListener('click', function (e) {
        const btn = e.target.closest('.seat-button');
        // Si no es un botón de asiento o está ocupado/deshabilitado, no hacer nada
        if (!btn || btn.classList.contains('occupied') || btn.disabled) return;
        toggleSeat(btn);
    });

    // Quitar desde el sidebar
    function bindRemoveButtons() {
        const removeBtns = document.querySelectorAll('.btn-remove-seat');
        removeBtns.forEach(function (b) {
            b.addEventListener('click', function () {
                const removeId = b.getAttribute('data-remove-id');
                const seatBtn = document.querySelector(`.seat-button[data-seat-code="${removeId}"]`) ||
                                document.querySelector(`.seat-button[data-seat-id="${removeId}"]`);
                if (seatBtn) {
                    toggleSeat(seatBtn);
                }
            });
        });
    }

    // Cargar selección inicial de butacas si la página ya las renderizó marcadas desde Flask
    const initialButtons = seatsMatrix.querySelectorAll('.seat-button.selected');
    initialButtons.forEach(function (btn) {
        selectedSeats.push({
            id_butaca: parseInt(btn.getAttribute('data-seat-id'), 10),
            id: btn.getAttribute('data-seat-code') || btn.getAttribute('data-seat-id'),
            fila: btn.getAttribute('data-seat-row'),
            butaca: parseInt(btn.getAttribute('data-seat-num'), 10),
            categoria: btn.getAttribute('data-seat-vip') === 'true' ? 'VIP D-BOX' : 'General',
            precio: parseInt(btn.getAttribute('data-seat-price'), 10) || 0
        });
    });
    updateSidebar();

    // Validación al enviar el formulario (POST nativo)
    if (formSeleccion) {
        formSeleccion.addEventListener('submit', function (e) {
            if (selectedSeats.length === 0) {
                e.preventDefault();
                alert('Por favor seleccioná al menos una butaca libre para continuar.');
            }
        });
    }

    // Cuenta regresiva visual del temporizador (10 minutos)
    let totalSeconds = 10 * 60;
    const countdownEl = document.getElementById('timerCountdown');
    if (countdownEl) {
        setInterval(function () {
            if (totalSeconds > 0) {
                totalSeconds--;
                const mins = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
                const secs = String(totalSeconds % 60).padStart(2, '0');
                countdownEl.textContent = `${mins}:${secs} min`;
            }
        }, 1000);
    }
});
