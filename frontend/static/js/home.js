/* Interactividad de la Cartelera de Películas (Sin AJAX/fetch) */
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('movieSearchInput');
    const genreChips = document.querySelectorAll('.genre-chip');
    const movieCards = document.querySelectorAll('.movie-card');

    let activeGenre = 'todos';
    let searchQuery = '';

    function updateFilter() {
        movieCards.forEach(function (card) {
            const title = card.getAttribute('data-title') || '';
            const genres = card.getAttribute('data-genres') || '';

            const matchesQuery = !searchQuery || title.includes(searchQuery);
            const matchesGenre = activeGenre === 'todos' || genres.includes(activeGenre);

            if (matchesQuery && matchesGenre) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        });
    }

    // Búsqueda en vivo por título en la cartelera
    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            searchQuery = e.target.value.toLowerCase().trim();
            updateFilter();
        });
    }

    // Filtrado por chip de género
    genreChips.forEach(function (chip) {
        chip.addEventListener('click', function () {
            genreChips.forEach(function (c) { c.classList.remove('active'); });
            chip.classList.add('active');
            activeGenre = chip.getAttribute('data-genre') || 'todos';
            updateFilter();
        });
    });
});

