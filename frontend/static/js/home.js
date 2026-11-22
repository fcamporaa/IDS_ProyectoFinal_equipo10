/* Búsqueda en vivo por título (sin AJAX/fetch).
   El filtro por género se resuelve en el servidor con ?id_genero=. */
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('movieSearchInput');
    const movieCards = document.querySelectorAll('.movie-card');

    if (!searchInput) return;

    searchInput.addEventListener('input', function (e) {
        const query = e.target.value.toLowerCase().trim();
        movieCards.forEach(function (card) {
            const title = card.getAttribute('data-title') || '';
            card.classList.toggle('hidden', Boolean(query) && !title.includes(query));
        });
    });
});
