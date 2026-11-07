/* Interactividad de Selección de Butacas (Sin peticiones AJAX ni fetch) */
document.addEventListener('DOMContentLoaded', function () {
    const seatsMatrix = document.getElementById('seatsMatrix');
    const assignedList = document.getElementById('assignedSeatsList');
    const countBadge = document.getElementById('seatsCountBadge');
    const displaySubtotal = document.getElementById('displaySubtotal');
    const displayTotal = document.getElementById('displayTotal');

    if (!seatsMatrix || !assignedList || !countBadge) return;

    let selectedSeats = [
        { id: 'E-7', fila: 'E', butaca: 7, categoria: 'General 4D', precio: 8500 },
        { id: 'E-8', fila: 'E', butaca: 8, categoria: 'General 4D', precio: 8500 }
    ];

    function formatMoney(amount) {
        return '$' + amount.toLocaleString('es-AR');
    }

    function updateSidebar() {
        // Actualizar badge
        countBadge.textContent = selectedSeats.length + (selectedSeats.length === 1 ? ' Butaca' : ' Butacas');

        // Renderizar items
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

        // Actualizar montos
        if (displaySubtotal) displaySubtotal.textContent = formatMoney(total);
        if (displayTotal) displayTotal.textContent = formatMoney(total);

        // Re-vincular botones de quitar
        bindRemoveButtons();
    }

    function toggleSeat(btn) {
        const seatId = btn.getAttribute('data-seat-id');
        const row = btn.getAttribute('data-seat-row');
        const num = parseInt(btn.getAttribute('data-seat-num'), 10);
        const isVip = btn.getAttribute('data-seat-vip') === 'true';
        const price = parseInt(btn.getAttribute('data-seat-price'), 10) || 0;
        const category = isVip ? 'VIP D-BOX' : 'General 4D';

        const existingIndex = selectedSeats.findIndex(function (s) { return s.id === seatId; });

        if (existingIndex >= 0) {
            // Deseleccionar
            selectedSeats.splice(existingIndex, 1);
            btn.classList.remove('selected');
            btn.textContent = '';
        } else {
            // Seleccionar
            selectedSeats.push({
                id: seatId,
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

    // Delegación de clicks en la matriz
    seatsMatrix.addEventListener('click', function (e) {
        const btn = e.target.closest('.seat-button');
        if (!btn || btn.classList.contains('occupied')) return;
        toggleSeat(btn);
    });

    // Quitar desde el sidebar
    function bindRemoveButtons() {
        const removeBtns = document.querySelectorAll('.btn-remove-seat');
        removeBtns.forEach(function (b) {
            b.addEventListener('click', function () {
                const removeId = b.getAttribute('data-remove-id');
                const seatBtn = document.querySelector(`.seat-button[data-seat-id="${removeId}"]`);
                if (seatBtn) {
                    toggleSeat(seatBtn);
                }
            });
        });
    }

    bindRemoveButtons();

    // Cuenta regresiva visual del temporizador (10 minutos)
    let totalSeconds = 8 * 60 + 40;
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

