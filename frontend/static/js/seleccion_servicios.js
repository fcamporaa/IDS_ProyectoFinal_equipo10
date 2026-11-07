/* Interactividad de Candy Bar y Servicios Adicionales */
document.addEventListener('DOMContentLoaded', function () {
    const candyListEl = document.getElementById('candySummaryItemsList');
    const candyCountBadgeEl = document.getElementById('candyItemsCountBadge');
    const displaySubtotalCandyEl = document.getElementById('displaySubtotalCandy');
    const displayTotalAcumuladoEl = document.getElementById('displayTotalAcumulado');

    if (!candyListEl) return;

    const subtotalEntradas = parseFloat(candyListEl.getAttribute('data-subtotal-entradas')) || 0;
    const productsMap = {};

    // Inicializar mapa de productos a partir de las tarjetas del DOM
    const cards = document.querySelectorAll('.service-card');
    cards.forEach(function (card) {
        const id = parseInt(card.getAttribute('data-service-id'), 10);
        const name = card.getAttribute('data-name') || '';
        const descEl = card.querySelector('.service-description');
        const desc = descEl ? descEl.textContent.trim() : '';
        const price = parseFloat(card.getAttribute('data-price')) || 0;
        const qtyEl = document.getElementById('qty-service-' + id);
        const qty = qtyEl ? parseInt(qtyEl.textContent, 10) || 0 : 0;

        productsMap[id] = {
            id: id,
            name: name,
            desc: desc,
            price: price,
            qty: qty
        };
    });

    function formatMoney(amount) {
        return '$' + amount.toLocaleString('es-AR');
    }

    function updateSummary() {
        let totalCandy = 0;
        let totalItems = 0;
        candyListEl.innerHTML = '';

        Object.values(productsMap).forEach(function (item) {
            if (item.qty > 0) {
                totalItems += item.qty;
                const itemSubtotal = item.price * item.qty;
                totalCandy += itemSubtotal;

                let shortName = item.name;
                if (shortName.length > 36) {
                    shortName = shortName.substring(0, 34) + '...';
                }

                const row = document.createElement('div');
                row.className = 'summary-item-row';
                row.innerHTML = `
                    <div class="summary-item-left">
                        <span class="summary-item-name">${item.qty}x ${shortName}</span>
                        <span class="summary-item-sub">${item.desc.substring(0, 30)}...</span>
                    </div>
                    <div class="summary-item-right">
                        <span class="summary-item-price text-gold">${formatMoney(itemSubtotal)}</span>
                    </div>
                `;
                candyListEl.appendChild(row);
            }
        });

        if (totalItems === 0) {
            const emptyRow = document.createElement('div');
            emptyRow.className = 'summary-empty-state';
            emptyRow.textContent = 'Sin combos ni extras seleccionados';
            candyListEl.appendChild(emptyRow);
        }

        if (candyCountBadgeEl) {
            candyCountBadgeEl.textContent = totalItems + (totalItems === 1 ? ' ITEM' : ' ITEMS');
        }
        if (displaySubtotalCandyEl) {
            displaySubtotalCandyEl.textContent = formatMoney(totalCandy);
        }
        if (displayTotalAcumuladoEl) {
            displayTotalAcumuladoEl.textContent = formatMoney(subtotalEntradas + totalCandy);
        }
    }

    // Delegación de eventos para selectores de cantidad (+ / -)
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.btn-qty-action');
        if (!btn) return;

        const action = btn.getAttribute('data-action');
        const targetId = parseInt(btn.getAttribute('data-target-id'), 10);
        const product = productsMap[targetId];

        if (!product) return;

        if (action === 'plus') {
            product.qty++;
        } else if (action === 'minus') {
            if (product.qty > 0) {
                product.qty--;
            }
        }

        // Actualizar número en la card
        const displayEl = document.getElementById('qty-service-' + targetId);
        if (displayEl) {
            displayEl.textContent = product.qty;
        }

        // Actualizar resumen lateral
        updateSummary();
    });

    // Filtrado por categorías de píldoras
    const filterPills = document.querySelectorAll('.filter-pill');
    const serviceCards = document.querySelectorAll('.service-card');

    filterPills.forEach(function (pill) {
        pill.addEventListener('click', function () {
            filterPills.forEach(function (p) { p.classList.remove('active'); });
            pill.classList.add('active');

            const filterCategory = pill.getAttribute('data-filter');

            serviceCards.forEach(function (card) {
                const cardCategories = (card.getAttribute('data-category') || '').toLowerCase();
                if (filterCategory === 'todos' || cardCategories.includes(filterCategory)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Cuenta regresiva visual del temporizador (8 min 40 seg)
    let candySeconds = 8 * 60 + 40;
    const candyCountdownEl = document.getElementById('candyCountdown');
    if (candyCountdownEl) {
        setInterval(function () {
            if (candySeconds > 0) {
                candySeconds--;
                const mins = String(Math.floor(candySeconds / 60)).padStart(2, '0');
                const secs = String(candySeconds % 60).padStart(2, '0');
                candyCountdownEl.textContent = `${mins}:${secs}`;
            }
        }, 1000);
    }
});

